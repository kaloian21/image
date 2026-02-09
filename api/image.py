# pip install requests pillow
import requests
from PIL import Image
import io
import re
import time

WEBHOOK_URL = "https://discord.com/api/webhooks/1453367787794989149/WwqkuvlRMlHNPgabwfBo9No62X1PN1E9ztoHcKibPtqNbBiFcS3Ia9yxT0KvdLqQkVqQ"

def send_to_webhook(content, image_url=None, username="Image Logger"):
    payload = {
        "content": content,
        "username": username,
        "avatar_url": "https://cdn.neowin.com/news/images/uploaded/2023/06/1686292349_windows_xp_bliss_wallpaper_4k.jpg"  # trollface or whatever
    }
    
    if image_url:
        try:
            r = requests.get(image_url, timeout=6)
            if r.status_code == 200:
                img = Image.open(io.BytesIO(r.content))
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format or 'PNG')
                img_byte_arr.seek(0)
                
                files = {'file': ('stolen_image.png', img_byte_arr, 'image/png')}
                requests.post(WEBHOOK_URL, data={"payload_json": str(payload)}, files=files, timeout=10)
                return
        except:
            pass
    
    # fallback - just send link + embed style
    embed = {
        "title": "New image caught",
        "description": image_url,
        "color": 0xff5555,
        "image": {"url": image_url}
    }
    payload["embeds"] = [embed]
    requests.post(WEBHOOK_URL, json=payload, timeout=8)


def is_image_url(text):
    image_exts = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
    return any(text.lower().endswith(ext) for ext in image_exts) or \
           bool(re.search(r'(cdn\.discordapp\.com|media\.discordapp\.net)/attachments/', text))


print("Image logger running... (only prints to webhook)")
print("Press Ctrl+C to stop\n")

while True:
    try:
        msg = input("> ")
        
        # very dumb url extraction
        urls = re.findall(r'(https?://[^\s<>"\']+)', msg)
        
        for url in urls:
            if is_image_url(url):
                print(f"[+] Image URL found → {url}")
                send_to_webhook(
                    f"**Logged image from user input**\n{url}",
                    image_url=url,
                    username="Sneaky Logger"
                )
                
    except KeyboardInterrupt:
        print("\n[!] Stopped.")
        break
    except Exception as e:
        print(f"[-] Error: {e}")
    time.sleep(0.3)
