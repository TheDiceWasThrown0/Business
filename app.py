from flask import Flask, request, jsonify, render_template, redirect, url_for
import threading
import os
from generator import create_liminal_reel
from uploader import upload_to_tiktok, upload_to_instagram

app = Flask(__name__, static_folder='static')

def process_video_generation(theme, webhook_callback=None):
    """
    Runs generation in background (for webhook).
    """
    try:
        print(f"Starting background generation for theme: {theme}")
        create_liminal_reel(theme=theme)
    except Exception as e:
        print(f"Background process failed: {e}")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create():
    theme = request.form.get('theme', 'classic')
    api_key_override = request.form.get('api_key')
    
    if api_key_override:
        os.environ["OPENAI_API_KEY"] = api_key_override

    try:
        # For the web UI, we run synchronously so we can redirect to the result
        # In a production app, we'd use a job queue, but for this "one-button" local tool, this is fine.
        video_filename = create_liminal_reel(theme=theme)
        
        if video_filename:
            return render_template('result.html', video_url=url_for('static', filename=f'output/{video_filename}'))
        else:
            return "Error generating video. Check console logs.", 500
    except Exception as e:
        return f"An error occurred: {e}", 500

@app.route('/generate', methods=['POST'])
def trigger_generation():
    """
    Webhook endpoint for Make.com.
    """
    data = request.json or {}
    theme = data.get("theme", "classic")
    
    thread = threading.Thread(target=process_video_generation, args=(theme,))
    thread.start()
    
    return jsonify({"status": "started", "message": f"Generation started for theme: {theme}"}), 202

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible
    app.run(host='0.0.0.0', port=5001, debug=True)
