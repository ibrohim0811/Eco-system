├── 🤖 bot/                     # Telegram Bot qismi
│   ├── 🔘 buttons/            # Klaviatura va tugmalar
│   ├── ⚙️ handlers/           # Xabarlarni qayta ishlovchilar
│   ├── 🌐 locales/            # Tarjima fayllari (i18n)
│   ├── 🛡️ middlewares/        # Oraliq qatlamlar (auth, lang)
│   └── 🚦 states/             # FSM (Finite State Machine) holatlari
│
├── 🌐 django_app/              # Admin Panel va Ma'lumotlar bazasi
│   ├── 📜 models.py            # Bazadagi jadvallar (User, FAQ va h.k.)
│   ├── 🛡️ admin.py             # Admin panel sozlamalari
│   ├── 🧬 mixins.py            # Qayta ishlatiluvchi kodlar
│   └── 🎨 views.py             # Web interfeys logikasi
│
├── 📂 templates/               # Frontend (HTML) qismi
│   ├── ✨ animations.html
│   ├── 🔐 auth.html
│   └── 👤 user.html
│
├── ⚙️ core/                    # Django loyiha sozlamalari
├── 🛠️ manage.py                # Django boshqaruv fayli
└── 📜 justfile                 # Loyihani ishga tushirish buyruqlari