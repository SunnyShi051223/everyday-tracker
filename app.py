import webview
import json
import os
import sys
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

# 数据目录：exe/py 所在目录
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    # 打包后的内置文件在 _MEIPASS 临时目录
    BUNDLE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = BASE_DIR

DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
HTML_FILE = os.path.join(BUNDLE_DIR, 'index.html')
PORT = 18080


class Api:
    def get_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def save_settings(self, data):
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True

    def get_data(self, date):
        path = os.path.join(DATA_DIR, f'{date}.json')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def save_data(self, date, data):
        path = os.path.join(DATA_DIR, f'{date}.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True


class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BUNDLE_DIR, **kwargs)

    def log_message(self, format, *args):
        pass  # 静默，不输出请求日志


def start_server():
    server = HTTPServer(('127.0.0.1', PORT), QuietHandler)
    server.serve_forever()


if __name__ == '__main__':
    # 启动本地 HTTP 服务器（后台线程）
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    api = Api()
    window = webview.create_window(
        '每日 Tracker',
        url=f'http://127.0.0.1:{PORT}/index.html',
        js_api=api,
        width=480,
        height=820,
        min_size=(360, 500),
        text_select=True,
    )
    webview.start(debug=False)
