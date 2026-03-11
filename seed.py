from database import SessionLocal, engine, Base
import models

def seed():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # 1. Clear existing data (Optional, handle with care in prod)
    # db.query(models.ServiceOption).delete()
    # db.query(models.ServiceOptionGroup).delete()
    # db.query(models.PriceRule).delete()
    # db.query(models.Service).delete()
    # db.query(models.Category).delete()
    # db.commit()

    # 2. Create Categories matching NavBar exactly based on songtao.vn list
    raw_categories = [
        ("Bằng Khen", "bang-khen"),
        ("Banner/ Poster", "banner-poster"),
        ("Bao Lì xì", "bao-li-xi"),
        ("Bao thư", "bao-thu"),
        ("Bìa đựng Thẻ từ", "bia-dung-the-tu"),
        ("Bìa hồ sơ", "bia-ho-so"),
        ("Biểu mẫu/ Carbonless", "bieu-mau"),
        ("Bưu ảnh/ Postcard", "buu-anh"),
        ("Catalogue", "catalogue"),
        ("Colorchart", "color-chart"),
        ("Cưới hỏi - Sự kiện", "cuoi-hoi-su-kien"),
        ("Danh thiếp", "danh-thiep"),
        ("Đế Lót Ly", "de-lot-ly"),
        ("Decal giấy (tờ rời)", "decal-giay"),
        ("Ghi chú/ block note", "ghi-chu"),
        ("Giấy Lót Bàn Ăn", "giay-lot-ban-an"),
        ("Giấy tiêu đề", "giay-tieu-de"),
        ("Hộp giấy", "hop-giay"),
        ("In nhanh", "in-nhanh"),
        ("In trên Nhựa", "in-tren-nhua"),
        ("Inproof", "inproof"),
        ("Lịch", "lich"),
        ("Menu", "menu"),
        ("Nhãn Cổ Chai", "nhan-co-chai"),
        ("Nhãn Decal các loại", "nhan-decal"),
        ("Nhãn treo (Tags) - Nhãn Giấy", "nhan-treo"),
        ("Phiếu bảo hành", "phieu-bao-hanh"),
        ("Phiếu Tích điểm", "phieu-tich-diem"),
        ("Photobook", "photobook"),
        ("Quạt", "quat"),
        ("Standee để bàn", "standee-de-ban"),
        ("Tem bảo hành", "tem-bao-hanh"),
        ("Thiệp - Thiệp cưới", "thiep-cuoi"),
        ("Thiết kế Logo", "thiet-ke-logo"),
        ("Tờ rơi - Tờ gấp", "to-roi-to-gap"),
        ("Túi giấy", "tui-giay"),
        ("Vé giữ xe", "ve-giu-xe"),
        ("Voucher - Coupon", "voucher-coupon")
    ]

    cats = {}
    for index, (name, slug) in enumerate(raw_categories):
        cat = models.Category(name=name, slug=slug)
        cats[slug] = cat
    
    for c in cats.values():
        existing = db.query(models.Category).filter_by(slug=c.slug).first()
        if not existing:
            db.add(c)
    db.commit()

    # Refresh IDs
    for key in cats:
        cats[key] = db.query(models.Category).filter_by(slug=cats[key].slug).first()

    # 3. Create Services Demo implementation for a few categories, others can be expanded later
    services = [
        models.Service(category_id=cats["danh-thiep"].id, name="Danh thiếp Bồi 2 lớp", slug="danh-thiep-boi", description="In danh thiếp dày dặn, sang trọng.", image_url="https://songtao.vn/upload/sanpham/danh-thiep-gia-re.jpg"),
        models.Service(category_id=cats["danh-thiep"].id, name="Danh thiếp Giấy Couche 300gsm", slug="danh-thiep-c300", description="Kích thước 9x5.4cm. In offset 4 màu 2 mặt. Cán màng mờ 2 mặt.", image_url="https://songtao.vn/upload/sanpham/danh-thiep-gia-re.jpg"),
        models.Service(category_id=cats["to-roi-to-gap"].id, name="Tờ rơi A5 - C150gsm", slug="to-roi-a5-c150", description="Giấy Couche 150gsm. In offset 4 màu 2 mặt.", image_url="https://songtao.vn/upload/sanpham/to-roi-a5.jpg"),
        models.Service(category_id=cats["nhan-decal"].id, name="Tem Decal Giấy", slug="tem-decal-giay", description="Decal giấy đế vàng/trắng. Cán màng bóng/mờ. Bế demi.", image_url="https://songtao.vn/upload/sanpham/decal-giay.jpg"),
        models.Service(category_id=cats["bao-thu"].id, name="Bao thư 12x22cm", slug="bao-thu-nho", description="Kích thước 12x22cm. Giấy Fort 100gsm. Nắp keo.", image_url="https://songtao.vn/upload/sanpham/bao-thu-nho.jpg"),
        models.Service(category_id=cats["catalogue"].id, name="In Catalogue A4", slug="in-catalogue-a4", description="Kích thước A4 đứng. Bìa C250gsm, Ruột C150gsm. Đóng kim giữa hoặc keo gáy.", image_url="https://songtao.vn/upload/sanpham/catalogue.jpg"),
        models.Service(category_id=cats["voucher-coupon"].id, name="Voucher Giá Rẻ", slug="in-voucher", description="Kích thước 7x18cm. Cấn răng cưa hoặc không.", image_url="https://songtao.vn/upload/sanpham/voucher-coupon.jpg"),
        models.Service(category_id=cats["menu"].id, name="Menu Bồi Nhựa", slug="in-menu", description="Chống nước, bền đẹp. Menu đóng cuốn.", image_url="https://songtao.vn/upload/sanpham/menu.jpg"),
        models.Service(category_id=cats["bao-li-xi"].id, name="Bao Lì Xì (In Nhanh)", slug="bao-li-xi-nhanh", description="Giấy C150gsm. In offset chuẩn màu.", image_url="https://songtao.vn/upload/sanpham/bao-li-xi.jpg"),
        models.Service(category_id=cats["tui-giay"].id, name="Túi Giấy Kraft Có Quai", slug="tui-giay-kraft", description="Túi giấy bảo vệ môi trường.", image_url="https://songtao.vn/upload/sanpham/tui-giay.jpg"),
        models.Service(category_id=cats["bang-khen"].id, name="Bằng Khen Khung Gỗ", slug="bang-khen-go", description="Giấy mỹ thuật cao cấp + lồng khung gỗ.", image_url="https://songtao.vn/upload/sanpham/danh-thiep-gia-re.jpg")
    ]

    for s in services:
        existing = db.query(models.Service).filter_by(slug=s.slug).first()
        if not existing:
            db.add(s)
            db.commit() 
            # Re-fetch to get ID
            s = db.query(models.Service).filter_by(slug=s.slug).first()
            
            # Add basic price rules
            rules = [
                models.PriceRule(service_id=s.id, min_qty=100, max_qty=499, unit_price=500),
                models.PriceRule(service_id=s.id, min_qty=500, max_qty=999, unit_price=450),
                models.PriceRule(service_id=s.id, min_qty=1000, max_qty=None, unit_price=200)
            ]
            db.add_all(rules)
            
            # Add Options (Simplified)
            group = models.ServiceOptionGroup(service_id=s.id, name="Thành phẩm")
            db.add(group)
            db.commit()
            db.add_all([
                models.ServiceOption(group_id=group.id, label="Cán màng mờ", price_modifier=0, modifier_type="fixed"),
                models.ServiceOption(group_id=group.id, label="Cán màng bóng", price_modifier=0, modifier_type="fixed")
            ])

    db.commit()
    db.close()
    print("Database seeded with Songtao data!")

if __name__ == "__main__":
    try:
        seed()
    except Exception as e:
        print(f"Error seeding: {e}")
