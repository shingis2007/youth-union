# Yoshlar Ittifoqi Bot

TIIAME Yoshlar Ittifoqi uchun Telegram bot (aiogram 3.x). E'lonlar, tadbirlarga
yozilish (RSVP), murojaatlar va kengash a'zolari boshqaruvi bir joyda.

## Imkoniyatlar

**Foydalanuvchi uchun:**
- `/start` — ro'yxatdan o'tish va bosh menyu
- 📅 Tadbirlar ro'yxati va "✅ Qatnashaman" tugmasi orqali ro'yxatdan o'tish
- 📨 Murojaat yuborish
- 👥 Kengash a'zolari bilan (rasm bilan) tanishish

**Admin uchun** (`/admin`):
- 📤 Barcha foydalanuvchilarga e'lon yuborish
- 📅 Yangi tadbir qo'shish
- 📨 Murojaatlarni ko'rish va `/javob_<user_id>` orqali javob berish
- 🙋 Har bir tadbir bo'yicha qatnashuvchilar ro'yxati (telefon raqami bilan)
- 👥 Foydalanuvchilar soni
- ➕ Kengash a'zosini rasm bilan qo'shish / 🗑 o'chirish
- 📊 Umumiy statistika

Ma'lumotlar SQLite bazasida (`bot_database.db`) saqlanadi — hech qanday
tashqi xizmatga bog'liq emas, WAL rejimida ishlaydi va bir nechta
foydalanuvchi bir vaqtda yozsa ham xatoga olib kelmaydi. Har bir handlerda
xatoliklar tutilib log qilinadi (`bot.log`), shu sababli bitta muammoli
xabar butun botni to'xtatib qo'ymaydi.

## O'rnatish (lokal)

```bash
git clone <repo-url>
cd youth_union_bot

python3.11 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# .env faylini ochib BOT_TOKEN va ADMIN_IDS ni to'ldiring
```

> **Eslatma:** Python 3.11 ishlatish tavsiya etiladi — Python 3.13 da
> `pydantic-core` bilan bog'liq muammolar chiqishi mumkin.

`.env` fayli:

```
BOT_TOKEN=123456:AAExampleTokenFromBotFather
ADMIN_IDS=111111111,222222222
DB_PATH=bot_database.db
```

`ADMIN_IDS` — vergul bilan ajratilgan Telegram foydalanuvchi ID lari
(o'zingizning ID ni [@userinfobot](https://t.me/userinfobot) orqali bilib
olishingiz mumkin).

Ishga tushirish:

```bash
python main.py
```

## Docker orqali (istalgan serverga)

```bash
cp .env.example .env   # to'ldiring
docker compose up -d --build
```

Bu usul VPS, DigitalOcean, Hetzner va boshqa har qanday serverda bir xil
ishlaydi — muhit farqidan kelib chiqadigan muammolarni bartaraf qiladi.

## Railway / Render kabi platformalar

`Procfile` allaqachon tayyor (`worker: python main.py`). Platformada
`BOT_TOKEN`, `ADMIN_IDS`, `DB_PATH` environment variable larni kiriting va
deploy qiling. Agar platforma diskni har safar tozalasa (masalan Render
Free), bazani doimiy saqlash uchun persistent disk/volume ulashni unutmang
— aks holda qayta ishga tushganda ma'lumotlar yo'qoladi.

## Loyiha tuzilishi

```
youth_union_bot/
├── main.py            # Bot ishga tushishi, routerlar, global error handler
├── config.py           # .env dan sozlamalarni o'qiydi
├── database.py         # SQLite bilan ishlaydigan async funksiyalar
├── keyboards.py        # Reply/inline klaviaturalar
├── states.py            # FSM holatlari
├── handlers/
│   ├── user.py          # Oddiy foydalanuvchi funksiyalari
│   └── admin.py          # Admin panel funksiyalari
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── Procfile
```

## Eski koddan nima o'zgardi

- Yuklangan admin fayli aslida buzilgan (git-konflikt qoldiqlari, noto'g'ri
  indentatsiya, ikki marta takrorlangan importlar/funksiyalar) edi — to'liq
  tozalab qayta yozildi.
- `database.py` yo'q edi — funksiya nomlariga qarab (`add_tadbir`,
  `get_murojaatlar` va h.k.) to'liq, async, SQLite asosidagi versiyasi
  yozildi. Oldingi JSON/dict asosidagi yechim ehtimoldan ko'ra ma'lumot
  yo'qotish va concurrency muammolariga moyil bo'lardi.
- Foydalanuvchi tomoni (tadbirga yozilish, murojaat yuborish, kengash
  a'zolarini ko'rish) umuman yo'q edi — to'liq qo'shildi.
- Bare `except:` bloklari olib tashlandi, o'rniga `except Exception as e` +
  logging qo'yildi; global error handler qo'shildi — bironta xabar xato
  bersa ham bot yiqilmaydi.
- Statistika bo'limi, Docker/Procfile deploy fayllari qo'shildi.
