import os # Thêm import os để xử lý đường dẫn file
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from api import auth, services, orders, admin, upload, categories, search, banners,news
from fastapi.staticfiles import StaticFiles
# --- THÊM DÒNG NÀY ĐỂ XỬ LÝ DOWNLOAD ---
from fastapi.responses import FileResponse

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

# Phục vụ file tĩnh để XEM (Preview)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- ROUTE ÉP TẢI FILE (DOWNLOAD) ---
@app.get("/api/admin/download-artwork/{filename}", tags=["Upload"])
async def download_artwork(filename: str):
    # Trỏ đúng vào thư mục chứa file artwork của ông
    file_path = os.path.join("static", "uploads", filename)
    
    # Kiểm tra xem file có tồn tại không để tránh lỗi 500
    if not os.path.exists(file_path):
        return {"error": "File không tồn tại trên hệ thống!"}

    # FileResponse kèm tham số filename sẽ ép trình duyệt phải DOWNLOAD thay vì PREVIEW
    return FileResponse(
        path=file_path, 
        filename=filename, 
        media_type='application/octet-stream'
    )

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
app.include_router(news.router, prefix="/api/news", tags=["News"])