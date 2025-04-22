from collections import defaultdict
from lib_process import asyncio, json, threading, os, time, logging, struct, config



from six.moves import queue
from google.cloud import speech

if config["stt"]["mode"] == 'stt_gg_cloud':
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config["stt"]["credential"]

from asyncio import Queue
from paho.mqtt.client import Client as MQTTClient, CallbackAPIVersion

from text_process import text_process
from tts_process import tts_process





if config["logging_type"] =='INFO':
    logging.basicConfig(level=logging.INFO) 
else:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("server_debug.log", encoding='utf-8', mode='a')
        ]
    )       

logger = logging.getLogger("AudioServer")
#Thông tin Broker
MQTT_HOST = config['broker']['host']
MQTT_PORT = config['broker']['port']
MQTT_USER = config['broker']['username']
MQTT_PASS = config['broker']['password']
#Thông tin Client
CLIENT_TOPIC_PREFIX  = config['client']['topic_prefix']
CLIENT_GROUP  = config['client']['group'] 
CLIENT_PUB_MESSAGE_TOPIC=config['client']['pub_message_topic'] 
CLIENT_PUB_AUDIO_TOPIC=config['client']['pub_audio_topic'] 
CLIENT_SUB_AUDIO_TOPIC=config['client']['sub_audio_topic'] 
CLIENT_SUB_MESSAGE_TOPIC=config['client']['sub_message_topic'] 


event_loop = None  # sẽ gán khi khởi động

transcoders = {}

def on_connect(client, userdata, flags, rc, properties=None):
    logger.info("Connected to MQTT Broker with result code %s", rc)
    client.subscribe(f"{CLIENT_TOPIC_PREFIX}/{CLIENT_GROUP}/+/{CLIENT_PUB_MESSAGE_TOPIC}",qos=1)
    client.subscribe(f"{CLIENT_TOPIC_PREFIX}/{CLIENT_GROUP}/+/{CLIENT_PUB_AUDIO_TOPIC}",qos=2)


# Khai báo dictionary lưu số lượng gói theo hw_id
packet_counter = defaultdict(int)  # from collections import defaultdict

def on_message(client, userdata, msg):
    topic = msg.topic
    hw_id = topic.split("/")[2]

    if topic.endswith(f"/{CLIENT_PUB_AUDIO_TOPIC}"):
        packet_counter[hw_id] += 1  # tăng số lượng gói
        logger.info(f"[{hw_id}] Received audio packet #{packet_counter[hw_id]}")
        asyncio.run_coroutine_threadsafe(client_queues[hw_id]["audio"].put(msg.payload), event_loop)

    elif topic.endswith(f"/{CLIENT_PUB_MESSAGE_TOPIC}"):
        payload = msg.payload.decode()
        logger.info(f"{CLIENT_PUB_MESSAGE_TOPIC} {hw_id}: {payload}")

        try:
            state_data = json.loads(payload)
            if state_data.get("state") == "start_send":
                if state_data.get("tts_mode"):
                    config['client']['tts_sending_mode'] = state_data.get("tts_mode")
                logger.info(f"[{hw_id}] Received start_send")
                # Reset packet count when a new stream starts
                packet_counter[hw_id] = 0
                asyncio.run_coroutine_threadsafe(
                    client_queues[hw_id]["audio"].put(payload.encode()), event_loop
                )
            # elif state_data.get("state") == "finish_send":
                # logger.info(f"[{hw_id}] Received finish_send")
                # time.sleep(0.5)  # <-- thêm dòng này
                # if hw_id in transcoders:
                    # transcoders[hw_id].finish()

        except Exception as e:
            logger.warning(f"[{hw_id}] Invalid state payload or not JSON: {e}")
        except asyncio.CancelledError:
            logger.warning(f"[{hw_id}] Cancel")
            # Dọn dẹp tài nguyên ở đây (nếu cần)

           
#Khai báo MQTT

mqtt_client = MQTTClient(callback_api_version=CallbackAPIVersion.VERSION2)
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
mqtt_client.loop_start()
logger.info("MQTT client initialized and loop started")



async def delete_old_files(directory, max_age_days):
    now = time.time()
    cutoff = now - max_age_days * 86400
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            if os.path.getmtime(file_path) < cutoff:
                logger.info(f"Deleting old file: {file_path}")
                os.remove(file_path)

class Transcoder:
    def __init__(self, encoding, hw_id, chunk_size, loop):
        self.buff = queue.Queue()
        self.encoding = encoding
        self.language_code = config['stt']['lang']
        self.rate = config['stt']['rate']
        self.chunk_size = chunk_size
        self.closed = False
        self.transcript = None
        self.hw_id = hw_id
        self.loop = loop
        self.should_stop = False  # <- THÊM BIẾN DỪNG
        self.thread = threading.Thread(target=self.process, daemon=True)
        self.thread.start()

    def finish(self):
        """Gọi khi muốn dừng nhận audio từ bên ngoài (ví dụ: từ on_message)"""
        self.should_stop = True
        self.closed = True
        logger.info(f"[{self.hw_id}] Transcoder finish() called")

    async def async_response_loop(self, responses):
        for response in responses:
            if not response.results:
                continue
            result = response.results[0]
            if not result.alternatives:
                continue
            transcript = result.alternatives[0].transcript
            if result.is_final:
                self.transcript = transcript
                await client_queues[self.hw_id]["request"].put(transcript)
                logger.info(f"[{self.hw_id}] Final transcript: {transcript}")

                mqtt_client.publish(
                    f"{CLIENT_TOPIC_PREFIX}/{CLIENT_GROUP}/{self.hw_id}/{CLIENT_SUB_MESSAGE_TOPIC}",
                    json.dumps({"state": "finish_transcoding", "request": transcript}),
                    qos=0
                )

                self.finish()  # <- DỪNG NHẬN AUDIO KHI CÓ is_final
                break

    def process(self):
        client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=self.encoding,
            sample_rate_hertz=self.rate,
            language_code=self.language_code,
        )
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            single_utterance=True,
            interim_results=False
        )

        try:
            requests = (
                speech.StreamingRecognizeRequest(audio_content=chunk)
                for chunk in self.stream_generator()
            )
            responses = client.streaming_recognize(streaming_config, requests)
            future = asyncio.run_coroutine_threadsafe(
                asyncio.wait_for(self.async_response_loop(responses), timeout=15),
                self.loop
            )
            future.result()
        except asyncio.TimeoutError:
            logger.warning(f"[{self.hw_id}] STT response timed out.")
            mqtt_client.publish(
                f"{CLIENT_TOPIC_PREFIX}/{CLIENT_GROUP}/{self.hw_id}/{CLIENT_SUB_MESSAGE_TOPIC}",
                json.dumps({"state": f"[{self.hw_id}] STT response timed out."}),
                qos=0
            )
        except Exception as e:
            logger.error(f"[{self.hw_id}] Google STT Error with chunk: {self.chunk_size} : {e}")
            mqtt_client.publish(
                f"{CLIENT_TOPIC_PREFIX}/{CLIENT_GROUP}/{self.hw_id}/{CLIENT_SUB_MESSAGE_TOPIC}",
                json.dumps({"state": f"[{self.hw_id}] Google STT Error: {e}"}),
                qos=0
            )
        except asyncio.CancelledError:
            logger.warning(f"[{self.hw_id}] Cancelled")
        finally:
            self.closed = True

    def stream_generator(self):
        bytes_per_second = self.rate * 2  # 16-bit PCM = 2 bytes/sample
        expected_interval = self.chunk_size / bytes_per_second

        while not self.closed:
            if self.should_stop:  # <- DỪNG KHI FLAG ĐƯỢC KÍCH HOẠT
                logger.info(f"[{self.hw_id}] stream_generator stopped by flag")
                return
            try:
                chunk = self.buff.get(timeout=1.0)
                if chunk is None:
                    return
                yield chunk
                # time.sleep(expected_interval)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"[{self.hw_id}] Unexpected error in stream_generator: {e}")
            except asyncio.CancelledError:
                logger.warning(f"[{self.hw_id}] Cancelled")

    def write(self, data):
        self.buff.put(data)


client_queues = defaultdict(lambda: {
    "audio": Queue(),
    "request": Queue(),
    "answer": Queue(),              # ✅ ADD
    "music_file": Queue()           # ✅ ADD (thay vì 'music_link')
})



async def receiver_worker(hw_id):
    buffer = {}
    expected_seq = 0
    seq_wait_start = None
    last_active = time.time()

    while True:
        try:
            if time.time() - last_active > config['client']['session_timeout']:
                logger.info(f"[{hw_id}] Session timeout. Force cleanup.")
                if hw_id in transcoders:
                    transcoders[hw_id].closed = True
                    del transcoders[hw_id]
                buffer.clear()
                expected_seq = 0
                seq_wait_start = None
                last_active = time.time()
                continue

            payload = await client_queues[hw_id]["audio"].get()
            last_active = time.time()

            # ✅ Nếu là message JSON khởi tạo transcoder
            try:
                msg = json.loads(payload.decode())
                if msg.get("state") == "start_send" and "package_size" in msg:
                    package_size = msg["package_size"]
                    logger.info(f"[{hw_id}] Initializing new Transcoder with chunk_size={package_size}")
                    mqtt_client.publish(
                        f"{CLIENT_TOPIC_PREFIX}/{CLIENT_GROUP}/{hw_id}/{CLIENT_SUB_MESSAGE_TOPIC}",
                        json.dumps({"state": f"[{hw_id}] Initializing new Transcoder with chunk_size={package_size}"}),
                        qos=0
                    )
                    if hw_id in transcoders:
                        if not transcoders[hw_id].closed:
                            logger.warning(f"[{hw_id}] Previous transcoder still running.")
                            # ✅ Cập nhật hw_id này vào danh sách hw_id đang transcoding
                            continue
                        else:
                            del transcoders[hw_id]
                    transcoder = Transcoder(
                        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                        hw_id=hw_id,
                        chunk_size=package_size,  # ✅ dùng kích thước do client gửi
                        loop=event_loop
                    )
                    transcoders[hw_id] = transcoder
                    expected_seq = 0
                    seq_wait_start = None
                    buffer.clear()
                    continue
            except Exception:
                pass  # Không phải JSON khởi tạo, tiếp tục xử lý gói audio
            if hw_id not in transcoders:
                logger.warning(f"[{hw_id}] Received audio but have no hardware_id.")
                continue
            if len(payload) < 4:
                logger.warning(f"[{hw_id}] Payload too short")
                continue
            seq = int.from_bytes(payload[:4], byteorder="big")
            audio_data = payload[4:]
            buffer[seq] = audio_data
            logger.info(f"[{hw_id}] Received seq={seq}")
            if seq_wait_start is None:
                seq_wait_start = time.time()
            while expected_seq in buffer:
                transcoders[hw_id].write(buffer[expected_seq])
                del buffer[expected_seq]
                expected_seq += 1
                seq_wait_start = time.time()
            if seq_wait_start and (time.time() - seq_wait_start > config['client']['package_timeout']):
                logger.warning(f"[{hw_id}] Timeout waiting for seq={expected_seq}. Skipping.")
                expected_seq += 1
                seq_wait_start = time.time()
            transcoder = transcoders.get(hw_id)
            if transcoder and transcoder.closed:
                logger.info(f"[{hw_id}] Cleaning up closed transcoder.")
                del transcoders[hw_id]
        except Exception as e:
            logger.exception(f"[{hw_id}] Unexpected error in receiver_worker")
            mqtt_client.publish(
                f"{CLIENT_TOPIC_PREFIX}/{CLIENT_GROUP}/{hw_id}/{CLIENT_SUB_MESSAGE_TOPIC}",
                json.dumps({"state": "error_audio_payload_process"}),
                qos=0
            )
            await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.warning(f"[{hw_id}] Cancel")
            # Dọn dẹp tài nguyên ở đây (nếu cần)  
async def text_worker(hw_id):
    while True:
        transcript = await client_queues[hw_id]["request"].get()
        try:
            logger.info(f"[{hw_id}] Processing transcript")            
            answer, music_file = await asyncio.to_thread(text_process, transcript)
            if answer != '' and music_file == '': # ✅ Chỉ có trả lời dạng text
                await client_queues[hw_id]["answer"].put(answer)
                mqtt_client.publish(
                    f"{CLIENT_TOPIC_PREFIX}/{CLIENT_GROUP}/{hw_id}/{CLIENT_SUB_MESSAGE_TOPIC}",
                    json.dumps({"state": "tts_result","answer":answer})
                    ,qos=0
                )       
            elif answer =='' and music_file !='': # ✅ Chỉ có trả lời dạng music file
                if config['http_interface']['mode'] =='secure':
                    music_link = f"https://{config['address']['public']}:{config['http_interface']['secure_port']}/{music_file}"
                else:
                    music_link = f"http://{config['address']['public']}:{config['http_interface']['port']}/{music_file}"                    
                mqtt_client.publish(
                    f"{CLIENT_TOPIC_PREFIX}/{CLIENT_GROUP}/{hw_id}/{CLIENT_SUB_MESSAGE_TOPIC}",
                    json.dumps({"state": "music_result","music_link":music_link})
                    ,qos=0
                )               
            # Trường hợp 3 (hiếm): Cả hai đều rỗng
            elif answer == '' and music_file == '':
                logger.warning(f"[{hw_id}] Empty result from text_process")
        except Exception as e:
            logger.error(f"[{hw_id}] Text processing error: {e}")
            mqtt_client.publish(
                f"{CLIENT_TOPIC_PREFIX}/{CLIENT_GROUP}/{hw_id}/{CLIENT_SUB_MESSAGE_TOPIC}",
                json.dumps({"state": "error_text_process"})
                ,qos=0
            )
        except asyncio.CancelledError:
            logger.warning(f"[{hw_id}] Cancel")
            # Dọn dẹp tài nguyên ở đây (nếu cần)  

def chunk_pcm_audio(pcm_data: bytes, sample_rate=16000, chunk_duration=0.5) -> list[bytes]:
    """Chia dữ liệu PCM thành các chunk có độ dài chunk_duration (giây)"""
    chunk_size = int(sample_rate * 2 * chunk_duration)  # 2 bytes/sample, mono
    return [pcm_data[i:i+chunk_size] for i in range(0, len(pcm_data), chunk_size)]

async def send_audio_chunks(hw_id, audio_bytes):
    """Gửi các chunk âm thanh PCM trực tiếp đến client và phát bằng player"""
    chunks = chunk_pcm_audio(audio_bytes)
    total_seq = len(chunks)

    # Gửi thông báo bắt đầu gửi kèm số lượng chunk
    total_payload = json.dumps({
        "state": "start_send",
        "total_seq": total_seq
    })
    mqtt_client.publish(f"{CLIENT_TOPIC_PREFIX}/{CLIENT_GROUP}/{hw_id}/CLIENT_SUB_MESSAGE_TOPIC", total_payload,qos=2)

    # Gửi từng chunk PCM
    for seq, pcm_chunk in enumerate(chunks):
        mqtt_client.publish(
            f"{CLIENT_TOPIC_PREFIX}/{CLIENT_GROUP}/{hw_id}/CLIENT_SUB_AUDIO_TOPIC",
            struct.pack(">I", seq) + pcm_chunk
                ,qos=0  # QoS 1: at least once
                )               

    # Gửi thông báo kết thúc
    mmqtt_client.publish(f"{CLIENT_TOPIC_PREFIX}/{CLIENT_GROUP}/{hw_id}/CLIENT_SUB_MESSAGE_TOPIC",
        json.dumps({"state": "finish_send"})
                ,qos=0  # QoS 1: at least once
                )               
    await asyncio.sleep(0)  # Cho coroutine khác cơ hội chạy

  

async def tts_worker(hw_id):
    while True:
        try:
            answer = await client_queues[hw_id]["answer"].get()        
            logger.info(f"[{hw_id}] Get answer from queue: {answer}")
            # Xử lý TTS
            logger.info(f"[{hw_id}] Processing TTS: {answer}")
            if config['client']['tts_sending_mode'] ==1:
                tts_audio = await tts_process(answer,'BYTE',False)
                await send_audio_chunks(hw_id, tts_audio) # Gọi hàm chia nhỏ TTS và gửi lần lượt
            elif config['client']['tts_sending_mode'] ==2:
                tts_audio = await tts_process(answer,'BYTE',False)
                # Gửi toàn bộ âm thanh TTS lên MQTT        
                mqtt_client.publish(
                    f"{CLIENT_TOPIC_PREFIX}/{CLIENT_GROUP}/{hw_id}/{CLIENT_SUB_AUDIO_TOPIC}",
                    tts_audio
                    ,qos=0
                )        
                logger.info(f"[{hw_id}] Published TTS audio.")
            elif config['client']['tts_sending_mode'] ==3:
                tts_file = await tts_process(answer,'FILE',True)
                logger.info(f"[{hw_id}] Public final message...")
                if config['http_interface']['mode'] =='secure':
                    tts_link = f"https://{config['address']['public']}:{config['http_interface']['secure_port']}/{tts_file}"
                else:
                     tts_link = f"http://{config['address']['public']}:{config['http_interface']['port']}/{tts_file}"                   
        except Exception as e:
            logger.error(f"[{hw_id}] Error processing tts: {e}")  # ✅ FIXED: dùng đúng biến
            mqtt_client.publish(
                f"{CLIENT_TOPIC_PREFIX}/{CLIENT_GROUP}/{hw_id}/{CLIENT_SUB_MESSAGE_TOPIC}",
                json.dumps({"state": "error_tts_process"})
                ,qos=0
            )
        except asyncio.CancelledError:
            logger.warning(f"[{hw_id}] Cancel")
            # Dọn dẹp tài nguyên ở đây (nếu cần)  
        await asyncio.sleep(0)

# server_process.py

async def start_audio_server():
    active_hw_ids = set()
    global event_loop
    event_loop = asyncio.get_running_loop()
    while True:
        for hw_id in list(client_queues.keys()):
            if hw_id not in active_hw_ids:
                logger.info(f"[{hw_id}] Starting new client with hardware_id: {hw_id}")
                asyncio.create_task(receiver_worker(hw_id))
                asyncio.create_task(text_worker(hw_id))
                asyncio.create_task(tts_worker(hw_id))
                active_hw_ids.add(hw_id)
        await asyncio.sleep(1)

# Không có if __name__ == "__main__"
# => để script khác gọi: await server_process.main()
