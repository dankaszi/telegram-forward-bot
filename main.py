import os
import asyncio
from telethon import TelegramClient, events
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Flask szerver (Render miatt, de lokálisan sem zavar)
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Telegram Forward Bot aktív (user account módban)"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# Indítjuk a webservert (Render vagy lokál teszt miatt)
keep_alive()

# Betöltjük az .env változókat
load_dotenv()

import base64

# Decode session from environment if available
if os.getenv("SESSION_B64"):
    with open("user_session.session", "wb") as f:
        f.write(base64.b64decode(os.getenv("SESSION_B64")))
    print("🔓 Session file regenerated from environment.")


# 🔧 Alapbeállítások környezeti változókból
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
phone_number = os.getenv('PHONE_NUMBER')
source_chat_ids_str = os.getenv('SOURCE_CHAT_ID', '0')
target_chat_id = int(os.getenv('TARGET_CHAT_ID', '0'))

# Több forrás csoport támogatása
source_chat_ids = [int(id.strip()) for id in source_chat_ids_str.split(',') if id.strip()]

# Ellenőrizzük, hogy minden megvan-e
missing = [var for var, val in [
    ("TELEGRAM_API_ID", api_id),
    ("TELEGRAM_API_HASH", api_hash),
    ("PHONE_NUMBER", phone_number),
    ("SOURCE_CHAT_ID", source_chat_ids_str),
    ("TARGET_CHAT_ID", target_chat_id)
] if not val]

if missing:
    raise ValueError(f"❌ Hiányzó environment változók: {', '.join(missing)}")

# 📱 User account mód (nem bot token)
import asyncio
asyncio.set_event_loop(asyncio.new_event_loop())
client = TelegramClient('user_session', int(api_id), api_hash)

chat_names = {}

async def startup():
    await client.connect()
    if not await client.is_user_authorized():
        print("📱 Bejelentkezés szükséges...")
        await client.start(phone=lambda: phone_number)
    else:
        await client.start()

    me = await client.get_me()
    print(f"✅ Bejelentkezve mint: {me.first_name} ({me.username or 'nincs username'})")
    print(f"📱 Telefonszám: {me.phone}")
    print(f"📥 Forrás chat-ek száma: {len(source_chat_ids)}")
    print(f"📤 Cél chat ID: {target_chat_id}")

    for src in source_chat_ids:
        try:
            ent = await client.get_entity(src)
            chat_names[src] = getattr(ent, 'title', 'Privát chat')
            print(f"✅ Forrás chat elérhető: {chat_names[src]} (ID: {src})")
        except Exception as e:
            print(f"❌ Hiba a forrás chatnál ({src}): {e}")

@client.on(events.NewMessage(chats=source_chat_ids))
async def forward_message(event):
    try:
        src_name = chat_names.get(event.chat_id, str(event.chat_id))
        print(f"📨 Új üzenet érkezett: {src_name} (ID: {event.id})")
        await event.forward_to(target_chat_id)
        print(f"✅ Üzenet továbbítva: {event.id}")
    except Exception as e:
        print(f"❌ Továbbítási hiba: {e}")

async def main():
    await startup()
    print("\n🚀 A bot fut és figyeli az üzeneteket...\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
