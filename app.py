from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download_audio():
    data = request.get_json()
    url = data.get('url') if data else None

    if not url:
        return jsonify({'error': '유튜브 URL이 필요합니다.'}), 400

    try:
        # 1. 유튜브 봇 차단을 우회하는 파이프라인 API 호출
        cobalt_api = "https://api.cobalt.tools/"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "downloadMode": "audio",
            "audioFormat": "mp3"
        }

        response = requests.post(cobalt_api, json=payload, headers=headers, timeout=30)
        res_data = response.json()

        # 2. 다운로드 가능한 음원 스트림 URL 추출
        download_url = res_data.get('url')
        if not download_url and res_data.get('picker'):
            download_url = res_data['picker'][0].get('url')

        if not download_url:
            return jsonify({'error': '음원을 추출하지 못했습니다. 주소를 확인해주세요.'}), 500

        # 3. 추출된 MP3 바이너리 데이터를 사용자 브라우저로 스트리밍 전송
        audio_stream = requests.get(download_url, stream=True)
        
        return Response(
            audio_stream.iter_content(chunk_size=1024 * 1024),
            content_type='audio/mpeg',
            headers={
                "Content-Disposition": "attachment; filename=voicecure_audio.mp3"
            }
        )

    except Exception as e:
        return jsonify({'error': f"서버 오류: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
