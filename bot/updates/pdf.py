from fpdf import FPDF

def generate_users_pdf(users_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Foydalanuvchilar Ro'yxati", ln=True, align='C')
    pdf.ln(10) # Bo'sh joy

    # Jadval sarlavhasi
    pdf.set_font("Arial", "B", 10)
    pdf.cell(10, 8, "No", 1)
    pdf.cell(30, 8, "TG ID", 1)
    pdf.cell(50, 8, "Username", 1)
    pdf.cell(60, 8, "Ism", 1)
    pdf.cell(40, 8, "Sana", 1)
    pdf.ln()

    # Ma'lumotlarni to'ldirish
    pdf.set_font("Arial", "", 9)
    for idx, user in enumerate(users_data, 1):
        pdf.cell(10, 8, str(idx), 1)
        pdf.cell(30, 8, str(user['telegram_id']), 1)
        pdf.cell(50, 8, str(user['username'] or "N/A"), 1)
        pdf.cell(60, 8, str(user['first_name'][:30]), 1) # Ism juda uzun bo'lsa qirqamiz
        joined_date = user.get('date_joined')
        sana_matni = joined_date.strftime('%Y-%m-%d') if joined_date else "N/A"
        pdf.cell(40, 8, sana_matni, 1)
        pdf.ln()

    file_path = "all_users.pdf"
    pdf.output(file_path)
    return file_path


import sys
import datetime
from fpdf import FPDF

# Terminal xabarlarini saqlash uchun vaqtinchalik xotira
import sys
import os
import datetime
import logging
import asyncio
from fpdf import FPDF
from aiogram import Router, Bot, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile

# --- 1. TERMINAL LOGLARINI TUTISH TIZIMI ---
terminal_logs = []

class TerminalLogger:
    def __init__(self, original_stream):
        self.stream = original_stream

    def write(self, message):
        self.stream.write(message)
        if message.strip():
            # Vaqtni qo'shish va belgilarni tozalash (PDF xato bermasligi uchun)
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            # ASCII bo'lmagan belgilarni (emoji va h.k) olib tashlaymiz
            clean_msg = message.strip().encode('ascii', 'ignore').decode('ascii')
            terminal_logs.append(f"[{timestamp}] {clean_msg}")

    def flush(self):
        self.stream.flush()

# stdout va stderr ni yo'naltirish (Barcha loglarni tutish uchun)
sys.stdout = TerminalLogger(sys.stdout)
sys.stderr = TerminalLogger(sys.stderr)

# Loggingni bizning TerminalLogger orqali o'tadigan qilish
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(levelname)s:%(name)s:%(message)s"
)

# --- 2. ADMIN ROLLERI VA HOLATLARI ---
dp_admin = Router()
ADMIN_IDS = [int(os.getenv("ADMIN_ID", 0))] # .env dan olingan ID

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

class AdminStates(StatesGroup):
    waiting_broadcast_content = State()

# --- 3. PDF GENERATSIYA FUNKSIYALARI ---

def save_terminal_to_pdf():
    """Terminal loglarini qora fonda oq matn qilib PDFga saqlaydi"""
    if not terminal_logs:
        return None

    pdf = FPDF()
    pdf.add_page()
    
    # Qora fon
    pdf.set_fill_color(0, 0, 0)
    pdf.rect(0, 0, 210, 297, 'F')
    
    # Oq matn va terminal shrifti
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Courier", size=8)
    
    pdf.cell(0, 10, txt="--- TERMINAL LOG SESSION ---", ln=True, align='C')
    pdf.ln(5)
    
    y_pos = 20
    # Faqat oxirgi 100 ta qatorni chiqaramiz
    for line in terminal_logs[-100:]:
        if y_pos > 275: # Yangi sahifa
            pdf.add_page()
            pdf.set_fill_color(0, 0, 0)
            pdf.rect(0, 0, 210, 297, 'F')
            y_pos = 10
        
        pdf.cell(0, 5, txt=f"> {line}", ln=True)
        y_pos += 5
    
    file_name = f"logs/terminal_{datetime.datetime.now().strftime('%H%M%S')}.pdf"
    os.makedirs("logs", exist_ok=True)
    pdf.output(file_name)
    return file_name

