from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas

router = APIRouter()

# Lấy danh sách Banner
@router.get("/", response_model=List[schemas.Banner])
def get_banners(db: Session = Depends(get_db)):
    return db.query(models.Banner).order_by(models.Banner.sort_order.asc()).all()

# Thêm Banner mới
@router.post("/", response_model=schemas.Banner)
def create_banner(banner: schemas.BannerCreate, db: Session = Depends(get_db)):
    new_banner = models.Banner(**banner.model_dump()) 
    db.add(new_banner)
    db.commit()
    db.refresh(new_banner)
    return new_banner
# Cập nhật Banner (Sửa thông tin hoặc Bật/Tắt)
@router.put("/{banner_id}", response_model=schemas.Banner)
def update_banner(banner_id: int, banner_update: schemas.BannerCreate, db: Session = Depends(get_db)):
    # 1. Tìm xem cái banner có ID đó trong DB không
    db_banner = db.query(models.Banner).filter(models.Banner.id == banner_id).first()
    
    if not db_banner:
        raise HTTPException(status_code=404, detail="Không tìm thấy banner để cập nhật")
    
    # 2. Lấy dữ liệu mới từ Frontend gửi lên
    update_data = banner_update.model_dump(exclude_unset=True)
    
    # 3. Duyệt qua từng trường (title, image_url, position...) để cập nhật
    for key, value in update_data.items():
        setattr(db_banner, key, value)
    
    # 4. Lưu lại vào Database
    db.commit()
    db.refresh(db_banner)
    
    return db_banner
# Xóa Banner
@router.delete("/{banner_id}")
def delete_banner(banner_id: int, db: Session = Depends(get_db)):
    banner = db.query(models.Banner).filter(models.Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Không tìm thấy banner")
    db.delete(banner)
    db.commit()
    return {"message": "Xóa banner thành công"}