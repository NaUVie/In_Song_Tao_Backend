from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 1. Lấy đường dẫn tuyệt đối của folder hiện tại
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Đường dẫn tới file ca.pem sếp tải từ Aiven về bỏ vào project
ca_path = os.path.join(BASE_DIR, "ca.pem")

# 2. Lấy URL từ Render Environment
db_url = os.getenv("DATABASE_URL")

# 3. Xử lý link: Nếu là link Aiven (mysql://) thì phải đổi thành mysql+pymysql://
if db_url:
    if db_url.startswith("mysql://"):
        db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)
else:
    # Link chạy local ở máy sếp
    db_url = "mysql+pymysql://root:@localhost:3306/InNhanhTYD"

# 4. Cấu hình connect_args linh hoạt
connect_args = {}

# Nếu đang kết nối tới Cloud (Aiven), dùng file ca.pem để xác thực
if "aivencloud" in db_url:
    if os.path.exists(ca_path):
        connect_args = {
            "ssl": {
                "ca": ca_path
            }
        }
    else:
        # Nếu lỡ quên chưa upload file ca.pem, dùng cái này để chữa cháy (không khuyến khích)
        connect_args = {
            "ssl": {
                "check_hostname": False,
                "verify_mode": 0 # Tạm thời tắt verify để nó cho qua
            }
        }

# 5. Khởi tạo Engine
engine = create_engine(
    db_url, 
    pool_pre_ping=True,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()