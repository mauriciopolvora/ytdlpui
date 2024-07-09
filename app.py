from flask import Flask, request, render_template, send_file, Response, send_from_directory, abort
from flask_socketio import SocketIO
import yt_dlp
import os
import re 

app = Flask(__name__)
socketio = SocketIO(app)

def my_hook(d, socketid):
    if d['status'] == 'downloading':
        # Use regular expression to extract the numeric part of the progress string
        match = re.search(r'\d+(\.\d+)?%', d['_percent_str'])
        if match:
            percent_value = float(match.group().strip('%'))
            socketio.emit("update progress", percent_value, to=socketid)

def download_video(url, format, socketid):
    # Define a wrapper function for the progress hook that includes socketid
    def progress_hook(d):
        return my_hook(d, socketid)

    ydl_opts = {
        'format': 'bestaudio/best' if format == 'mp3' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'progress_hooks': [progress_hook], 
        'outtmpl': f'%(title)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info_dict)
        if format == 'mp3':
            filename = os.path.splitext(filename)[0] + '.mp3'
        socketio.emit("download complete", filename ,to=socketid)
        return filename

def update_downloads_list(filename):
    print('updating downloads list', filename)
    # Define the path to the text file
    txt_file_path = 'downloaded_files.txt'
    
    # Open the file in append mode, which creates the file if it doesn't exist
    with open(txt_file_path, 'a') as file:
        # Append the new filename followed by a newline
        file.write(filename + '\n')


@app.route("/progress/<socketid>", methods = ["POST", "GET"])
async def handle_request(socketid):
    url = request.form['url']
    format = request.form['format']
    filename = download_video(url, format, socketid)
    update_downloads_list(filename)
    return Response(200)


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        with open('downloaded_files.txt', 'r') as file:
            downloaded_files = file.read().strip().split('\n')
            # Remove any empty strings in case of extra newlines
            downloaded_files = [filename for filename in downloaded_files if filename]
    except FileNotFoundError:
        downloaded_files = []
    return render_template('index.html', downloaded_files=downloaded_files)

@app.route('/static/<filename>')
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)  # Return a 404 not found error if the file does not exist

if __name__ == '__main__':
    socketio.run(app=app, debug=True, host="0.0.0.0", port = 5000)
    
