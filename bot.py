import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters

# Render-க்காக ஒரு சிறிய Dummy Web Server
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), KeepAliveHandler)
    server.serve_forever()

# Server-ஐ தனியாக பின்னணியில் ரன் செய்ய
threading.Thread(target=run_dummy_server, daemon=True).start()

# உங்களின் API விவரங்கள்
API_ID = "33442108"
API_HASH = "db58bfc24809316cecb3f5c83e84116c"
BOT_TOKEN = "8281564589:AAE7NGNs3KZZ-Dnu94juPv2ecoJfnfMFDdc"

app = Client("thumbnail_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_thumbnails = {}

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Hi! முதலில் ஒரு Photo-வை அனுப்புங்கள் (அது Thumbnail ஆக சேமிக்கப்படும்). பின்பு Video-வை அனுப்புங்கள்.")

@app.on_message(filters.photo)
def save_thumb(client, message):
    user_id = message.from_user.id
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    file_path = message.download(file_name=f"downloads/{user_id}_thumb.jpg")
    user_thumbnails[user_id] = file_path
    message.reply_text("✅ Thumbnail சேமிக்கப்பட்டது! இப்போது Video-வை அனுப்புங்கள்.")

@app.on_message(filters.video)
def change_thumb(client, message):
    user_id = message.from_user.id
    if user_id in user_thumbnails:
        msg = message.reply_text("⏳ Processing video... Please wait.")
        video_path = message.download()
        thumb_path = user_thumbnails[user_id]
        
        client.send_video(
            chat_id=message.chat.id,
            video=video_path,
            thumb=thumb_path,
            caption="Here is your video with the new custom thumbnail!"
        )
        os.remove(video_path)
        msg.delete()
    else:
        message.reply_text("❌ முதலில் ஒரு Photo-வை Thumbnail ஆக அனுப்புங்கள்!")

print("Bot is alive and running...")
app.run()
