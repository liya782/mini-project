import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from utils import predict_audio

app = Flask(__name__)
# Configurations
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max limit
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')
                
@app.route('/analyze')
def analyze():
    return render_template('analyze.html')

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
        
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Handle blob files from recorder usually sent without clear filename or standard extension
        if filename == 'blob':
            filename = 'recording.webm'
            
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Pass file to prediction pipeline
        result = predict_audio(filepath)
        
        # Optional: clean up file after analysis or keep for history (keeping for now to show on results)
        
        if "error" in result:
            return jsonify({'error': result['error']}), 500
            
        return jsonify(result), 200
        
    return jsonify({'error': 'Invalid file type. Please upload a valid audio format (wav, mp3, webm).'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
