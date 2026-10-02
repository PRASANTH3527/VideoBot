import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

import os
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters
from PIL import Image

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

threading.Thread(target=run_dummy_server, daemon=True).start()

API_ID = "33442108"
API_HASH = "db58bfc24809316cecb3f5c83e84116c"
BOT_TOKEN = "8281564589:AAE7NGNs3KZZ-Dnu94juPv2ecoJfnfMFDdc"

app = Client("thumbnail_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_thumbnails = {}

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Hi! முதலில் ஒரு Photo-வை அனுப்புங்கள். பின்பு Video-வை 'File' ஆக அனுப்புங்கள்.")

@app.on_message(filters.photo | filters.video | filters.document)
def handle_media(client, message):
    user_id = message.from_user.id
    
    # 1. Photo-வை Thumbnail ஆக செட் செய்ய
    if message.photo or (message.document and message.document.mime_type and message.document.mime_type.startswith("image/")):
        if not os.path.exists("downloads"):
            os.makedirs("downloads")
        
        msg = message.reply_text("⏳ Saving and resizing thumbnail...")
        
        # Caching-ஐ தவிர்க்க ஒவ்வொரு படத்திற்கும் ஒரு Unique பெயர் (Timestamp)
        unique_id = int(time.time())
        raw_path = message.download(file_name=f"downloads/{user_id}_{unique_id}_raw.jpg")
        thumb_path = f"downloads/{user_id}_{unique_id}_thumb.jpg"
        
        try:
            img = Image.open(raw_path)
            img.thumbnail((320, 320))
            img.save(thumb_path, "JPEG")
            os.remove(raw_path)
            
            # பழைய thumbnail ஃபைல் சிஸ்டமில் இருந்தால் டெலீட் செய்ய
            if user_id in user_thumbnails and os.path.exists(user_thumbnails[user_id]):
                os.remove(user_thumbnails[user_id])
                
            user_thumbnails[user_id] = thumb_path
            msg.edit_text("✅ Thumbnail சேமிக்கப்பட்டது! (320x320 Resized).\nஇப்போது Video-வை 'File' ஆக அனுப்புங்கள்.")
        except Exception as e:
            msg.edit_text("❌ Error processing image. வேறு ஒரு Photo-வை அனுப்புங்கள்.")
            
    # 2. Video-வை Thumbnail உடன் திருப்பி அனுப்ப
    elif message.video or (message.document and message.document.mime_type and message.document.mime_type.startswith("video/")):
        if user_id in user_thumbnails:
            msg = message.reply_text("⏳ Processing video file... Please wait.")
            video_path = message.download()
            thumb_path = user_thumbnails[user_id]
            
            try:
                if message.document:
                    file_name = message.document.file_name or "video.mp4"
                    client.send_document(
                        chat_id=message.chat.id,
                        document=video_path,
                        thumb=thumb_path,
                        caption="Uploaded via Bot",
                        force_document=True,
                        file_name=file_name
                    )
                else:
                    client.send_video(
                        chat_id=message.chat.id,
                        video=video_path,
                        thumb=thumb_path,
                        caption="Uploaded via Bot"
                    )
            except Exception as e:
                message.reply_text(f"❌ Error sending file: {e}")
                
            os.remove(video_path)
            msg.delete()
        else:
            message.reply_text("❌ முதலில் ஒரு Photo-வை Thumbnail ஆக அனுப்புங்கள்!")

print("Bot is alive and running...")
app.run()
