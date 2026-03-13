from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
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

@router.get("/services", response_model=List[schemas.Service])
def get_admin_services(
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    return db.query(models.Service).options(
        joinedload(models.Service.category),
        joinedload(models.Service.price_rules),
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
    price_rules_data = service_data.pop("price_rules", [])

    db_service = models.Service(**service_data)
    db.add(db_service)
    db.flush() 

    for rule in price_rules_data:
        db.add(models.PriceRule(**rule, service_id=db_service.id))

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
    
    for key, value in data.items():
        setattr(db_service, key, value)

    db.query(models.PriceRule).filter(models.PriceRule.service_id == service_id).delete()
    old_groups = db.query(models.ServiceOptionGroup).filter(models.ServiceOptionGroup.service_id == service_id).all()
    old_group_ids = [g.id for g in old_groups]
    if old_group_ids:
        db.query(models.ServiceOption).filter(models.ServiceOption.group_id.in_(old_group_ids)).delete(synchronize_session=False)
    db.query(models.ServiceOptionGroup).filter(models.ServiceOptionGroup.service_id == service_id).delete(synchronize_session=False)

    for rule in price_rules_data:
        db.add(models.PriceRule(**rule, service_id=service_id))

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

# --- DASHBOARD STATS & CHART ---

@router.get("/stats")
def get_dashboard_stats(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    query_orders = db.query(models.Order)
    
    if start_date:
        query_orders = query_orders.filter(models.Order.created_at >= start_date)
    if end_date:
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        query_orders = query_orders.filter(models.Order.created_at < end_date_obj)

    total_revenue = query_orders.filter(models.Order.status != 'cancelled')\
        .with_entities(func.sum(models.Order.total_price)).scalar() or 0
    total_orders = query_orders.count()
    pending_orders = query_orders.filter(models.Order.status == 'pending').count()
    active_services = db.query(models.Service).filter(models.Service.is_deleted == False).count()

    recent_orders = query_orders.options(joinedload(models.Order.user))\
        .order_by(models.Order.id.desc()).limit(5).all()

    # THÊM ĐẾM SỐ ĐƠN HÀNG (order_count) VÀO BIỂU ĐỒ
    chart_query = db.query(
        func.date(models.Order.created_at).label('date'),
        func.sum(models.Order.total_price).label('revenue'),
        func.count(models.Order.id).label('order_count') 
    ).filter(models.Order.status != 'cancelled')
    
    if start_date: chart_query = chart_query.filter(models.Order.created_at >= start_date)
    if end_date: chart_query = chart_query.filter(models.Order.created_at < end_date_obj)
    chart_data = chart_query.group_by(func.date(models.Order.created_at)).all()

# 4. TOP DỊCH VỤ BÁN CHẠY (Thêm tính tổng tiền)
    top_services_query = db.query(
        models.Service.name,
        models.Service.image_url,
        func.sum(models.OrderItem.quantity).label('total_sold'),
        func.sum(models.OrderItem.item_price).label('total_revenue') # THÊM DÒNG NÀY ĐỂ TÍNH TIỀN
    ).join(models.OrderItem, models.Service.id == models.OrderItem.service_id)\
     .join(models.Order, models.Order.id == models.OrderItem.order_id)\
     .filter(models.Order.status != 'cancelled')

    if start_date: top_services_query = top_services_query.filter(models.Order.created_at >= start_date)
    if end_date: top_services_query = top_services_query.filter(models.Order.created_at < end_date_obj)

    top_services = top_services_query.group_by(models.Service.id)\
        .order_by(func.sum(models.OrderItem.quantity).desc()).limit(5).all()

    return {
        "totalOrders": total_orders,
        "pendingOrders": pending_orders,
        "totalRevenue": total_revenue,
        "activeServices": active_services,
        "recentOrders": recent_orders,
        "chartData": [{"date": str(r.date), "revenue": r.revenue, "order_count": r.order_count} for r in chart_data],
        # NHỚ SỬA DÒNG NÀY, THÊM total_revenue:
        "topServices": [{"name": r.name, "image_url": r.image_url, "total_sold": r.total_sold or 0, "total_revenue": r.total_revenue or 0} for r in top_services]
    }