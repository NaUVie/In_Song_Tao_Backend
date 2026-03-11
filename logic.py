from sqlalchemy.orm import Session
import models
import schemas
from fastapi import HTTPException

def calculate_item_price(db: Session, item: schemas.OrderItemCreate) -> float:
    # 1. Tìm Service
    service = db.query(models.Service).filter(models.Service.id == item.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail=f"Dịch vụ {item.service_id} không tồn tại")
    
    # 2. Lấy đơn giá gốc từ PriceRule (Dò mốc số lượng)
    price_rule = db.query(models.PriceRule).filter(
        models.PriceRule.service_id == item.service_id,
        models.PriceRule.min_qty <= item.quantity,
        (models.PriceRule.max_qty >= item.quantity) | (models.PriceRule.max_qty == None)
    ).first()
    
    if not price_rule:
        raise HTTPException(status_code=400, detail=f"Số lượng {item.quantity} không nằm trong bảng giá")
    
    unit_price = price_rule.unit_price
    
    # 3. Tính phụ phí gia công (Modifier)
    # Chúng ta sẽ tính tổng phụ phí trên mỗi đơn vị (unit_modifier) 
    # và phụ phí cố định trên cả đơn hàng (fixed_modifier)
    unit_modifier = 0
    fixed_modifier = 0
    
    if item.selected_options:
        for group in service.option_groups:
            selected_label = item.selected_options.get(group.name)
            if selected_label:
                # Tìm option trong DB
                selected_option = next((opt for opt in group.options if opt.label == selected_label), None)
                
                if selected_option:
                    m_type = selected_option.modifier_type
                    m_val = selected_option.price_modifier
                    
                    # Nếu m_type là NULL hoặc "per_unit" -> Cộng vào đơn giá
                    if m_type == "per_unit" or m_type is None:
                        unit_modifier += m_val
                    # Nếu là "fixed" -> Cộng thẳng vào tổng đơn (VD: Phí thiết kế)
                    elif m_type == "fixed":
                        fixed_modifier += m_val
                    # Nếu là "percentage" -> % của đơn giá gốc
                    elif m_type == "percentage":
                        unit_modifier += (unit_price * (m_val / 100))

    # 4. TỔNG TIỀN CUỐI CÙNG
    # Tổng = (Đơn giá gốc + Phụ phí mỗi cái) * Số lượng + Phụ phí cố định
    total_price = (unit_price + unit_modifier) * item.quantity + fixed_modifier
    
    return float(total_price)