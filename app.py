
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from transcribe import audio_to_text
from summarize import summarize_text, generate_quiz

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 150 * 1024 * 1024  # 150 MB
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Upload folder banao agar nahi hai toh
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # File save karo
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    try:
        # Step 1: Audio to Text
        transcript = audio_to_text(filepath)
        
        # Step 2: Summarize
        summary = summarize_text(transcript)
        
        # Step 3: Generate Quiz
        quiz = generate_quiz(transcript)
        
        return jsonify({
            "transcript": transcript,
            "summary": summary,
            "quiz": quiz
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
