import os
import shutil
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import models
from .auth import get_current_user

router = APIRouter()

# Đảm bảo thư mục tồn tại khi chạy code
UPLOAD_DIR = "static/uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


def check_admin(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="không có quyền up ảnh!")
    return current_user

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    admin: models.User = Depends(check_admin)
):
    # 1. Kiểm tra định dạng (Chỉ nhận ảnh)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File này không phải ảnh!")

    # 2. Tạo tên file duy nhất (UUID) để không bị trùng
    ext = file.filename.split(".")[-1]
    filename = f"{uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # 3. Lưu file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lưu file: {str(e)}")

    # 4. Trả về đường dẫn tương đối để lưu vào DB
    return {"image_url": f"/static/uploads/{filename}"}