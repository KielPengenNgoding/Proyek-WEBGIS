from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean,
    Time, TIMESTAMP, ForeignKey, UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.core.database import Base


class JenisParkir(Base):
    __tablename__ = "jenis_parkir"

    id_jenis      = Column(Integer, primary_key=True, autoincrement=True)
    kode_jenis    = Column(String(10), nullable=False, unique=True)
    nama_jenis    = Column(String(50), nullable=False)
    deskripsi     = Column(Text, nullable=True)
    warna_marker  = Column(String(7), nullable=False, default="#1976D2")
    ikon_marker   = Column(String(50), nullable=True)

    lokasi_jenis = relationship(
        "LokasiJenis", back_populates="jenis", cascade="all, delete-orphan"
    )


class ZonaParkir(Base):
    __tablename__ = "zona_parkir"

    id_zona    = Column(Integer, primary_key=True, autoincrement=True)
    kode_zona  = Column(String(20), nullable=False, unique=True)
    nama_zona  = Column(String(100), nullable=False)
    jenis_zona = Column(String(50), nullable=False)
    deskripsi  = Column(Text, nullable=True)
    tarif_zona = Column(Numeric(10, 2), nullable=True, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    geom       = Column(Geometry("MULTIPOLYGON", srid=4326), nullable=False)

    lokasi_parkir = relationship("LokasiParkir", back_populates="zona")


class LokasiParkir(Base):
    __tablename__ = "lokasi_parkir"

    id_lokasi         = Column(Integer, primary_key=True, autoincrement=True)
    kode_lokasi       = Column(String(20), nullable=False, unique=True)
    nama_lokasi       = Column(String(150), nullable=False)
    alamat            = Column(Text, nullable=True)
    kapasitas_total   = Column(Integer, nullable=True)
    tarif_per_jam     = Column(Numeric(10, 2), nullable=True, default=0)
    operator          = Column(String(150), nullable=True)
    operator_tipe     = Column(String(50), nullable=True)
    jam_buka          = Column(Time, nullable=True)
    jam_tutup         = Column(Time, nullable=True)
    fee_berbayar      = Column(Boolean, nullable=True)
    beratap           = Column(Boolean, nullable=True)
    penerangan        = Column(Boolean, nullable=True)
    akses_disabilitas = Column(Boolean, nullable=True)
    permukaan         = Column(String(50), nullable=True)
    tipe_parkir       = Column(String(50), nullable=True)
    status            = Column(String(20), nullable=False, default="aktif")
    osm_id            = Column(String(50), nullable=True)
    id_zona           = Column(
        Integer, ForeignKey("zona_parkir.id_zona", ondelete="SET NULL"), nullable=True
    )
    created_at        = Column(TIMESTAMP(timezone=True), server_default=func.now())
    geom              = Column(Geometry("POINT", srid=4326), nullable=False)

    zona         = relationship("ZonaParkir", back_populates="lokasi_parkir")
    lokasi_jenis = relationship(
        "LokasiJenis", back_populates="lokasi", cascade="all, delete-orphan"
    )


class LokasiJenis(Base):
    __tablename__ = "lokasi_jenis"

    id_lokasi_jenis = Column(Integer, primary_key=True, autoincrement=True)
    id_lokasi       = Column(
        Integer, ForeignKey("lokasi_parkir.id_lokasi", ondelete="CASCADE"), nullable=False
    )
    id_jenis        = Column(
        Integer, ForeignKey("jenis_parkir.id_jenis", ondelete="RESTRICT"), nullable=False
    )
    kapasitas       = Column(Integer, nullable=True)
    tarif_khusus    = Column(Numeric(10, 2), nullable=True)
    catatan         = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("id_lokasi", "id_jenis", name="uq_lokasi_jenis"),
    )

    lokasi = relationship("LokasiParkir", back_populates="lokasi_jenis")
    jenis  = relationship("JenisParkir", back_populates="lokasi_jenis")