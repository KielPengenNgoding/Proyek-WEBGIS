from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional

from app.core.database import get_db
from app.models.models_parkir import ZonaParkir
from app.schemas.schemas_parkir import (
    ZonaParkirCreate, ZonaParkirUpdate, ZonaParkirResponse,
    GeoJSONFeatureCollection, GeoJSONFeature, GeoJSONGeometry,
)

router = APIRouter(prefix="/api/zones", tags=["Zona Parkir"])


@router.get("/", response_model=List[ZonaParkirResponse])
async def get_all_zones(
    jenis_zona: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(ZonaParkir).order_by(ZonaParkir.kode_zona)
    if jenis_zona:
        q = q.where(ZonaParkir.jenis_zona == jenis_zona)
    result = await db.execute(q)
    zones = result.scalars().all()

    responses = []
    for z in zones:
        luas_row = await db.execute(
            text("SELECT ROUND((ST_Area(geom::geography) / 10000.0)::numeric, 4) FROM zona_parkir WHERE id_zona = :id"),
            {"id": z.id_zona},
        )
        luas_val = luas_row.scalar()
        responses.append(ZonaParkirResponse(
            id_zona=z.id_zona, kode_zona=z.kode_zona, nama_zona=z.nama_zona,
            jenis_zona=z.jenis_zona, deskripsi=z.deskripsi, tarif_zona=z.tarif_zona,
            luas_ha=float(luas_val) if luas_val else None,
        ))
    return responses


@router.get("/geojson", response_model=GeoJSONFeatureCollection,
            summary="[GEOJSON] Semua zona sebagai FeatureCollection")
async def get_zones_geojson(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(text("""
        SELECT id_zona, kode_zona, nama_zona, jenis_zona, tarif_zona,
               ROUND((ST_Area(geom::geography) / 10000.0)::numeric, 4) AS luas_ha,
               ST_AsGeoJSON(geom)::json AS geometry
        FROM zona_parkir ORDER BY kode_zona
    """))
    features = []
    for row in rows.mappings():
        features.append(GeoJSONFeature(
            geometry=GeoJSONGeometry(**row["geometry"]),
            properties={
                "id_zona":    row["id_zona"],
                "kode_zona":  row["kode_zona"],
                "nama_zona":  row["nama_zona"],
                "jenis_zona": row["jenis_zona"],
                "tarif_zona": float(row["tarif_zona"]) if row["tarif_zona"] else 0,
                "luas_ha":    float(row["luas_ha"]) if row["luas_ha"] else None,
            },
        ))
    return GeoJSONFeatureCollection(type="FeatureCollection", features=features, total=len(features))


@router.get("/{id_zona}", response_model=ZonaParkirResponse)
async def get_zone(id_zona: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ZonaParkir).where(ZonaParkir.id_zona == id_zona))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zona id={id_zona} tidak ditemukan")
    luas_row = await db.execute(
        text("SELECT ROUND((ST_Area(geom::geography) / 10000.0)::numeric, 4) FROM zona_parkir WHERE id_zona = :id"),
        {"id": id_zona},
    )
    luas_val = luas_row.scalar()
    return ZonaParkirResponse(
        id_zona=zone.id_zona, kode_zona=zone.kode_zona, nama_zona=zone.nama_zona,
        jenis_zona=zone.jenis_zona, deskripsi=zone.deskripsi, tarif_zona=zone.tarif_zona,
        luas_ha=float(luas_val) if luas_val else None,
    )


@router.get("/{id_zona}/parking", response_model=GeoJSONFeatureCollection,
            summary="[SPASIAL] Parkir di dalam zona — ST_Within")
async def get_parking_in_zone(id_zona: int, db: AsyncSession = Depends(get_db)):
    zone_check = await db.execute(select(ZonaParkir).where(ZonaParkir.id_zona == id_zona))
    if not zone_check.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Zona id={id_zona} tidak ditemukan")

    rows = await db.execute(text("""
        SELECT lp.id_lokasi, lp.kode_lokasi, lp.nama_lokasi, lp.kapasitas_total,
               lp.tarif_per_jam, lp.fee_berbayar, lp.beratap, lp.status, lp.id_zona,
               ST_X(lp.geom) AS longitude, ST_Y(lp.geom) AS latitude,
               ST_AsGeoJSON(lp.geom)::json AS geometry,
               STRING_AGG(jp.nama_jenis, ', ' ORDER BY jp.nama_jenis) AS jenis_kendaraan
        FROM lokasi_parkir lp
        JOIN zona_parkir zp ON ST_Within(lp.geom, zp.geom)
        LEFT JOIN lokasi_jenis lj ON lp.id_lokasi = lj.id_lokasi
        LEFT JOIN jenis_parkir jp ON lj.id_jenis = jp.id_jenis
        WHERE zp.id_zona = :id_zona
        GROUP BY lp.id_lokasi, lp.kode_lokasi, lp.nama_lokasi, lp.kapasitas_total,
                 lp.tarif_per_jam, lp.fee_berbayar, lp.beratap, lp.status, lp.id_zona, lp.geom
        ORDER BY lp.kode_lokasi
    """), {"id_zona": id_zona})

    features = _to_features(rows)
    return GeoJSONFeatureCollection(type="FeatureCollection", features=features, total=len(features))


@router.post("/", response_model=ZonaParkirResponse, status_code=status.HTTP_201_CREATED)
async def create_zone(payload: ZonaParkirCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(ZonaParkir).where(ZonaParkir.kode_zona == payload.kode_zona)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Kode zona '{payload.kode_zona}' sudah ada")
    try:
        result = await db.execute(text("""
            INSERT INTO zona_parkir (kode_zona, nama_zona, jenis_zona, deskripsi, tarif_zona, geom)
            VALUES (:kode, :nama, :jenis, :deskripsi, :tarif,
                    ST_SetSRID(ST_GeomFromText(:wkt), 4326))
            RETURNING id_zona, kode_zona, nama_zona, jenis_zona, deskripsi, tarif_zona,
                      ROUND((ST_Area(geom::geography) / 10000.0)::numeric, 4) AS luas_ha
        """), {
            "kode": payload.kode_zona, "nama": payload.nama_zona,
            "jenis": payload.jenis_zona, "deskripsi": payload.deskripsi,
            "tarif": float(payload.tarif_zona) if payload.tarif_zona else 0,
            "wkt": payload.geom_wkt,
        })
        row = result.mappings().one()
        return ZonaParkirResponse(**dict(row))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal membuat zona: {str(e)}")


@router.put("/{id_zona}", response_model=ZonaParkirResponse)
async def update_zone(
    id_zona: int, payload: ZonaParkirUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ZonaParkir).where(ZonaParkir.id_zona == id_zona))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zona id={id_zona} tidak ditemukan")
    updates = payload.model_dump(exclude_none=True)
    if "geom_wkt" in updates:
        wkt = updates.pop("geom_wkt")
        await db.execute(
            text("UPDATE zona_parkir SET geom = ST_SetSRID(ST_GeomFromText(:wkt), 4326) WHERE id_zona = :id"),
            {"wkt": wkt, "id": id_zona},
        )
    for field, value in updates.items():
        setattr(zone, field, value)
    await db.flush()
    luas_row = await db.execute(
        text("SELECT ROUND((ST_Area(geom::geography) / 10000.0)::numeric, 4) FROM zona_parkir WHERE id_zona = :id"),
        {"id": id_zona},
    )
    luas_val = luas_row.scalar()
    return ZonaParkirResponse(
        id_zona=zone.id_zona, kode_zona=zone.kode_zona, nama_zona=zone.nama_zona,
        jenis_zona=zone.jenis_zona, deskripsi=zone.deskripsi, tarif_zona=zone.tarif_zona,
        luas_ha=float(luas_val) if luas_val else None,
    )


@router.delete("/{id_zona}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_zone(id_zona: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ZonaParkir).where(ZonaParkir.id_zona == id_zona))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zona id={id_zona} tidak ditemukan")
    await db.delete(zone)


def _to_features(rows) -> List[GeoJSONFeature]:
    features = []
    for row in rows.mappings():
        features.append(GeoJSONFeature(
            geometry=GeoJSONGeometry(**row["geometry"]),
            properties={
                "id_lokasi":       row["id_lokasi"],
                "kode_lokasi":     row["kode_lokasi"],
                "nama_lokasi":     row["nama_lokasi"],
                "kapasitas_total": row["kapasitas_total"],
                "tarif_per_jam":   float(row["tarif_per_jam"]) if row["tarif_per_jam"] else 0,
                "fee_berbayar":    row["fee_berbayar"],
                "beratap":         row["beratap"],
                "status":          row["status"],
                "id_zona":         row["id_zona"],
                "longitude":       row["longitude"],
                "latitude":        row["latitude"],
                "jenis_kendaraan": row["jenis_kendaraan"],
            },
        ))
    return features