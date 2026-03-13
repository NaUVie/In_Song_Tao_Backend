import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ca_path = os.path.join(BASE_DIR, "ca.pem")

# 1. LẤY DATABASE URL TỪ MÔI TRƯỜNG
db_url = os.getenv("DATABASE_URL")

# 2. XỬ LÝ LOGIC LOCAL / PRODUCTION
if not db_url:
    # Không có biến môi trường -> Đang chạy ở máy cá nhân (Local)
    db_url = "mysql+pymysql://root:@localhost:3306/InNhanhTYD"
    print(">>> [MÔI TRƯỜNG]: Đang chạy ở LOCAL - Dùng Database Localhost")
else:
    # Có biến môi trường -> Đang chạy trên Server thật (Render)
    if db_url.startswith("mysql://"):
        db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)
    print(">>> [MÔI TRƯỜNG]: Đang chạy trên PRODUCTION - Dùng Database Online")

# 3. CẤU HÌNH SSL CHO CLOUD (Aiven)
connect_args = {}
if db_url and "aivencloud" in db_url:
    if os.path.exists(ca_path):
        connect_args = {
            "ssl": {
                "ca": ca_path
            }
        }
    else:
        connect_args = {
            "ssl": {
                "check_hostname": False,
                "verify_mode": 0 
            }
        }

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