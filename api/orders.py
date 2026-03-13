from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload 
import models
import schemas
from database import get_db
from .auth import get_current_user
from typing import List
import logic

router = APIRouter()

@router.post("/", response_model=schemas.Order)
def create_order(
    order: schemas.OrderCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Tạo đơn hàng gốc
    db_order = models.Order(user_id=current_user.id, total_price=0, status="pending")
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    total_order_price = 0
    
    # 2. Xử lý từng món trong giỏ hàng
    for item in order.items:
        item_price = logic.calculate_item_price(db, item)
        
        db_item = models.OrderItem(
            order_id=db_order.id,
            service_id=item.service_id,
            quantity=item.quantity,
            selected_options=item.selected_options,
            item_price=item_price,
            artwork_url=item.artwork_url
        )
        db.add(db_item)
        total_order_price += item_price
        
    db_order.total_price = total_order_price * 1.08 
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/my", response_model=List[schemas.Order])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Order)\
             .options(
                 joinedload(models.Order.items).joinedload(models.OrderItem.service)
             )\
             .filter(models.Order.user_id == current_user.id)\
             .order_by(models.Order.id.desc())\
             .all()
             
@router.get("/all", response_model=List[schemas.Order])
def get_all_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Ông không có quyền Admin!")

    return db.query(models.Order)\
             .options(
                
                 joinedload(models.Order.items).joinedload(models.OrderItem.service),
                 joinedload(models.Order.user) 
             )\
             .order_by(models.Order.id.desc())\
             .all()

@router.patch("/{order_id}/status", response_model=schemas.Order)
def update_order_status(
    order_id: int,
    status_data: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403)

    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Không thấy đơn này")

    # Cập nhật trạng thái mới (pending, printing, shipped, completed, cancelled)
    db_order.status = status_data.status
    db.commit()
    db.refresh(db_order)
    return db_order