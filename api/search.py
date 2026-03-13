from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
# Import DB và các bảng của ông (nhớ sửa đường dẫn import cho đúng project của ông nhé)
from database import get_db
import models 

router = APIRouter()

@router.get("/")
def global_search(q: str = "", db: Session = Depends(get_db)):
    if not q or len(q) < 2:
        # Trả về rỗng nếu không nhập gì hoặc nhập có 1 ký tự
        return {"services": [], "categories": [], "orders": []}

    search_keyword = f"%{q}%"

    # 1. Tìm trong bảng Dịch vụ (Ví dụ tìm theo tên hoặc mô tả)
    services = db.query(models.Service).filter(
        or_(
            models.Service.name.ilike(search_keyword),
            models.Service.description.ilike(search_keyword)
        )
    ).limit(5).all() # Chỉ lấy 5 kết quả đầu cho nhẹ web

    # 2. Tìm trong bảng Danh mục
    categories = db.query(models.Category).filter(
        models.Category.name.ilike(search_keyword)
    ).limit(5).all()

    # 3. Tìm trong bảng Đơn hàng (Tìm theo Mã đơn hoặc Tên khách)
    # Giả sử bảng Order có cột order_code và customer_name
    # orders = db.query(models.Order).filter(
    #     or_(
    #         models.Order.order_code.ilike(search_keyword),
    #         models.Order.customer_name.ilike(search_keyword)
    #     )
    # ).limit(5).all()

    # Gom tất cả lại trả về cho Frontend
    return {
        "services": services,
        "categories": categories,
        # "orders": orders
    }