import os
import socket
import json
from flask import Flask, request, jsonify, send_from_directory, render_template, make_response
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import qrcode
import io

app = Flask(__name__)

@app.route('/chat-name')
def chat_name():
    return render_template('chat_name.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

# Folder config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IMPORTED_FOLDER = os.path.join(BASE_DIR, 'imported')
CHAT_FILE = os.path.join(BASE_DIR, 'messages.json')

ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'mkv', 'flv', 'wmv', 'webm',
    'mpeg', 'mpg', 'm4v', '3gp', '3g2', 'ts', 'zip', 'mp3', 'srt', 'x', 'xls', 'docx', 'doc',
    'pptx', 'ppt', 'exe', 'apk', 'csv', 'json', 'xml', 'html', 'css', 'js', 'm4a', 'wav',
    'ogg', 'flac', 'aac', 'midi', 'bmp', 'tiff', 'svg', 'webp', 'rar', '7z', 'tar', 'gz',
    'bz2', 'dmg', 'iso', 'psd', 'ai', 'eps', 'indd', 'odt', 'odp', 'ods', 'odg', 'md',
    'log', 'yaml', 'yml', 'conf', 'cfg', 'properties', 'bat', 'sh', 'ps1', 'vbs', 'py', 'rb',
    'go', 'java', 'c', 'cpp', 'h', 'hpp', 'cs', 'rs', 'swift', 'kt', 'dart', 'ts', 'tsx',
    'jsx', 'php', 'asp', 'aspx', 'jsp', 'sql', 'db', 'sqlite', 'mdb', 'accdb', 'bak', 'tmp',
    'torrent', 'epub', 'mobi', 'azw3', 'fb2', 'cbz', 'cbr', 'chm', 'docm', 'dotx', 'dotm',
    'xltx', 'xltm', 'xlam', 'xlsb', 'xltm', 'pptm', 'potx', 'potm', 'ppam'
}

os.makedirs(IMPORTED_FOLDER, exist_ok=True)

# Ensure chat file exists
if not os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, 'w') as f:
        json.dump([], f)

def clear_chat_file():
    with open(CHAT_FILE, 'w') as f:
        json.dump([], f)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    ext = filename.rsplit('.', 1)[-1].lower()
    if ext in ['mp4', 'mov', 'avi', 'mkv', 'flv', 'wmv', 'webm', 'mpeg', 'mpg', 'm4v', '3gp', '3g2', 'ts']:
        return 'video'
    elif ext in ['mp3', 'wav', 'ogg', 'flac', 'aac', 'midi', 'm4a']:
        return 'audio'
    elif ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'svg', 'webp']:
        return 'image'
    elif ext in ['zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'dmg', 'iso']:
        return 'archive'
    elif ext == 'pdf':
        return 'pdf'
    elif ext in ['txt', 'md', 'log', 'csv', 'json', 'xml', 'html', 'css', 'js', 'py', 'java', 'c', 'cpp', 'rb', 'go', 'php', 'sql']:
        return 'document'
    else:
        return 'file'

def list_files_in_folder(folder_path):
    files = []
    for filename in os.listdir(folder_path):
        path = os.path.join(folder_path, filename)
        if os.path.isfile(path):
            size = round(os.path.getsize(path) / (1024 * 1024), 2)  # MB
            modified_time = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M')
            files.append({
                'name': filename,
                'size': size,
                'modified': modified_time,
                'type': get_file_type(filename)
            })
    files.sort(key=lambda x: x['modified'], reverse=True)
    return files

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/qr')
def qr_code():
    ip = get_local_ip()
    url = f"http://{ip}:5000/"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    response = make_response(buf.read())
    response.headers.set('Content-Type', 'image/png')
    return response

@app.route('/imported')
def imported():
    return render_template('imported.html')

@app.route('/imported/files')
def imported_files():
    files = list_files_in_folder(IMPORTED_FOLDER)
    return jsonify(files)

@app.route('/imported/upload', methods=['POST'])
def imported_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(IMPORTED_FOLDER, filename)

        if os.path.exists(save_path):
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{name}_{timestamp}{ext}"
            save_path = os.path.join(IMPORTED_FOLDER, filename)

        try:
            file.save(save_path)
            return jsonify({'message': 'File uploaded', 'filename': filename}), 200
        except Exception as e:
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/imported/files/<filename>', methods=['DELETE'])
def imported_delete(filename):
    safe_name = secure_filename(filename)
    path = os.path.join(IMPORTED_FOLDER, safe_name)
    if os.path.exists(path):
        os.remove(path)
        return jsonify({'message': 'File deleted'}), 200
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/imported/files/<filename>')
def imported_serve_file(filename):
    return send_from_directory(IMPORTED_FOLDER, filename, as_attachment=True)

@app.route("/preview.html")
def preview():
    return render_template("preview.html")

@app.route('/imported/preview/<path:filename>')
def preview_file(filename):
    file_path = os.path.join(IMPORTED_FOLDER, filename)
    if not os.path.isfile(file_path):
        return "File not found", 404
    return render_template('preview.html', filename=filename)

# ✅ Chat message endpoints
@app.route('/chat/send', methods=['POST'])
def send_chat_message():
    data = request.json
    if not data or 'name' not in data or 'msg' not in data:
        return jsonify({'error': 'Invalid'}), 400

    now = datetime.now()
    cutoff = now - timedelta(minutes=3)

    try:
        with open(CHAT_FILE, 'r') as f:
            chat = json.load(f)
    except:
        chat = []

    filtered_chat = []
    for entry in chat:
        try:
            entry_time = datetime.fromisoformat(entry['time'])
            if entry_time >= cutoff:
                filtered_chat.append(entry)
        except Exception:
            # Keep entry if time format fails
            filtered_chat.append(entry)

    new_entry = {
        'name': data['name'],
        'msg': data['msg'],
        'time': now.isoformat()
    }
    if 'replyTo' in data and data['replyTo']:
        new_entry['replyTo'] = data['replyTo']

    filtered_chat.append(new_entry)

    with open(CHAT_FILE, 'w') as f:
        json.dump(filtered_chat[-100:], f)

    return jsonify({'status': 'ok'})

@app.route('/chat/messages')
def get_chat_messages():
    try:
        with open(CHAT_FILE, 'r') as f:
            chat = json.load(f)
    except:
        chat = []
    return jsonify(chat)
# Typing indicator state (in-memory, not persistent)
typing_users = {}

@app.route('/chat/typing', methods=['POST'])
def update_typing():
    data = request.json
    name = data.get("name")
    is_typing = data.get("typing", False)
    if name:
        typing_users[name] = is_typing
    return jsonify({"status": "ok"})

@app.route('/chat/typing')
def get_typing_users():
    # Return list of names currently typing (except yourself)
    self_name = request.args.get("name")
    current_typing = [n for n, v in typing_users.items() if v and n != self_name]
    return jsonify(current_typing)

if __name__ == '__main__':
    clear_chat_file()
    app.run(host='0.0.0.0', port=5000, debug=True)
