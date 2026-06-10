from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any, Dict
from decimal import Decimal
from datetime import time


# ── JenisParkir ──────────────────────────────

class JenisParkirBase(BaseModel):
    kode_jenis:   str = Field(..., max_length=10)
    nama_jenis:   str = Field(..., max_length=50)
    deskripsi:    Optional[str] = None
    warna_marker: str = Field(default="#1976D2", pattern=r"^#[0-9A-Fa-f]{6}$")
    ikon_marker:  Optional[str] = None

class JenisParkirCreate(JenisParkirBase):
    pass

class JenisParkirUpdate(BaseModel):
    nama_jenis:   Optional[str] = Field(None, max_length=50)
    deskripsi:    Optional[str] = None
    warna_marker: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    ikon_marker:  Optional[str] = None

class JenisParkirResponse(JenisParkirBase):
    id_jenis: int
    model_config = {"from_attributes": True}


# ── ZonaParkir ───────────────────────────────

class ZonaParkirBase(BaseModel):
    kode_zona:  str = Field(..., max_length=20)
    nama_zona:  str = Field(..., max_length=100)
    jenis_zona: str
    deskripsi:  Optional[str] = None
    tarif_zona: Optional[Decimal] = Decimal("0")

    @field_validator("jenis_zona")
    @classmethod
    def validate_jenis_zona(cls, v: str) -> str:
        allowed = {"Wisata", "Komersial", "Transit", "Permukiman", "Pemerintahan"}
        if v not in allowed:
            raise ValueError(
                f"jenis_zona harus salah satu dari: {', '.join(sorted(allowed))}"
            )
        return v

class ZonaParkirCreate(ZonaParkirBase):
    geom_wkt: str = Field(..., description="WKT MULTIPOLYGON SRID 4326")

class ZonaParkirUpdate(BaseModel):
    nama_zona:  Optional[str] = None
    jenis_zona: Optional[str] = None
    deskripsi:  Optional[str] = None
    tarif_zona: Optional[Decimal] = None
    geom_wkt:   Optional[str] = None

class ZonaParkirResponse(ZonaParkirBase):
    id_zona: int
    luas_ha: Optional[float] = None
    model_config = {"from_attributes": True}


# ── LokasiParkir ─────────────────────────────

class LokasiParkirBase(BaseModel):
    nama_lokasi:       str = Field(..., max_length=150)
    alamat:            Optional[str] = None
    kapasitas_total:   Optional[int] = Field(None, ge=0)
    tarif_per_jam:     Optional[Decimal] = Decimal("0")
    operator:          Optional[str] = None
    operator_tipe:     Optional[str] = None
    jam_buka:          Optional[time] = None
    jam_tutup:         Optional[time] = None
    fee_berbayar:      Optional[bool] = None
    beratap:           Optional[bool] = None
    penerangan:        Optional[bool] = None
    akses_disabilitas: Optional[bool] = None
    permukaan:         Optional[str] = None
    tipe_parkir:       Optional[str] = None
    status:            str = Field(default="aktif", pattern=r"^(aktif|nonaktif|renovasi)$")
    osm_id:            Optional[str] = None
    id_zona:           Optional[int] = None

class LokasiParkirCreate(LokasiParkirBase):
    longitude: float = Field(..., ge=110.0, le=111.0)
    latitude:  float = Field(..., ge=-8.1,  le=-7.5)

class LokasiParkirUpdate(BaseModel):
    nama_lokasi:       Optional[str] = None
    alamat:            Optional[str] = None
    kapasitas_total:   Optional[int] = Field(None, ge=0)
    tarif_per_jam:     Optional[Decimal] = None
    operator:          Optional[str] = None
    operator_tipe:     Optional[str] = None
    jam_buka:          Optional[time] = None
    jam_tutup:         Optional[time] = None
    fee_berbayar:      Optional[bool] = None
    beratap:           Optional[bool] = None
    penerangan:        Optional[bool] = None
    akses_disabilitas: Optional[bool] = None
    permukaan:         Optional[str] = None
    tipe_parkir:       Optional[str] = None
    status:            Optional[str] = Field(None, pattern=r"^(aktif|nonaktif|renovasi)$")
    longitude:         Optional[float] = None
    latitude:          Optional[float] = None
    id_zona:           Optional[int] = None

class LokasiParkirResponse(LokasiParkirBase):
    id_lokasi:       int
    kode_lokasi:     str
    longitude:       Optional[float] = None
    latitude:        Optional[float] = None
    nama_zona:       Optional[str] = None
    jenis_kendaraan: Optional[List[str]] = None
    model_config = {"from_attributes": True}


# ── GeoJSON ──────────────────────────────────

class GeoJSONGeometry(BaseModel):
    type: str
    coordinates: Any

class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONGeometry
    properties: Dict[str, Any]

class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]
    total: int = 0


# ── LokasiJenis ──────────────────────────────

class LokasiJenisCreate(BaseModel):
    id_jenis:     int
    kapasitas:    Optional[int] = Field(None, ge=0)
    tarif_khusus: Optional[Decimal] = None
    catatan:      Optional[str] = None

class LokasiJenisResponse(BaseModel):
    id_lokasi_jenis: int
    id_lokasi:       int
    id_jenis:        int
    kode_jenis:      Optional[str] = None
    nama_jenis:      Optional[str] = None
    kapasitas:       Optional[int] = None
    tarif_khusus:    Optional[Decimal] = None
    catatan:         Optional[str] = None
    model_config = {"from_attributes": True}