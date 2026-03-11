import cloudinary
import cloudinary.uploader
import urllib.request
import re
import json
import ssl

# Configuration
cloudinary.config( 
    cloud_name = "dctmlwevc", 
    api_key = "538515369964225", 
    api_secret = "ETu_ZZZMHAnKjgxImHaMbbiqoNM", 
    secure=True
)

url = "https://songtao.vn/trang-chu.aspx"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        html = response.read().decode('utf-8')
        
    img_tags = re.findall(r'<img[^>]+src="([^">]+)"[^>]*alt="([^">]*)"', html, re.IGNORECASE)
    
    results = {}
    print(f"Found {len(img_tags)} image tags. Filtering...")
    
    for src, alt in img_tags:
        if '/upload/sanpham/' in src:
            full_src = src if src.startswith('http') else 'https://songtao.vn' + src
            name = alt.strip()
            # Prevent re-uploading the same name and ignore empty names
            if name and name not in results:
                print(f"Uploading {name} from {full_src}...")
                try:
                    upload_result = cloudinary.uploader.upload(full_src, public_id=f"innhanhtyd_{re.sub(r'[^a-zA-Z0-9_\-]', '_', name.lower())}")
                    results[name] = upload_result["secure_url"]
                    print(f"Success: {upload_result['secure_url']}")
                except Exception as upload_e:
                    print(f"Upload failed for {name}: {upload_e}")
            
    print("Finished uploading images.")
    with open('scraped_images.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        print("Saved mapping to scraped_images.json")
        
except Exception as e:
    print(f"Error scraping: {e}")
