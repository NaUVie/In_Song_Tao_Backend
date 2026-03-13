from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from .auth import get_current_user

router = APIRouter()

# 1. Lấy danh sách danh mục
@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

# 2. Thêm danh mục mới (Chỉ Admin)
@router.post("/categories")
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin: 
        raise HTTPException(status_code=403, detail=" không có quyền thực thi!")
    
    db_cat = models.Category(
        name=category.name,
        slug=category.slug,
        image_url=category.image_url
    )
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

# 3. Sửa danh mục
@router.put("/categories/{cat_id}")
def update_category(cat_id: int, category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin: raise HTTPException(status_code=403)
        
    db_cat = db.query(models.Category).filter(models.Category.id == cat_id).first()
    if not db_cat: raise HTTPException(status_code=404, detail="Không thấy danh mục!")

    db_cat.name = category.name
    db_cat.slug = category.slug
    db_cat.image_url = category.image_url
        
    db.commit()
    db.refresh(db_cat)
    return db_cat

# 4. Xóa danh mục
@router.delete("/categories/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin: raise HTTPException(status_code=403)
        
    db_cat = db.query(models.Category).filter(models.Category.id == cat_id).first()
    if db_cat:
        db.delete(db_cat)
        db.commit()
    return {"message": "Xóa thành công"}