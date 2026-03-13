from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON, Text,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255))
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    orders = relationship("Order", back_populates="user")
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    slug = Column(String(255), unique=True, index=True)
    services = relationship("Service", back_populates="category")
    image_url = Column(String(1024), nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String(255), index=True)
    slug = Column(String(255), unique=True, index=True)
    description = Column(Text)
    image_url = Column(String(1024), nullable=True)
    category = relationship("Category", back_populates="services")
    option_groups = relationship("ServiceOptionGroup", back_populates="service")
    price_rules = relationship("PriceRule", back_populates="service")
    is_deleted = Column(Boolean, default=False)
class ServiceOptionGroup(Base):
    __tablename__ = "service_option_groups"
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"))
    name = Column(String(255))  # e.g., "Loại giấy", "Kích thước"
    is_required = Column(Boolean, default=True)
    service = relationship("Service", back_populates="option_groups")
    options = relationship("ServiceOption", back_populates="group")

class ServiceOption(Base):
    __tablename__ = "service_options"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("service_option_groups.id"))
    label = Column(String(255))
    price_modifier = Column(Float, default=0.0)
    modifier_type = Column(String(50))  # "fixed", "percentage", "per_unit"
    group = relationship("ServiceOptionGroup", back_populates="options")

class PriceRule(Base):
    __tablename__ = "price_rules"
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"))
    min_qty = Column(Integer)
    max_qty = Column(Integer, nullable=True)
    unit_price = Column(Float)
    metadata_json = Column(JSON, nullable=True)  # Store custom calculation logic if needed
    service = relationship("Service", back_populates="price_rules")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_price = Column(Float)
    status = Column(String(50), default="pending")
    
    # Dòng này bây giờ sẽ chạy ngon lành
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    quantity = Column(Integer)
    selected_options = Column(JSON)  # Store snapshot of options
    item_price = Column(Float)
    artwork_url = Column(String(1024), nullable=True)
    service = relationship("Service") 
    order = relationship("Order", back_populates="items")

    
class Banner(Base):
    __tablename__ = "banners"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=False)
    link = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    position = Column(String(50), default="top")