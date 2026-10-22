from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlparse
import yt_dlp

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        if "/api/search" in path:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            query = query_params.get('q', [''])[0]
            results = []
            if query:
                ydl_opts = {'format': 'bestaudio', 'noplaylist': True, 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        info = ydl.extract_info(f"ytsearch5:{query}", download=False)
                        for entry in info.get('entries', []):
                            results.append({
                                'id': entry.get('id'),
                                'title': entry.get('title'),
                                'duration': entry.get('duration'),
                                'thumbnail': entry.get('thumbnail'),
                                'uploader': entry.get('uploader')
                            })
                    except Exception as e:
                        results = []

            self.wfile.write(json.dumps(results).encode('utf-8'))
            return

        elif "/api/stream" in path:
            video_id = query_params.get('id', [''])[0]
            if not video_id:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing video id")
                return

            url = f"https://www.youtube.com/watch?v={video_id}"
            ydl_opts = {'format': 'bestaudio', 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                    audio_url = info.get('url')
                    self.send_response(302)
                    self.send_header('Location', audio_url)
                    self.end_headers()
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(e).encode('utf-8'))
            return

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Endpoint not found")
