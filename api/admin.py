from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import models
import schemas
from database import get_db
from .auth import get_current_user

router = APIRouter()

# 👮‍♂️ Kiểm tra quyền Admin
def check_admin(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges"
        )
    return current_user

# --- QUẢN LÝ DỊCH VỤ (SERVICE MANAGEMENT) ---
# --- QUẢN LÝ DỊCH VỤ (SERVICE MANAGEMENT) ---

@router.get("/services", response_model=List[schemas.Service])
def get_admin_services(
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    # Load thêm price_rules để Frontend hiện được bảng giá
    return db.query(models.Service).options(
        joinedload(models.Service.category),
        joinedload(models.Service.price_rules), # Load bảng giá số lượng
        joinedload(models.Service.option_groups).joinedload(models.ServiceOptionGroup.options)
    ).filter(models.Service.is_deleted == False).all()

@router.post("/services", response_model=schemas.Service)
def create_service(
    service_in: schemas.ServiceCreate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    service_data = service_in.model_dump()
    options_data = service_data.pop("option_groups", [])
    price_rules_data = service_data.pop("price_rules", []) # Tách bảng giá

    # 1. Tạo Service
    db_service = models.Service(**service_data)
    db.add(db_service)
    db.flush() 

    # 2. Tạo Bảng giá số lượng (Price Rules)
    for rule in price_rules_data:
        db.add(models.PriceRule(**rule, service_id=db_service.id))

    # 3. Tạo Gia công (Options)
    for group in options_data:
        opts = group.pop("options", [])
        db_group = models.ServiceOptionGroup(**group, service_id=db_service.id)
        db.add(db_group)
        db.flush() 
        for opt in opts:
            db.add(models.ServiceOption(**opt, group_id=db_group.id))

    db.commit()
    db.refresh(db_service)
    return db_service

@router.put("/services/{service_id}", response_model=schemas.Service)
def update_service(
    service_id: int,
    service_in: schemas.ServiceCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    db_service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    data = service_in.model_dump()
    options_data = data.pop("option_groups", [])
    price_rules_data = data.pop("price_rules", [])
    
    # 1. Update thông tin cơ bản
    for key, value in data.items():
        setattr(db_service, key, value)

    # 2. DỌN DẸP DỮ LIỆU CŨ (Xóa con trước cha sau)
    # Xóa Price Rules cũ
    db.query(models.PriceRule).filter(models.PriceRule.service_id == service_id).delete()

    # Xóa Options cũ
    old_groups = db.query(models.ServiceOptionGroup).filter(models.ServiceOptionGroup.service_id == service_id).all()
    old_group_ids = [g.id for g in old_groups]
    if old_group_ids:
        db.query(models.ServiceOption).filter(models.ServiceOption.group_id.in_(old_group_ids)).delete(synchronize_session=False)
    db.query(models.ServiceOptionGroup).filter(models.ServiceOptionGroup.service_id == service_id).delete(synchronize_session=False)

    # 3. NẠP DỮ LIỆU MỚI
    # Nạp Price Rules
    for rule in price_rules_data:
        db.add(models.PriceRule(**rule, service_id=service_id))

    # Nạp Options
    for group in options_data:
        opts = group.pop("options", [])
        db_group = models.ServiceOptionGroup(**group, service_id=service_id)
        db.add(db_group)
        db.flush()
        for opt in opts:
            db.add(models.ServiceOption(**opt, group_id=db_group.id))

    db.commit()
    db.refresh(db_service)
    return db_service
@router.delete("/services/{service_id}")
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    db_service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # 🔴 XÓA CŨ: (BỎ HẾT ĐOẠN QUERY DELETE CON VÀ DB.DELETE GỐC)
    # db.query(models.PriceRule).filter(models.PriceRule.service_id == service_id).delete()
    # ...
    # db.delete(db_service)

    # 🟢 SỬA MỚI: CHỈ CẦN DÒNG NÀY LÀ DB KHÔNG CHỬI NỮA
    db_service.is_deleted = True 
    
    db.commit()
    return {"message": "Đã ngừng kinh doanh dịch vụ này, dữ liệu cũ vẫn được bảo toàn!"}
# --- QUẢN LÝ ĐƠN HÀNG (ORDER MANAGEMENT) ---

@router.get("/orders", response_model=List[schemas.Order])
def get_all_orders(
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    return db.query(models.Order)\
             .options(
                 joinedload(models.Order.user),
                 joinedload(models.Order.items).joinedload(models.OrderItem.service)
             )\
             .order_by(models.Order.id.desc())\
             .all()

@router.patch("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status_update: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db_order.status = status_update.status
    db.commit()
    return {"message": "Order status updated", "new_status": status_update.status}

# --- QUẢN LÝ DANH MỤC (CATEGORY MANAGEMENT) ---

@router.post("/categories", response_model=schemas.Category)
def create_category(
    category: schemas.CategoryBase,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category