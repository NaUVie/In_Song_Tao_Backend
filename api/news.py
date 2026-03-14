from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from .auth import get_current_user 
from typing import List

router = APIRouter()

# 1. Lấy danh sách (Công khai)
@router.get("/", response_model=List[schemas.NewsShort])
def get_news(db: Session = Depends(get_db)):
    return db.query(models.News)\
             .filter(models.News.is_active == True)\
             .order_by(models.News.created_at.desc())\
             .all()

# 2. Lấy chi tiết (Công khai)
@router.get("/{slug}", response_model=schemas.News)
def get_news_detail(slug: str, db: Session = Depends(get_db)):
    db_news = db.query(models.News).filter(models.News.slug == slug).first()
    if not db_news:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết này!")
    return db_news

# 3. Admin tạo tin
@router.post("/", response_model=schemas.News)
def create_news(
    news_data: schemas.NewsCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Chỉ Admin mới có quyền!")

    db_news = models.News(**news_data.dict())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

# 4. Admin cập nhật tin (FIX LỖI 422 VÀ BẢO MẬT)
@router.put("/{news_id}", response_model=schemas.News)
def update_news(
    news_id: int, 
    news_data: schemas.NewsUpdate, # Dùng NewsUpdate để linh hoạt hơn
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Chỉ Admin mới có quyền sửa!")

    db_news = db.query(models.News).filter(models.News.id == news_id).first()
    if not db_news: 
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết")
    
    # Chỉ lấy những trường có gửi dữ liệu lên (loại bỏ trường None hoặc ID dư thừa)
    update_data = news_data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_news, key, value)
    
    db.commit()
    db.refresh(db_news)
    return db_news

# 5. Admin xóa tin (BẢO MẬT)
@router.delete("/{news_id}")
def delete_news(
    news_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Chỉ Admin mới có quyền xóa!")

    db_news = db.query(models.News).filter(models.News.id == news_id).first()
    if not db_news:
        raise HTTPException(status_code=404, detail="Không thấy bài này")

    db.delete(db_news)
    db.commit()
    return {"message": "Đã xóa bài viết thành công"}