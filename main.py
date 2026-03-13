from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from api import auth, services, orders, admin,upload,categories, search, banners
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="In Nhanh TYD API", version="1.0.0")

# Create tables
Base.metadata.create_all(bind=engine)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
async def root():
    return {"message": "Welcome to In Nhanh TYD API"}


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(services.router, prefix="/api/services", tags=["Services"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin CMS"])
app.include_router(upload.router, prefix="/api/admin", tags=["Upload"])
app.include_router(categories.router, prefix="/api/admin", tags=["Categories"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(banners.router, prefix="/api/banners", tags=["Banners"])