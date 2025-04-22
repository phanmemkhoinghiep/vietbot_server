from quart import Quart, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from lib_process import asyncio, json, os, ssl, uuid, config
from tts_process import tts_process



# Cau hinh SSL
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(
    certfile='/home/admin/.acme.sh/vietbot.vn_ecc/fullchain.cer',
    keyfile='/home/admin/.acme.sh/vietbot.vn_ecc/vietbot.vn.key'
)

app = Quart(__name__, template_folder='templates')

# Cấu hình thư mục upload cho file mp3
MP3_FOLDER = os.path.join(os.getcwd(), 'mp3')
TTS_FOLDER = os.path.join(os.getcwd(), 'tts')
# Chắc chắn rằng thư mục TTS, MP3 được cấu hình, nếu chưa tồn tại thì tạo mới
os.makedirs(TTS_FOLDER, exist_ok=True)
os.makedirs(MP3_FOLDER, exist_ok=True)
app.config['MP3_FOLDER'] = MP3_FOLDER
app.config['TTS_FOLDER'] = TTS_FOLDER


# @app.route('/')
# async def index():
    # files = [f for f in os.listdir(app.config['MP3_FOLDER']) if f.endswith('.mp3')]
    # return await render_template('upload.html', files=files)



# @app.route('/upload', methods=['POST'])

# # Route phục vụ upload file mp3

# @app.route('/upload', methods=['POST'])
# async def upload_file():
    # try:
        # files = await request.files
        # if 'file' not in files:
            # return jsonify({"state": "Failed", "error": "No file part in request"}), 400

        # file = files['file']
        # if file.filename == '':
            # return jsonify({"state": "Failed", "error": "No selected file"}), 400

        # filename = secure_filename(file.filename)
        # if not filename.lower().endswith('.mp3'):
            # return jsonify({"state": "Failed", "error": "Only .mp3 files are allowed"}), 400

        # save_path = os.path.join(app.config['MP3_FOLDER'], filename)
        # await file.save(save_path)

        # # Cập nhật lại danh sách file sau khi upload
        # files = [f for f in os.listdir(app.config['MP3_FOLDER']) if f.endswith('.mp3')]
        # return await render_template('upload.html', files=files)

    # except Exception as e:
        # return jsonify({"state": "Failed", "error": str(e)})


# Route phục vụ client truy xuất file mp3 đã upload
@app.route('/mp3/<path:filename>', methods=['GET'])
async def get_mp3(filename):
    try:
        file_path = os.path.join(app.config['MP3_FOLDER'], filename)
        if not os.path.abspath(file_path).startswith(os.path.abspath(app.config['MP3_FOLDER'])):
            return {"error": "File access denied"}, 403
        return await send_from_directory(app.config['MP3_FOLDER'], filename)
    except FileNotFoundError:
        return {"error": "File not found"}, 404

# @app.route('/generate-tts', methods=['POST'])
# async def generate_tts():
    # try:
        # form = await request.form
        # text = form.get("tts_text", "").strip()
        # if not text:
            # return jsonify({"state": "Failed", "error": "No text provided"}), 400

        # # Gọi hàm tts_process để tạo file TTS (hãy đảm bảo rằng hàm tts_process nhận tham số (text, flag) và trả về đường dẫn file)
        # tts_file = await tts_process(text, True)
        # # Lấy tên file từ đường dẫn trả về
        # filename = os.path.basename(tts_file)
        # # Xây dựng đường link truy cập file dựa vào public IP và port từ global_vars
        # tts_link f"https://{config['address']['public']}:{config['http_interface']['secure_port']}/tts/{filename}"
        
        # return jsonify({
            # "state": "Success",
            # "file_url": tts_link
        # })

    # except Exception as e:
        # return jsonify({"state": "Failed", "error": str(e)})


# Route phục vụ client truy xuất file tts đã tạo ra
@app.route('/tts/<path:filename>', methods=['GET'])
async def get_tts(filename):
    try:
        file_path = os.path.join(app.config['TTS_FOLDER'], filename)
        if not os.path.abspath(file_path).startswith(os.path.abspath(app.config['TTS_FOLDER'])):
            return {"error": "File access denied"}, 403
        return await send_from_directory(app.config['TTS_FOLDER'], filename)
    except FileNotFoundError:
        return {"error": "File not found"}, 404



# @app.route('/api', methods=['POST'])
# async def post_process():
    # try:
        # payload = await request.get_json()
        # return jsonify({'state': 'Failed', 'response': 'chưa mở khóa tính năng này'})
    # except Exception as e:
        # return jsonify({'state': 'Failed', 'error': str(e)})


if __name__ == '__main__':
    print("Starting API Server directly...")
    # asyncio.run(app.run_task(host=config['address']['local'], port=config['http_interface']['port']))
    asyncio.run(app.run_task(host=config['address']['local'], port=config['http_interface']['secure_port'], ssl=ssl_context))

# if __name__ == '__main__':
    # print("Starting both HTTP and HTTPS servers...")

    # async def start_servers():
        # # Server HTTP
        # task_http = asyncio.create_task(
            # app.run_task(host=config['address']['local'], port=config['http_interface']['port'])
        # )

        # # Server HTTPS
        # task_https = asyncio.create_task(
            # app.run_task(host=config['address']['local'], port=config['http_interface']['secure_port'], ssl=ssl_context)
        # )

        # await asyncio.gather(task_http, task_https)

    # asyncio.run(start_servers()) 
