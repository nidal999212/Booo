import threading
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
def start_keep_alive():
    keep_alive_thread = threading.Thread(target=keep_alive)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()
