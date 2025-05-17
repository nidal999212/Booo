# دليل نشر بوت تيليجرام بشكل دائم

هذا الدليل يشرح كيفية نشر بوت تيليجرام لتفعيل الإنترنت المجاني بشكل دائم على خادم.

## خيارات الاستضافة

### 1. PythonAnywhere (موصى به للمبتدئين)

#### الخطوات:
1. قم بإنشاء حساب على [PythonAnywhere](https://www.pythonanywhere.com/)
2. قم بتسجيل الدخول وانتقل إلى لوحة التحكم
3. انقر على "Files" وقم بتحميل ملفات البوت (bot.py وأي ملفات أخرى)
4. انقر على "Consoles" ثم "Bash" لفتح وحدة تحكم
5. قم بتثبيت المكتبات المطلوبة:
   ```
   pip3 install --user python-telegram-bot
   ```
6. انتقل إلى "Tasks" وأضف مهمة جديدة لتشغيل البوت:
   ```
   python3 /home/yourusername/bot.py
   ```
7. اضبط المهمة لتعمل كل دقيقة للتأكد من أن البوت يعمل دائماً

### 2. خادم VPS (للمستخدمين المتقدمين)

#### الخطوات:
1. قم بإنشاء خادم VPS على DigitalOcean أو Linode أو AWS
2. قم بتثبيت Python على الخادم:
   ```
   sudo apt update
   sudo apt install python3 python3-pip
   ```
3. قم بنقل ملفات البوت إلى الخادم باستخدام SCP أو SFTP
4. قم بتثبيت المكتبات المطلوبة:
   ```
   pip3 install python-telegram-bot
   ```
5. قم بإنشاء خدمة systemd لتشغيل البوت تلقائياً:
   ```
   sudo nano /etc/systemd/system/telegrambot.service
   ```
6. أضف المحتوى التالي:
   ```
   [Unit]
   Description=Telegram Bot Service
   After=network.target

   [Service]
   User=yourusername
   WorkingDirectory=/path/to/bot/directory
   ExecStart=/usr/bin/python3 /path/to/bot/directory/bot.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
7. قم بتفعيل وتشغيل الخدمة:
   ```
   sudo systemctl enable telegrambot.service
   sudo systemctl start telegrambot.service
   ```

## تعديلات مهمة على الكود للاستضافة الدائمة

قبل النشر، يُنصح بإجراء التعديلات التالية على الكود:

### 1. إضافة معالجة الأخطاء والمحاولات المتكررة

```python
import time
from telegram.error import NetworkError, Unauthorized

def main() -> None:
    """Start the bot with error handling and retry logic."""
    setup_database()
    
    while True:
        try:
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
            
        except NetworkError:
            # Handle network errors with exponential backoff
            logger.error("Network error occurred. Retrying in 10 seconds...")
            time.sleep(10)
        except Unauthorized:
            # The user has blocked or kicked the bot
            logger.error("The user has blocked or kicked the bot.")
            break
        except Exception as e:
            # Handle other exceptions
            logger.error(f"Error occurred: {e}")
            logger.error("Retrying in 30 seconds...")
            time.sleep(30)
```

### 2. تحسين السجلات لتتبع الأخطاء

```python
import logging
import os
from logging.handlers import RotatingFileHandler

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'bot.log')

# Create a rotating file handler
file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Configure the root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Also log to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)
```

### 3. تأكد من أن قاعدة البيانات تعمل بشكل صحيح

```python
def setup_database():
    """Setup database with error handling."""
    db_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(db_dir, 'user_data.db')
    
    try:
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
        logger.info(f"Database setup successful at {db_path}")
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise
```

## التحقق من حالة البوت

بعد نشر البوت، يمكنك التحقق من حالته باستخدام الأوامر التالية:

### على PythonAnywhere:
- تحقق من سجلات المهام في لوحة التحكم

### على خادم VPS:
```
sudo systemctl status telegrambot.service
journalctl -u telegrambot.service
```

## الصيانة الدورية

للحفاظ على عمل البوت بشكل سليم:

1. تحقق من السجلات بانتظام للكشف عن الأخطاء
2. قم بعمل نسخ احتياطية لقاعدة البيانات بشكل دوري
3. تأكد من تحديث المكتبات عند الحاجة
4. راقب استخدام الموارد (CPU، الذاكرة، القرص) على الخادم

## الدعم والمساعدة

إذا واجهت أي مشاكل في نشر البوت، يمكنك:

1. مراجعة سجلات الأخطاء
2. التحقق من توثيق python-telegram-bot على [الموقع الرسمي](https://python-telegram-bot.readthedocs.io/)
3. البحث عن حلول في منتديات المطورين مثل Stack Overflow
