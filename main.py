import os
import asyncio
import base64
import logging
from telethon import TelegramClient, events
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- Flask keep-alive szerver (Render free verzióhoz) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Telegram Forward Bot fut rendben!"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# Keep-alive aktiválása
keep_alive()

# --- .env beolvasás (helyi futtatáshoz) ---
load_dotenv()

# --- Logolás beállítása ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("forward_log.txt", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Session visszaállítása Render környezetből ---
if os.getenv("SESSION_B64"):
    try:
        with open("user_session.session", "wb") as f:
            f.write(base64.b64decode(os.getenv("SESSION_B64")))
        logger.info("🔓 Session file regenerated from environment.")
    except Exception as e:
        logger.error(f"⚠️ Session regeneration failed: {e}")
else:
    logger.warning("ℹ️ No SESSION_B64 found in environment, proceeding normally.")

# --- Környezeti változók betöltése ---
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
phone_number = os.getenv('PHONE_NUMBER')
source_chat_ids_str = os.getenv('SOURCE_CHAT_ID', '0')
target_chat_id = int(os.getenv('TARGET_CHAT_ID', '0'))

# Ellenőrzés
missing = []
for var_name, var_value in [
    ("TELEGRAM_API_ID", api_id),
    ("TELEGRAM_API_HASH", api_hash),
    ("PHONE_NUMBER", phone_number),
    ("SOURCE_CHAT_ID", source_chat_ids_str),
    ("TARGET_CHAT_ID", target_chat_id)
]:
    if not var_value:
        missing.append(var_name)
if missing:
    raise ValueError(f"❌ Hiányzó environment változók: {', '.join(missing)}")

# --- Forrás chat ID-k feldolgozása ---
source_chat_ids = []
for id_str in source_chat_ids_str.split(','):
    try:
        source_chat_ids.append(int(id_str.strip()))
    except ValueError:
        logger.warning(f"⚠️ Érvénytelen SOURCE_CHAT_ID: {id_str}")

# --- Telegram kliens létrehozása (User Account) ---
client = TelegramClient('user_session', int(api_id), api_hash)

chat_names = {}

async def startup():
    try:
        if not await client.is_user_authorized():
            logger.info("📱 Bejelentkezés szükséges...")
            await client.start(phone=lambda: phone_number)
        else:
            await client.connect()

        me = await client.get_me()
        logger.info(f"✅ Bejelentkezve mint: {me.first_name} (@{me.username if me.username else 'nincs username'})")
        logger.info(f"📥 Forrás chat-ek száma: {len(source_chat_ids)}")
        logger.info(f"📤 Cél chat ID: {target_chat_id}")

        valid_source_ids = []
        for source_id in source_chat_ids:
            try:
                source_chat = await client.get_entity(source_id)
                chat_names[source_id] = getattr(source_chat, 'title', 'Private chat')
                valid_source_ids.append(source_id)
                logger.info(f"✅ Forrás chat elérhető: {chat_names[source_id]} (ID: {source_id})")
            except Exception as e:
                logger.warning(f"⚠️ Kihagyva: Forrás chat nem elérhető ({source_id}): {e}")

        # --- Üzenetek (szöveg / egyképes / fájlos posztok) ---
        @client.on(events.NewMessage(chats=valid_source_ids))
        async def forward_message(event):
            try:
                source_name = chat_names.get(event.chat_id, f"Chat {event.chat_id}")
                logger.info(f"📨 Új üzenet a '{source_name}' csoportból (ID: {event.id})")
                await event.forward_to(target_chat_id)
                logger.info(f"✅ Üzenet továbbítva: {event.id}")
            except Exception as e:
                logger.error(f"❌ Továbbítási hiba (üzenet {event.id}): {e}")

        # --- Albumok (többképes / többmédiás posztok) ---
        @client.on(events.Album(chats=valid_source_ids))
        async def forward_album(event):
            try:
                source_name = chat_names.get(event.chat_id, f"Chat {event.chat_id}")
                logger.info(f"🖼️ Új album a '{source_name}' csoportból ({len(event.messages)} elem)")

                messages = event.messages
                caption = messages[0].message or ""

                await client.send_file(
                    target_chat_id,
                    [msg.media for msg in messages if msg.media],
                    caption=caption
                )
                logger.info(f"✅ Album továbbítva ({len(messages)} elem)")
            except Exception as e:
                logger.error(f"❌ Album továbbítási hiba: {e}")

        logger.info("🚀 Bot fut és figyeli az üzeneteket...")
        await client.run_until_disconnected()

    except Exception as e:
        logger.error(f"❌ Inicializálási hiba: {e}")
        raise

# --- Futtatás ---
if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(startup())
