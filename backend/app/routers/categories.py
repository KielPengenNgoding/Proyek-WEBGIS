from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models.models_parkir import JenisParkir
from app.schemas.schemas_parkir import (
    JenisParkirCreate, JenisParkirUpdate, JenisParkirResponse
)

router = APIRouter(prefix="/api/categories", tags=["Kategori Kendaraan"])


@router.get("/", response_model=List[JenisParkirResponse])
async def get_all_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JenisParkir).order_by(JenisParkir.id_jenis))
    return result.scalars().all()


@router.get("/{id_jenis}", response_model=JenisParkirResponse)
async def get_category(id_jenis: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(JenisParkir).where(JenisParkir.id_jenis == id_jenis)
    )
    jenis = result.scalar_one_or_none()
    if not jenis:
        raise HTTPException(status_code=404, detail=f"Kategori id={id_jenis} tidak ditemukan")
    return jenis


@router.post("/", response_model=JenisParkirResponse, status_code=status.HTTP_201_CREATED)
async def create_category(payload: JenisParkirCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(JenisParkir).where(JenisParkir.kode_jenis == payload.kode_jenis)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Kode '{payload.kode_jenis}' sudah ada")
    jenis = JenisParkir(**payload.model_dump())
    db.add(jenis)
    await db.flush()
    await db.refresh(jenis)
    return jenis


@router.put("/{id_jenis}", response_model=JenisParkirResponse)
async def update_category(
    id_jenis: int, payload: JenisParkirUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(JenisParkir).where(JenisParkir.id_jenis == id_jenis)
    )
    jenis = result.scalar_one_or_none()
    if not jenis:
        raise HTTPException(status_code=404, detail=f"Kategori id={id_jenis} tidak ditemukan")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(jenis, field, value)
    await db.flush()
    await db.refresh(jenis)
    return jenis


@router.delete("/{id_jenis}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(id_jenis: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(JenisParkir).where(JenisParkir.id_jenis == id_jenis)
    )
    jenis = result.scalar_one_or_none()
    if not jenis:
        raise HTTPException(status_code=404, detail=f"Kategori id={id_jenis} tidak ditemukan")
    await db.delete(jenis)