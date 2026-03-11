from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 1. Lấy URL từ Render Environment
db_url = os.getenv("DATABASE_URL")

# 2. Xử lý link: Nếu là link Aiven (mysql://) thì phải đổi thành mysql+pymysql://
if db_url:
    if db_url.startswith("mysql://"):
        db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)
else:
    # Link chạy local ở máy sếp
    db_url = "mysql+pymysql://root:@localhost:3306/InNhanhTYD"

# 3. Cấu hình Engine với SSL (Bắt buộc cho Aiven)
# Thêm connect_args để nó chịu kết nối bảo mật SSL
engine = create_engine(
    db_url, 
    pool_pre_ping=True,
    connect_args={
        "ssl": {
            "ssl_mode": "REQUIRED"
        }
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()