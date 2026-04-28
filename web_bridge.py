from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from voice_bridge import VALID_WORDS, connect_arduino, send_to_arduino

HTML_PATH = Path(__file__).with_name("index.html")


def start_web_bridge(host="127.0.0.1", port=8000):
    arduino = connect_arduino()
    if not arduino:
        return

    class BridgeHandler(BaseHTTPRequestHandler):
        status_message = "Ready. Enter a word and click Send."

        def _render_page(self):
            word_list = "".join(f"<li>{w}</li>" for w in VALID_WORDS)
            html = HTML_PATH.read_text(encoding="utf-8")
            html = html.replace("{{STATUS_MESSAGE}}", BridgeHandler.status_message)
            html = html.replace("{{WORD_LIST}}", word_list)
            return html.encode("utf-8")

        def do_GET(self):
            payload = self._render_page()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_POST(self):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            params = parse_qs(body)
            word = params.get("word", [""])[0]
            ok, message = send_to_arduino(arduino, word)
            BridgeHandler.status_message = ("✅ " if ok else "⚠️ ") + message
            print(BridgeHandler.status_message)

            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

    server = HTTPServer((host, port), BridgeHandler)
    print(f"🌐 Web bridge running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Stopping web bridge...")
    finally:
        arduino.close()
        server.server_close()


if __name__ == "__main__":
    start_web_bridge()
