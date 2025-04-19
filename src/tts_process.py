import hashlib
from lib_process import texttospeech, logging, os, asyncio, aiofiles

from global_vars import config

# Cấu hình logging
if config["logging_type"] == 'INFO':
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

# Các thông số TTS
SPEED = config["tts"]["speed"] or 1.0
RATE = config["tts"]["rate"] or 16000
PITCH = config["tts"]["pitch"] or 0

# Khởi tạo biến môi trường nếu dùng Google Cloud TTS
if config["tts"]["mode"] == 'tts_gg_cloud':
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config["tts"]["credential"]
    logger.debug(f"GCloud credential path: {os.environ['GOOGLE_APPLICATION_CREDENTIALS']}")

# Hàm xử lý TTS với cache và nhiều mode
async def tts_process(text, re_use):
    file_name = None
    encrypted_file_name = f"{hashlib.md5(text[:90].encode('utf-8')).hexdigest()}.mp3"

    # Định dạng tên file cache theo mode
    mode_prefix_map = {
        'tts_gg_free': 'gg_',
        'tts_edge': 'edge_',
        'tts_gg_cloud': 'ggloud_'
    }

    try:
        prefix = mode_prefix_map.get(config["tts"]["mode"], 'tts_')
        file_name = os.path.join('tts' if re_use else '/tmp', prefix + encrypted_file_name)

        # Kiểm tra file đã tồn tại (dùng lại nếu có)
        if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
            return file_name

        # TTS Google Free
        if config["tts"]["mode"] == 'tts_gg_free':
            from gtts import gTTS
            tts = gTTS(text=text, lang='vi')
            await asyncio.to_thread(tts.save, file_name)
            return file_name

        # TTS Edge
        elif config["tts"]["mode"] == 'tts_edge':
            import edge_tts
            VOICE_MAP = {
                'female_southern_voice': 'vi-VN-HoaiMyNeural',
                'male_southern_voice': 'vi-VN-NamMinhNeural',
            }
            VOICE = VOICE_MAP.get(config["tts"]["voice_name"], 'vi-VN-HoaiMyNeural')
            communicate = edge_tts.Communicate(text, VOICE)
            await communicate.save(file_name)
            return file_name

        # TTS Google Cloud
        elif config["tts"]["mode"] == 'tts_gg_cloud':
            VOICE_MAP = {
                'female_northern_voice': 'vi-VN-Neural2-A',
                'male_northern_voice': 'vi-VN-Neural2-D'
            }
            NAME = VOICE_MAP.get(config["tts"]["voice_name"], 'vi-VN-Wavenet-A')
            client = texttospeech.TextToSpeechClient()
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code='vi-VN', name=NAME
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=SPEED,
                pitch=PITCH,
                sample_rate_hertz=RATE
            )
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            async with aiofiles.open(file_name, "wb") as out:
                await out.write(response.audio_content)
            return file_name

    except Exception as e1:
        logger.info(f"Lỗi: {str(e1)}")
        return ''

# Debug/Test
if __name__ == '__main__':
    import asyncio

    async def main():
        print(await tts_process('Việt Nam', True))
        print(await tts_process('China', False))

    asyncio.run(main())
