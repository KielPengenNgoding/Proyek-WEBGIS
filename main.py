from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.routers import parking, zones, categories

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="REST API WebGIS Parkir Publik Kota Yogyakarta — SIG ITERA 2025/2026",
    openapi_tags=[
        {"name": "Lokasi Parkir",      "description": "CRUD + query spasial untuk titik parkir (Point)"},
        {"name": "Zona Parkir",        "description": "CRUD + GeoJSON untuk zona pelayanan (MultiPolygon)"},
        {"name": "Kategori Kendaraan", "description": "CRUD tabel master jenis kendaraan"},
        {"name": "Health",             "description": "Status sistem"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parking.router)
app.include_router(zones.router)
app.include_router(categories.router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    try:
        async with engine.connect() as conn:
            postgis_ver = (await conn.execute(text("SELECT PostGIS_Version()"))).scalar()
            total       = (await conn.execute(text("SELECT COUNT(*) FROM lokasi_parkir"))).scalar()
        return {
            "status": "healthy",
            "postgis_version": postgis_ver,
            "total_lokasi_parkir": total,
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "detail": str(e)},
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)