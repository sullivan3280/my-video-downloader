from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('url')
    if not video_url:
        return "Please provide a link!", 400

    # Cloud-friendly settings: Stream directly to RAM instead of saving to disk
    ydl_opts = {
        'format': 'best',
        'outtmpl': '-', # This dash tells yt-dlp to stream the video out
        'logtostderr': True,
    }

    try:
        # We fetch video info first to grab the clean title for the file download
        with yt_dlp.YoutubeDL({'format': 'best'}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            filename = f"{info.get('title', 'video')}.{info.get('ext', 'mp4')}"

        # A quick function to feed the video bytes straight to the browser
        def generate():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

        # This sends it straight down to your device without using server space
        return app.response_class(generate(), mimetype='video/mp4', headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\""
        })
    except Exception as e:
        return f"Error downloading video: {str(e)}", 500

if __name__ == '__main__':
    # Render tells us which port to use via an environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
