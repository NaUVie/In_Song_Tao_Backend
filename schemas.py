from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
# --- USER ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- SERVICE OPTIONS ---
class ServiceOptionBase(BaseModel):
    label: str
    price_modifier: float = 0
    modifier_type: Optional[str] = None

class ServiceOptionGroupBase(BaseModel):
    name: str
    is_required: bool = True
    options: List[ServiceOptionBase]

# --- PRICE RULES (Số lượng & Đơn giá) ---
class PriceRuleBase(BaseModel):
    min_qty: int
    max_qty: Optional[int] = None
    unit_price: float

# --- SERVICE MAIN ---
class ServiceBase(BaseModel):
    category_id: int
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_deleted: bool = False  
class ServiceCreate(ServiceBase):
    option_groups: List[ServiceOptionGroupBase] = []
    price_rules: List[PriceRuleBase] = [] 
class Service(ServiceBase):
    id: int
    option_groups: List[ServiceOptionGroupBase] = [] 
    price_rules: List[PriceRuleBase] = []
    class Config:
        from_attributes = True

# --- CATEGORY ---
class CategoryBase(BaseModel):
    name: str
    slug: str
    image_url: Optional[str] = None  
    parent_id: Optional[int] = None
class CategoryCreate(CategoryBase): 
    pass

class Category(CategoryBase):
    id: int
    services: List[Service] = []
    class Config:
        from_attributes = True

# --- ORDERS ---
class OrderItemCreate(BaseModel):
    service_id: int
    quantity: int
    selected_options: Dict[str, Any]
    artwork_url: Optional[str] = None

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    recipient_name: str
    phone_number: str
    address: str
class OrderItem(BaseModel):
    id: int
    service_id: int
    service: Optional[Service] = None 
    quantity: int
    item_price: float
    selected_options: Optional[Dict[str, Any]] = None
    artwork_url: Optional[str] = None
    class Config:
        from_attributes = True

class Order(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: datetime
    user: Optional[User] = None 
    items: List[OrderItem]
    recipient_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str
    
    # --- BANNERS ---
class BannerBase(BaseModel):
    title: Optional[str] = None
    image_url: str
    link: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0
    position: str = "top"

class BannerCreate(BannerBase):
    pass

class Banner(BannerBase):
    id: int
    class Config:
        from_attributes = True
        
# --- NEWS ---
class NewsBase(BaseModel):
    title: str
    slug: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True

class NewsCreate(NewsBase):
    content: str

# Thêm cái này để fix lỗi 422 khi Update (PUT)
class NewsUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True

# Dùng cho trang danh sách (Bỏ qua cột content cho nhẹ)
class NewsShort(NewsBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# Dùng cho trang chi tiết (Có đầy đủ content)
class News(NewsBase):
    id: int
    content: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True