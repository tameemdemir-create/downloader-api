from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)  # يسمح لـ GitHub Pages بالاتصال بالسيرفر

@app.route('/extract', methods=['POST'])
def extract_media():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'الرجاء إدخال رابط صحيح'}), 400

    try:
        # إعدادات لطلب الرابط المباشر فقط دون تحميل الفيديو على السيرفر
        ydl_opts = {
            'format': 'best',
            'skip_download': True,
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            download_url = info.get('url')
            title = info.get('title', 'Media File')
            thumbnail = info.get('thumbnail', '')

            return jsonify({
                'success': True,
                'title': title,
                'download_url': download_url,
                'thumbnail': thumbnail
            })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
