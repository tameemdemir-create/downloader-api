from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

@app.route('/extract', methods=['POST'])
def extract_media():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'success': False, 'error': 'الرجاء إدخال رابط صحيح'}), 400

    try:
        # إعدادات ذكية تضمن الحصول على ملف واحد مدمج (صوت وصورة) يعمل على كل الأجهزة
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            download_url = info.get('url')
            title = info.get('title', 'video_download')
            thumbnail = info.get('thumbnail', '')
            ext = info.get('ext', 'mp4')

            # تنظيف اسم الملف من الرموز الغريبة
            safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).rstrip()
            if not safe_title:
                safe_title = "media_file"

            return jsonify({
                'success': True,
                'title': title,
                'safe_title': f"{safe_title}.{ext}",
                'download_url': download_url,
                'thumbnail': thumbnail
            })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# مسار جديد لإجبار المتصفح والهاتف على تحميل الملف فوراً بدل فتحه
@app.route('/download', methods=['GET'])
def proxy_download():
    file_url = request.args.get('url')
    filename = request.args.get('filename', 'video.mp4')
    
    if not file_url:
        return "رابط غير صالح", 400

    try:
        req = requests.get(file_url, stream=True)
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': req.headers.get('Content-Type', 'application/octet-stream')
        }
        return Response(req.iter_content(chunk_size=1024*1024), headers=headers)
    except Exception as e:
        return f"حدث خطأ أثناء التحميل: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
