# دليل نشر بوت تيليجرام على منصة Render.com

هذا الدليل يشرح كيفية نشر بوت تيليجرام لتفعيل الإنترنت المجاني على منصة Render.com بشكل دائم ومجاني.

## المتطلبات الأساسية

1. حساب على منصة [Render.com](https://render.com/)
2. حساب على [GitHub](https://github.com/) (اختياري، لكنه مفضل)
3. ملفات البوت المحدثة مع التوكن الجديد

## الملفات المطلوبة للنشر على Render.com

1. **bot.py**: الملف الرئيسي للبوت
2. **requirements.txt**: يحتوي على المكتبات المطلوبة
3. **Procfile**: يحدد كيفية تشغيل البوت

## خطوات النشر على Render.com

### 1. إنشاء مستودع GitHub (اختياري ولكن موصى به)

1. قم بإنشاء مستودع جديد على GitHub
2. قم برفع ملفات البوت إلى المستودع:
   - bot.py
   - requirements.txt
   - Procfile

### 2. إنشاء حساب على Render.com

1. قم بزيارة [Render.com](https://render.com/)
2. انقر على "Sign Up" لإنشاء حساب جديد
3. يمكنك التسجيل باستخدام حساب GitHub أو بريد إلكتروني

### 3. إنشاء خدمة جديدة على Render.com

1. بعد تسجيل الدخول، انقر على "New +" في لوحة التحكم
2. اختر "Web Service"
3. قم بتوصيل مستودع GitHub الخاص بك أو استخدم خيار "Upload Files" لرفع الملفات مباشرة

### 4. تكوين الخدمة

قم بملء المعلومات التالية:
- **Name**: اسم للخدمة (مثل "telegram-internet-bot")
- **Region**: اختر المنطقة الأقرب إليك
- **Branch**: main (إذا كنت تستخدم GitHub)
- **Runtime**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python bot.py`
- **Plan**: Free

### 5. إعدادات متقدمة (اختياري)

يمكنك تكوين المتغيرات البيئية إذا كنت بحاجة إليها، لكن في حالتنا ليست ضرورية لأن التوكن موجود مباشرة في الكود.

### 6. إنشاء الخدمة

انقر على "Create Web Service" لبدء عملية النشر. ستقوم Render.com تلقائياً بتثبيت المكتبات المطلوبة وتشغيل البوت.

## ملاحظات هامة

1. **الخطة المجانية في Render.com**:
   - تتوقف الخدمة بعد 15 دقيقة من عدم النشاط
   - تعود للعمل تلقائياً عند وصول طلب جديد
   - محدودة بـ 750 ساعة تشغيل شهرياً

2. **الحفاظ على استمرارية البوت**:
   - يمكنك إعداد "Health Check" لإبقاء البوت نشطاً
   - استخدم خدمة مثل [UptimeRobot](https://uptimerobot.com/) لإرسال طلبات دورية

3. **قاعدة البيانات**:
   - في الإصدار المجاني من Render.com، قد تفقد البيانات عند إعادة تشغيل الخدمة
   - للحفاظ على البيانات، يمكنك استخدام خدمة قاعدة بيانات خارجية مثل MongoDB Atlas

## تعديلات مقترحة على الكود للعمل بشكل أفضل على Render.com

### 1. إضافة معالجة للحفاظ على الخدمة نشطة

أضف هذا الكود في بداية ملف bot.py:

```python
import threading
import time
import http.server
import socketserver
import os

# إنشاء خادم HTTP بسيط للحفاظ على الخدمة نشطة
def keep_alive():
    PORT = int(os.environ.get('PORT', 8080))
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Bot is running!')
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

# تشغيل الخادم في خيط منفصل
keep_alive_thread = threading.Thread(target=keep_alive)
keep_alive_thread.daemon = True
keep_alive_thread.start()
```

### 2. تعديل معالجة قاعدة البيانات

لتجنب فقدان البيانات عند إعادة تشغيل الخدمة، يمكنك استخدام مسار ثابت لقاعدة البيانات:

```python
def setup_database():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_data.db')
    conn = sqlite3.connect(db_path)
    # باقي الكود...
```

## التحقق من حالة البوت

بعد النشر، يمكنك التحقق من حالة البوت من خلال:

1. لوحة تحكم Render.com: تحقق من سجلات الخدمة للتأكد من أن البوت يعمل بشكل صحيح
2. تيليجرام: تفاعل مع البوت للتأكد من أنه يستجيب للأوامر

## استكشاف الأخطاء وإصلاحها

إذا واجهت مشاكل في تشغيل البوت على Render.com:

1. تحقق من سجلات الخدمة في لوحة تحكم Render.com
2. تأكد من أن جميع المكتبات المطلوبة مدرجة في ملف requirements.txt
3. تأكد من أن الأمر في Procfile صحيح
4. تحقق من أن البوت يعمل محلياً قبل النشر
