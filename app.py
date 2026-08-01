from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import tempfile

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download_audio():
    data = request.get_json()
    url = data.get('url') if data else None

    if not url:
        return jsonify({'error': 'URL이 필요합니다.'}), 400

    try:
        temp_dir = tempfile.gettempdir()
        out_pattern = os.path.join(temp_dir, '%(id)s.%(ext)s')

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': out_pattern,
            'quiet': True,
            'no_warnings': True,
            # ★ 유튜브 봇 차단 우회 설정 (모바일 앱 클라이언트로 위장)
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android', 'mweb']
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            file_path = os.path.join(temp_dir, f"{video_id}.mp3")

        if os.path.exists(file_path):
            title = info.get('title', 'audio').replace('/', '_').replace('\\', '_')
            return send_file(
                file_path,
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name=f"{title}.mp3"
            )
        else:
            return jsonify({'error': '파일 변환 실패'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
