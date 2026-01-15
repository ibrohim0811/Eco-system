# 🌱 EcoLife Platform

EcoLife — bu ekologik muammolarni aniqlash, takliflar yig‘ish va foydalanuvchilarni rag‘batlantirish uchun yaratilgan **Telegram bot + Django web platforma**.

---

## 📂 Loyiha tuzilmasi

```text
├── 🤖 bot/                     # Telegram Bot qismi
│   ├── 🔘 buttons/            # Klaviatura va tugmalar
│   ├── ⚙️ handlers/           # Xabarlarni qayta ishlovchilar
│   ├── 🌐 locales/            # Tarjima fayllari (i18n)
│   ├── 🛡️ middlewares/        # Oraliq qatlamlar (auth, til tanlash)
│   └── 🚦 states/             # FSM (Finite State Machine) holatlari
│
├── 🌐 django_app/              # Django Web ilovasi (Admin + Backend)
│   ├── 📜 models.py            # Ma'lumotlar bazasi modellari
│   ├── 🛡️ admin.py             # Django Admin sozlamalari
│   ├── 🧬 mixins.py            # Qayta ishlatiluvchi yordamchi kodlar
│   └── 🎨 views.py             # Web sahifa logikasi
│
├── 📂 templates/               # Frontend (HTML) shablonlar
│   ├── ✨ animations.html     # Animatsiyalar
│   ├── 🔐 auth.html           # Login / autentifikatsiya
│   └── 👤 user.html           # Foydalanuvchi profili
│
├── ⚙️ core/                    # Django asosiy sozlamalari
├── 🛠️ manage.py                # Django boshqaruv fayli
└── 📜 justfile                 # Loyihani ishga tushirish buyruqlari
