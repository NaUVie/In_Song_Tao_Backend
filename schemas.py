from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

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
# SẾP CHÚ Ý THẰNG NÀY: Dùng để nhận dữ liệu từ Admin gửi lên
class ServiceCreate(ServiceBase):
    option_groups: List[ServiceOptionGroupBase] = []
    price_rules: List[PriceRuleBase] = [] # <--- PHẢI CÓ DÒNG NÀY THÌ MỚI LƯU ĐƯỢC GIÁ

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
    image_url: Optional[str] = None  # <--- ĐÃ THÊM ĐỂ NHẬN LINK ẢNH TỪ VUE

class CategoryCreate(CategoryBase):  # <--- ĐÃ THÊM CLASS NÀY ĐỂ API CREATE HOẠT ĐỘNG
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
    user: Optional[User] = None 
    items: List[OrderItem]
    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str