from lib_process import asyncio, websockets, json, threading, os, global_vars, time
import logging
import ssl
from six.moves import queue
from google.cloud import speech
from link_process import link_process

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'google_tts.json'

#Cau hinh SSL
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(
    certfile='/home/admin/.acme.sh/vietbot.vn_ecc/fullchain.cer',
    keyfile='/home/admin/.acme.sh/vietbot.vn_ecc/vietbot.vn.key'
)

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Lưu trữ client đang hoạt động
active_clients = {}

# Giới hạn số lượng xử lý STT đồng thời
semaphore = asyncio.Semaphore(5)


class Transcoder(object):
    """
    Converts audio chunks to text using Google Cloud Speech-to-Text streaming.
    """
    def __init__(self, encoding, rate, language_code):
        from six.moves import queue
        self.buff = queue.Queue()
        self.encoding = encoding
        self.language_code = language_code
        self.rate = rate
        self.closed = True
        self.transcript = None

    def start(self):
        self.closed = False
        threading.Thread(target=self.process, daemon=True).start()

    def response_loop(self, responses):
        for response in responses:
            if not response.results:
                continue
            result = response.results[0]
            if not result.alternatives:
                continue
            transcript = result.alternatives[0].transcript
            if result.is_final:
                self.transcript = transcript
                break  # Đã xong 1 câu, dừng loop luôn

    def process(self):
        from google.cloud import speech
        client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=self.encoding,
            sample_rate_hertz=self.rate,
            language_code=self.language_code,
        )
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            single_utterance=True,
            interim_results=True
        )

        try:
            requests = (
                speech.StreamingRecognizeRequest(audio_content=chunk)
                for chunk in self.stream_generator()
            )
            responses = client.streaming_recognize(streaming_config, requests)
            self.response_loop(responses)
        except Exception as e:
            print("Google STT Error:", e)
        finally:
            self.closed = True

    def stream_generator(self):
        """
        Generator that yields audio chunks in real time to Google STT
        """
        while not self.closed:
            try:
                chunk = self.buff.get(timeout=1.0)  # Chờ tối đa 1 giây
                if chunk is None:
                    return
                yield chunk  # Gửi từng chunk ngay khi nhận
            except queue.Empty:
                continue  # Không có chunk mới, tiếp tục chờ

    def write(self, data):
        self.buff.put(data)




async def handle_short_tts(websocket):
    await websocket.send(json.dumps({"state": "listening"}))

    transcoder = Transcoder(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        rate=global_vars.DEFAULT_AUDIO_SAMPLE_RATE,
        language_code=global_vars.LANG_CODE
    )
    transcoder.start()

    try:
        while True:
            try:
                data = await websocket.recv()
                if not data:
                    break  # Client đã ngắt
            except websockets.ConnectionClosed:
                logging.info("🔌 WebSocket connection closed")
                break

            # Nếu là gói kết thúc từ client
            if data == b'\x00':
                logging.info("📩 Nhận được tín hiệu kết thúc ghi âm từ client.")
                transcoder.buff.put(None)
                break

            transcoder.write(data)

            # Nếu đã có kết quả STT, phản hồi luôn
            if transcoder.transcript:
                logging.info(f"🗣 Transcription: {transcoder.transcript}")
                answer, tts_link, music_link = await link_process(transcoder.transcript)

                response_data = {
                    "request": transcoder.transcript,
                    "answer": answer,
                    "tts_link": tts_link,
                    "music_link": music_link
                }

                transcoder.transcript = None
                await websocket.send(json.dumps(response_data))
                # Vẫn gửi None để đảm bảo đóng stream trong mọi tình huống
                transcoder.buff.put(None)
                break
    finally:
        transcoder.closed = True
        transcoder.buff.put(None)



async def handle_connection(websocket):
    hw_id = None
    try:
        raw = await websocket.recv()
        data = json.loads(raw)
        hw_id = data.get("hw_id")
        msg_type = data.get("type")

        if not hw_id or msg_type not in ("reconnect", "connect"):
            raise ValueError("Invalid handshake message")

        if hw_id in global_vars.SHORT_AUTHORIZED_HW_IDS:
            client_type = "short"
            await websocket.send(json.dumps({"state": "ID in Short whitelist, Authorized"}))
        else:
            await websocket.send(json.dumps({"error": "Unauthorized"}))
            await websocket.close()
            return

        active_clients[hw_id] = {"websocket": websocket, "type": client_type}
        logging.info(f"✅ Client {hw_id} authorized ({client_type})")

        # Giai đoạn tiếp theo: chờ lệnh "command" để bắt đầu STT
        max_commands = 100  # optional: tránh spam command liên tục
        commands_received = 0

        while commands_received < max_commands:
            raw = await websocket.recv()
            # Nếu là bytes
            if isinstance(raw, bytes):
                if raw == b'\x00':
                    logging.info("📩 Nhận được chuỗi rỗng từ Client, bỏ qua")
                    continue
                else:
                    logging.warning("⚠️ Nhận được bytes không hợp lệ, bỏ qua")
                    continue  # hoặc dùng: break / websocket.close() nếu nghi ngờ tấn công

            # Nếu là text
            try:
                data = json.loads(raw)
                if data.get("type") == "command":
                    commands_received += 1
                    await handle_short_tts(websocket)
            except json.JSONDecodeError:
                logging.warning("⚠️ Dữ liệu JSON không hợp lệ, bỏ qua")
                await websocket.send(json.dumps({"error": "Invalid JSON"}))

        else:
            await websocket.send(json.dumps({"error": "Overquota, please connect/reconnect"}))
            pass

    except websockets.exceptions.ConnectionClosedError as e:
        logging.warning(f"🔌 Client closed unexpectedly: {e}")
    except websockets.exceptions.ConnectionClosedOK as e:
        logging.info(f"👋 Client closed cleanly: {e}")
    except Exception as e:
        logging.error(f"❌ Error with client {hw_id}: {e}")
        try:
            await websocket.send(json.dumps({"error": "Internal server error"}))
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass
        if hw_id:
            active_clients.pop(hw_id, None)



async def server_process():
    logging.info(f"🚀 Starting WebSocket server at ws://{global_vars.ip_address}:{global_vars.socket_port}")
    logging.info(f"🚀 Starting Secure WebSocket server at wss://{global_vars.ip_address}:{global_vars.socket_secure_port}")

    # Tạo 2 server: ws và wss
    ws_server = websockets.serve(
        handle_connection,
        global_vars.ip_address,
        global_vars.socket_port,  # Ví dụ: 21199
        ping_interval=30,
        ping_timeout=10,
        close_timeout=5
    )

    wss_server = websockets.serve(
        handle_connection,
        global_vars.ip_address,
        global_vars.socket_secure_port,  # Ví dụ: 443 hoặc 21200
        ssl=ssl_context,
        ping_interval=30,
        ping_timeout=10,
        close_timeout=5
    )

    # Chạy cả hai song song
    await asyncio.gather(ws_server, wss_server)

if __name__ == "__main__":
    asyncio.run(server_process())
