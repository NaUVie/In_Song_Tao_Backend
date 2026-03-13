from sqlalchemy.orm import Session
import models
import schemas
from fastapi import HTTPException

def calculate_item_price(db: Session, item: schemas.OrderItemCreate) -> float:
    service = db.query(models.Service).filter(models.Service.id == item.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail=f"Dịch vụ {item.service_id} không tồn tại")
    
    price_rule = db.query(models.PriceRule).filter(
        models.PriceRule.service_id == item.service_id,
        models.PriceRule.min_qty <= item.quantity,
        (models.PriceRule.max_qty >= item.quantity) | (models.PriceRule.max_qty == None)
    ).first()
    
    if not price_rule:
        raise HTTPException(status_code=400, detail=f"Số lượng {item.quantity} không nằm trong bảng giá")
    
    unit_price = price_rule.unit_price
    

    unit_modifier = 0
    fixed_modifier = 0
    
    if item.selected_options:
        for group in service.option_groups:
            selected_label = item.selected_options.get(group.name)
            if selected_label:
                selected_option = next((opt for opt in group.options if opt.label == selected_label), None)
                
                if selected_option:
                    m_type = selected_option.modifier_type
                    m_val = selected_option.price_modifier
                    
                    if m_type == "per_unit" or m_type is None:
                        unit_modifier += m_val
                    elif m_type == "fixed":
                        fixed_modifier += m_val
                    elif m_type == "percentage":
                        unit_modifier += (unit_price * (m_val / 100))

    total_price = (unit_price + unit_modifier) * item.quantity + fixed_modifier
    
    return float(total_price)