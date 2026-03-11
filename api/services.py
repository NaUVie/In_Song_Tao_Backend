from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, with_loader_criteria
import models
import schemas
from database import get_db
from typing import List
import logic  # Nhớ tạo file logic.py em đưa ở trên nhé sếp

router = APIRouter()

# --- 1. LẤY DANH MỤC (Chỉ hiện sản phẩm chưa xóa) ---
@router.get("/categories", response_model=List[schemas.Category])
def get_categories(db: Session = Depends(get_db)):
    # with_loader_criteria phải nằm trong options() mới đúng cú pháp
    return db.query(models.Category).options(
        joinedload(models.Category.services),
        with_loader_criteria(models.Service, models.Service.is_deleted == False)
    ).all()

# --- 2. LẤY CHI TIẾT DỊCH VỤ (Để khách đặt hàng) ---
@router.get("/{slug}", response_model=schemas.Service)
def get_service(slug: str, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(
        models.Service.slug == slug,
        models.Service.is_deleted == False # Chặn khách vào link sản phẩm đã xóa
    ).options(
        joinedload(models.Service.price_rules),
        joinedload(models.Service.option_groups).joinedload(models.ServiceOptionGroup.options)
    ).first()

    if not service:
        raise HTTPException(status_code=404, detail="Dịch vụ không tồn tại hoặc đã ngừng kinh doanh")
    return service

# --- 3. TÍNH GIÁ DỰA TRÊN SỐ LƯỢNG & OPTION ---
@router.post("/calculate-price")
def calculate_price(item: schemas.OrderItemCreate, db: Session = Depends(get_db)):
    try:
        # Kiểm tra sản phẩm có bị 'ngừng kinh doanh' không trước khi tính tiền
        db_service = db.query(models.Service).filter(
            models.Service.id == item.service_id,
            models.Service.is_deleted == False
        ).first()

        if not db_service:
            raise HTTPException(status_code=400, detail="Sản phẩm này hiện không còn hỗ trợ đặt hàng")

        total = logic.calculate_item_price(db, item)
        return {"total_price": total}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))