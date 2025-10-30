import os
from telethon.sync import TelegramClient

# Get credentials from environment
api_id = int(os.getenv('TELEGRAM_API_ID', '0'))
api_hash = os.getenv('TELEGRAM_API_HASH', '')
phone_number = os.getenv('PHONE_NUMBER', '')

print("🔐 Telegram User Login")
print("=" * 50)
print("Ez a szkript interaktívan bejelentkeztet a Telegram-ba.")
print("A session file mentésre kerül, és a main.py automatikusan használni tudja.")
print("=" * 50)
print()

# Create client with the same session name as main.py
client = TelegramClient('user_session', api_id, api_hash)

async def login():
    await client.start(phone=phone_number)
    me = await client.get_me()
    print(f"\n✅ Sikeres bejelentkezés!")
    print(f"👤 Név: {me.first_name}")
    print(f"📱 Username: @{me.username if me.username else 'nincs'}")
    print(f"☎️ Telefonszám: {me.phone}")
    print()
    print("✅ A session file mentve lett. Most már futtathatod a main.py-t!")
    await client.disconnect()

with client:
    client.loop.run_until_complete(login())
