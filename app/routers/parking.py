from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional

from app.core.database import get_db
from app.models.models_parkir import LokasiParkir
from app.schemas.schemas_parkir import (
    LokasiParkirCreate, LokasiParkirUpdate, LokasiParkirResponse,
    LokasiJenisCreate, LokasiJenisResponse,
    GeoJSONFeatureCollection, GeoJSONFeature, GeoJSONGeometry,
)

router = APIRouter(prefix="/api/parking", tags=["Lokasi Parkir"])

_BASE_SQL = """
    SELECT
        lp.id_lokasi, lp.kode_lokasi, lp.nama_lokasi, lp.alamat,
        lp.kapasitas_total, lp.tarif_per_jam, lp.operator, lp.operator_tipe,
        lp.jam_buka, lp.jam_tutup, lp.fee_berbayar, lp.beratap,
        lp.penerangan, lp.akses_disabilitas, lp.permukaan, lp.tipe_parkir,
        lp.status, lp.osm_id, lp.id_zona, zp.nama_zona,
        ST_X(lp.geom) AS longitude, ST_Y(lp.geom) AS latitude,
        ST_AsGeoJSON(lp.geom)::json AS geometry,
        STRING_AGG(jp.nama_jenis, ', ' ORDER BY jp.nama_jenis) AS jenis_kendaraan
    FROM lokasi_parkir lp
    LEFT JOIN zona_parkir zp ON lp.id_zona = zp.id_zona
    LEFT JOIN lokasi_jenis lj ON lp.id_lokasi = lj.id_lokasi
    LEFT JOIN jenis_parkir jp ON lj.id_jenis = jp.id_jenis
"""

_GROUP_BY = """
    GROUP BY lp.id_lokasi, lp.kode_lokasi, lp.nama_lokasi, lp.alamat,
             lp.kapasitas_total, lp.tarif_per_jam, lp.operator, lp.operator_tipe,
             lp.jam_buka, lp.jam_tutup, lp.fee_berbayar, lp.beratap,
             lp.penerangan, lp.akses_disabilitas, lp.permukaan, lp.tipe_parkir,
             lp.status, lp.osm_id, lp.id_zona, zp.nama_zona, lp.geom
"""


@router.get("/", response_model=GeoJSONFeatureCollection,
            summary="Semua lokasi parkir sebagai FeatureCollection GeoJSON")
async def get_all_parking(
    status: Optional[str] = Query(default="aktif"),
    jenis_kendaraan: Optional[str] = Query(None),
    fee_berbayar: Optional[bool] = Query(None),
    beratap: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    where, params = [], {}
    if status:
        where.append("lp.status = :status"); params["status"] = status
    if fee_berbayar is not None:
        where.append("lp.fee_berbayar = :fee"); params["fee"] = fee_berbayar
    if beratap is not None:
        where.append("lp.beratap = :beratap"); params["beratap"] = beratap
    if jenis_kendaraan:
        # FIX #5: gunakan nama_jenis case-insensitive, bukan kode_jenis
        where.append("LOWER(jp.nama_jenis) = LOWER(:nama_jenis)")
        params["nama_jenis"] = jenis_kendaraan

    where_sql = "WHERE " + " AND ".join(where) if where else ""
    sql = f"{_BASE_SQL} {where_sql} {_GROUP_BY} ORDER BY lp.kode_lokasi"
    rows = await db.execute(text(sql), params)
    features = _to_features(rows)
    return GeoJSONFeatureCollection(type="FeatureCollection", features=features, total=len(features))


@router.get("/radius", response_model=GeoJSONFeatureCollection,
            summary="[SPASIAL] Parkir dalam radius — ST_DWithin ::geography")
async def get_parking_by_radius(
    longitude: float = Query(..., ge=110.0, le=111.0),
    latitude:  float = Query(..., ge=-8.1,  le=-7.5),
    radius_m:  float = Query(default=500.0, ge=50.0, le=10000.0),
    jenis_kendaraan: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    # FIX #5: gunakan nama_jenis case-insensitive, bukan kode_jenis
    jenis_filter = "AND LOWER(jp.nama_jenis) = LOWER(:nama_jenis)" if jenis_kendaraan else ""
    params = {"lon": longitude, "lat": latitude, "radius": radius_m}
    if jenis_kendaraan:
        params["nama_jenis"] = jenis_kendaraan

    sql = f"""
        SELECT
            lp.id_lokasi, lp.kode_lokasi, lp.nama_lokasi, lp.kapasitas_total,
            lp.tarif_per_jam, lp.fee_berbayar, lp.beratap, lp.status, lp.id_zona,
            zp.nama_zona,
            ST_X(lp.geom) AS longitude, ST_Y(lp.geom) AS latitude,
            ST_AsGeoJSON(lp.geom)::json AS geometry,
            STRING_AGG(jp.nama_jenis, ', ' ORDER BY jp.nama_jenis) AS jenis_kendaraan,
            ROUND(ST_Distance(
                lp.geom::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
            )::numeric, 1) AS jarak_m
        FROM lokasi_parkir lp
        LEFT JOIN zona_parkir zp ON lp.id_zona = zp.id_zona
        LEFT JOIN lokasi_jenis lj ON lp.id_lokasi = lj.id_lokasi
        LEFT JOIN jenis_parkir jp ON lj.id_jenis = jp.id_jenis
        WHERE ST_DWithin(
            lp.geom::geography,
            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
            :radius
        )
        AND lp.status = 'aktif'
        {jenis_filter}
        GROUP BY lp.id_lokasi, lp.kode_lokasi, lp.nama_lokasi, lp.kapasitas_total,
                 lp.tarif_per_jam, lp.fee_berbayar, lp.beratap, lp.status, lp.id_zona,
                 zp.nama_zona, lp.geom
        ORDER BY jarak_m ASC
    """
    rows = await db.execute(text(sql), params)
    features = []
    for row in rows.mappings():
        features.append(GeoJSONFeature(
            geometry=GeoJSONGeometry(**row["geometry"]),
            properties={
                **_base_props(row),
                # FIX #1: is not None agar jarak 0.0 tidak jadi None
                "jarak_m": float(row["jarak_m"]) if row["jarak_m"] is not None else None,
            },
        ))
    return GeoJSONFeatureCollection(type="FeatureCollection", features=features, total=len(features))


@router.get("/nearest", response_model=GeoJSONFeatureCollection,
            summary="[SPASIAL] N parkir terdekat — operator <-> KNN + GIST index")
async def get_nearest_parking(
    longitude: float = Query(..., ge=110.0, le=111.0),
    latitude:  float = Query(..., ge=-8.1,  le=-7.5),
    n:         int   = Query(default=5, ge=1, le=20),
    jenis_kendaraan: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    # FIX #5: gunakan nama_jenis case-insensitive, bukan kode_jenis
    jenis_filter = "AND LOWER(jp.nama_jenis) = LOWER(:nama_jenis)" if jenis_kendaraan else ""
    params = {"lon": longitude, "lat": latitude, "n": n}
    if jenis_kendaraan:
        params["nama_jenis"] = jenis_kendaraan

    sql = f"""
        SELECT
            lp.id_lokasi, lp.kode_lokasi, lp.nama_lokasi, lp.kapasitas_total,
            lp.tarif_per_jam, lp.fee_berbayar, lp.beratap, lp.status, lp.id_zona,
            zp.nama_zona,
            ST_X(lp.geom) AS longitude, ST_Y(lp.geom) AS latitude,
            ST_AsGeoJSON(lp.geom)::json AS geometry,
            STRING_AGG(jp.nama_jenis, ', ' ORDER BY jp.nama_jenis) AS jenis_kendaraan,
            ROUND(ST_Distance(
                lp.geom::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
            )::numeric, 1) AS jarak_m
        FROM lokasi_parkir lp
        LEFT JOIN zona_parkir zp ON lp.id_zona = zp.id_zona
        LEFT JOIN lokasi_jenis lj ON lp.id_lokasi = lj.id_lokasi
        LEFT JOIN jenis_parkir jp ON lj.id_jenis = jp.id_jenis
        WHERE lp.status = 'aktif'
        {jenis_filter}
        GROUP BY lp.id_lokasi, lp.kode_lokasi, lp.nama_lokasi, lp.kapasitas_total,
                 lp.tarif_per_jam, lp.fee_berbayar, lp.beratap, lp.status, lp.id_zona,
                 zp.nama_zona, lp.geom
        ORDER BY lp.geom <-> ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
        LIMIT :n
    """
    rows = await db.execute(text(sql), params)
    features = []
    for row in rows.mappings():
        features.append(GeoJSONFeature(
            geometry=GeoJSONGeometry(**row["geometry"]),
            properties={
                **_base_props(row),
                # FIX #1: is not None agar jarak 0.0 tidak jadi None
                "jarak_m": float(row["jarak_m"]) if row["jarak_m"] is not None else None,
            },
        ))
    return GeoJSONFeatureCollection(type="FeatureCollection", features=features, total=len(features))


@router.get("/{id_lokasi}", response_model=LokasiParkirResponse)
async def get_parking_detail(id_lokasi: int, db: AsyncSession = Depends(get_db)):
    sql = f"{_BASE_SQL} WHERE lp.id_lokasi = :id {_GROUP_BY}"
    result = await db.execute(text(sql), {"id": id_lokasi})
    row = result.mappings().one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail=f"Lokasi id={id_lokasi} tidak ditemukan")
    return LokasiParkirResponse(
        id_lokasi=row["id_lokasi"], kode_lokasi=row["kode_lokasi"],
        nama_lokasi=row["nama_lokasi"], alamat=row["alamat"],
        kapasitas_total=row["kapasitas_total"], tarif_per_jam=row["tarif_per_jam"],
        operator=row["operator"], operator_tipe=row["operator_tipe"],
        jam_buka=row["jam_buka"], jam_tutup=row["jam_tutup"],
        fee_berbayar=row["fee_berbayar"], beratap=row["beratap"],
        penerangan=row["penerangan"], akses_disabilitas=row["akses_disabilitas"],
        permukaan=row["permukaan"], tipe_parkir=row["tipe_parkir"],
        status=row["status"], osm_id=row["osm_id"], id_zona=row["id_zona"],
        longitude=row["longitude"], latitude=row["latitude"],
        nama_zona=row["nama_zona"],
        jenis_kendaraan=(row["jenis_kendaraan"].split(", ") if row["jenis_kendaraan"] else []),
    )


@router.post("/", response_model=LokasiParkirResponse, status_code=status.HTTP_201_CREATED)
async def create_parking(payload: LokasiParkirCreate, db: AsyncSession = Depends(get_db)):
    # FIX #3: MAX(id_lokasi) hindari collision kode setelah DELETE
    count_row = await db.execute(text("SELECT COALESCE(MAX(id_lokasi), 0) FROM lokasi_parkir"))
    kode_lokasi = f"PKR-{count_row.scalar() + 1:03d}"

    id_zona = payload.id_zona
    if not id_zona:
        zona_row = await db.execute(text("""
            SELECT id_zona FROM zona_parkir
            WHERE ST_Within(ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), geom)
            LIMIT 1
        """), {"lon": payload.longitude, "lat": payload.latitude})
        z = zona_row.one_or_none()
        if z:
            id_zona = z[0]

    try:
        result = await db.execute(text("""
            INSERT INTO lokasi_parkir (
                kode_lokasi, nama_lokasi, alamat, kapasitas_total, tarif_per_jam,
                operator, operator_tipe, jam_buka, jam_tutup,
                fee_berbayar, beratap, penerangan, akses_disabilitas,
                permukaan, tipe_parkir, status, osm_id, id_zona, geom
            ) VALUES (
                :kode, :nama, :alamat, :kapasitas, :tarif,
                :operator, :op_tipe, :jam_buka, :jam_tutup,
                :fee, :beratap, :penerangan, :disabilitas,
                :permukaan, :tipe_parkir, :status, :osm_id, :id_zona,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
            )
            RETURNING id_lokasi
        """), {
            "kode": kode_lokasi, "nama": payload.nama_lokasi, "alamat": payload.alamat,
            "kapasitas": payload.kapasitas_total,
            "tarif": float(payload.tarif_per_jam) if payload.tarif_per_jam else 0,
            "operator": payload.operator, "op_tipe": payload.operator_tipe,
            "jam_buka": payload.jam_buka if payload.jam_buka else None,
            "jam_tutup": payload.jam_tutup if payload.jam_tutup else None,
            "fee": payload.fee_berbayar, "beratap": payload.beratap,
            "penerangan": payload.penerangan, "disabilitas": payload.akses_disabilitas,
            "permukaan": payload.permukaan, "tipe_parkir": payload.tipe_parkir,
            "status": payload.status, "osm_id": payload.osm_id,
            "id_zona": id_zona, "lon": payload.longitude, "lat": payload.latitude,
        })
        new_id = result.scalar()
        await db.commit()  # FIX #4: commit wajib setelah INSERT
        return await get_parking_detail(new_id, db)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Gagal membuat lokasi: {str(e)}")


@router.put("/{id_lokasi}", response_model=LokasiParkirResponse)
async def update_parking(
    id_lokasi: int, payload: LokasiParkirUpdate, db: AsyncSession = Depends(get_db)
):
    check = await db.execute(select(LokasiParkir).where(LokasiParkir.id_lokasi == id_lokasi))
    # FIX #2: simpan hasil scalar_one_or_none() sekali saja
    lokasi = check.scalar_one_or_none()
    if not lokasi:
        raise HTTPException(status_code=404, detail=f"Lokasi id={id_lokasi} tidak ditemukan")
    updates = payload.model_dump(exclude_none=True)
    lon = updates.pop("longitude", None)
    lat = updates.pop("latitude", None)
    if lon and lat:
        await db.execute(
            text("UPDATE lokasi_parkir SET geom = ST_SetSRID(ST_MakePoint(:lon, :lat), 4326) WHERE id_lokasi = :id"),
            {"lon": lon, "lat": lat, "id": id_lokasi},
        )
    for field, value in updates.items():
        setattr(lokasi, field, value)
    await db.flush()
    await db.commit()  # FIX #4: commit wajib setelah UPDATE
    return await get_parking_detail(id_lokasi, db)


@router.delete("/{id_lokasi}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_parking(id_lokasi: int, db: AsyncSession = Depends(get_db)):
    check = await db.execute(select(LokasiParkir).where(LokasiParkir.id_lokasi == id_lokasi))
    lokasi = check.scalar_one_or_none()
    if not lokasi:
        raise HTTPException(status_code=404, detail=f"Lokasi id={id_lokasi} tidak ditemukan")
    await db.delete(lokasi)
    await db.commit()  # FIX #4: commit wajib setelah DELETE


@router.get("/{id_lokasi}/jenis", response_model=List[LokasiJenisResponse])
async def get_parking_jenis(id_lokasi: int, db: AsyncSession = Depends(get_db)):
    rows = await db.execute(text("""
        SELECT lj.*, jp.kode_jenis, jp.nama_jenis
        FROM lokasi_jenis lj
        JOIN jenis_parkir jp ON lj.id_jenis = jp.id_jenis
        WHERE lj.id_lokasi = :id ORDER BY jp.kode_jenis
    """), {"id": id_lokasi})
    return [LokasiJenisResponse(**dict(r)) for r in rows.mappings()]


@router.post("/{id_lokasi}/jenis", response_model=LokasiJenisResponse,
             status_code=status.HTTP_201_CREATED)
async def add_parking_jenis(
    id_lokasi: int, payload: LokasiJenisCreate, db: AsyncSession = Depends(get_db)
):
    check = await db.execute(select(LokasiParkir).where(LokasiParkir.id_lokasi == id_lokasi))
    if not check.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Lokasi id={id_lokasi} tidak ditemukan")
    try:
        result = await db.execute(text("""
            INSERT INTO lokasi_jenis (id_lokasi, id_jenis, kapasitas, tarif_khusus, catatan)
            VALUES (:id_lokasi, :id_jenis, :kapasitas, :tarif, :catatan)
            RETURNING id_lokasi_jenis, id_lokasi, id_jenis, kapasitas, tarif_khusus, catatan
        """), {
            "id_lokasi": id_lokasi, "id_jenis": payload.id_jenis,
            "kapasitas": payload.kapasitas,
            "tarif": float(payload.tarif_khusus) if payload.tarif_khusus else None,
            "catatan": payload.catatan,
        })
        row = result.mappings().one()
        jenis_row = await db.execute(
            text("SELECT kode_jenis, nama_jenis FROM jenis_parkir WHERE id_jenis = :id"),
            {"id": payload.id_jenis},
        )
        jenis = jenis_row.one_or_none()
        await db.commit()  # FIX #4: commit setelah INSERT jenis
        return LokasiJenisResponse(
            **dict(row),
            kode_jenis=jenis[0] if jenis else None,
            nama_jenis=jenis[1] if jenis else None,
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Gagal menambah jenis: {str(e)}")


@router.delete("/{id_lokasi}/jenis/{id_jenis}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_parking_jenis(
    id_lokasi: int, id_jenis: int, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        text("DELETE FROM lokasi_jenis WHERE id_lokasi = :il AND id_jenis = :ij RETURNING id_lokasi_jenis"),
        {"il": id_lokasi, "ij": id_jenis},
    )
    if not result.one_or_none():
        raise HTTPException(status_code=404, detail="Kombinasi lokasi-jenis tidak ditemukan")
    await db.commit()  # FIX #4: commit setelah DELETE jenis


def _base_props(row) -> dict:
    return {
        "id_lokasi":       row["id_lokasi"],
        "kode_lokasi":     row["kode_lokasi"],
        "nama_lokasi":     row["nama_lokasi"],
        "kapasitas_total": row["kapasitas_total"],
        "tarif_per_jam":   float(row["tarif_per_jam"]) if row["tarif_per_jam"] else 0,
        "fee_berbayar":    row["fee_berbayar"],
        "beratap":         row["beratap"],
        "status":          row["status"],
        "id_zona":         row["id_zona"],
        "nama_zona":       row["nama_zona"],
        "longitude":       row["longitude"],
        "latitude":        row["latitude"],
        "jenis_kendaraan": row["jenis_kendaraan"],
    }


def _to_features(rows) -> List[GeoJSONFeature]:
    return [
        GeoJSONFeature(
            geometry=GeoJSONGeometry(**row["geometry"]),
            properties=_base_props(row),
        )
        for row in rows.mappings()
    ]