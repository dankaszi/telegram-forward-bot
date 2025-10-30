<<<<<<< HEAD
# Telegram Message Forwarder

Ez a program automatikusan továbbítja az üzeneteket egy Telegram csoportból/chatből egy másikba a saját Telegram fiókod használatával.

## Első beállítás

### 1. Hitelesítés (csak egyszer kell)

Először futtatnod kell a `login.py` szkriptet, hogy bejelentkezz a Telegram fiókodba:

```bash
python login.py
```

Ez a szkript:
1. Bekéri a telefonszámodat (már be van állítva a környezeti változókban)
2. Telegram küld egy hitelesítő kódot az applikációdba
3. Add meg ezt a kódot amikor kéri
4. Ha kétlépcsős hitelesítésed van, add meg a jelszavadat is
5. A session file mentésre kerül (`user_session.session`)

### 2. Program futtatása

Miután sikeresen bejelentkeztél, indítsd el a fő programot:

```bash
python main.py
```

A program:
- Automatikusan bejelentkezik a mentett session-nel
- Figyeli a forrás chat-et
- Minden új üzenetet automatikusan továbbít a cél chat-be

## Környezeti változók

A következő környezeti változókra van szükség (már be vannak állítva a Replit Secrets-ben):

- `TELEGRAM_API_ID`: Telegram API azonosító
- `TELEGRAM_API_HASH`: Telegram API hash
- `PHONE_NUMBER`: Telefonszámod (nemzetközi formátumban, pl. +36701234567)
- `SOURCE_CHAT_ID`: Forrás chat azonosítója(k) (ahonnan továbbítasz)
  - **Egy forrás csoport**: Csak add meg a chat ID-t (pl. `-1001713595325`)
  - **Több forrás csoport**: Vesszővel elválasztva add meg őket (pl. `-1001713595325,-1002104945722,-1003456789012`)
- `TARGET_CHAT_ID`: Cél chat azonosítója (ahova továbbítasz)

## Megjegyzések

- Ez a program a **saját Telegram fiókodból** továbbít, nem egy bot-ból
- Ezért hozzáférsz minden olyan chat-hez, ahol tag vagy (beleértve a privát csoportokat is)
- Nem kell admin jogosultság a forrás csoportban
- A cél csoportban kell írási jogosultságod
- A session file biztonságosan tárolja a bejelentkezési adatokat
- Az első bejelentkezés után a program automatikusan fut

## Hibaelhárítás

Ha nem működik az üzenet-továbbítás:
1. Ellenőrizd, hogy tag vagy-e mindkét csoportban
2. Ellenőrizd, hogy van-e írási jogosultságod a cél csoportban
3. Győződj meg róla, hogy a chat ID-k helyesek
4. Futtasd újra a `login.py`-t ha lejárt a session
=======
# telegram-forward-bot
>>>>>>> 66fe948e8eac2bd22df0158276dcb62854edabea
