from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import urllib.request
import json

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download_audio():
    data = request.get_json()
    url = data.get('url') if data else None

    if not url:
        return jsonify({'error': '유튜브 URL이 필요합니다.'}), 400

    try:
        # 1. 유튜브 봇 차단을 우회하는 외부 통로 호출
        cobalt_api = "https://api.cobalt.tools/"
        payload = json.dumps({
            "url": url,
            "downloadMode": "audio",
            "audioFormat": "mp3"
        }).encode('utf-8')

        req = urllib.request.Request(
            cobalt_api,
            data=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode('utf-8'))

        # 2. 음원 스트림 URL 추출
        download_url = res_data.get('url')
        if not download_url and res_data.get('picker'):
            download_url = res_data['picker'][0].get('url')

        if not download_url:
            return jsonify({'error': '음원을 추출하지 못했습니다. 주소를 확인해주세요.'}), 500

        # 3. 추출된 MP3 바이너리 데이터를 사용자 브라우저로 전송
        audio_req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
        audio_stream = urllib.request.urlopen(audio_req)

        def generate():
            while True:
                chunk = audio_stream.read(1024 * 1024) # 1MB 단위 분할 전송
                if not chunk:
                    break
                yield chunk

        return Response(
            generate(),
            content_type='audio/mpeg',
            headers={
                "Content-Disposition": "attachment; filename=voicecure_audio.mp3"
            }
        )

    except Exception as e:
        return jsonify({'error': f"서버 오류: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
