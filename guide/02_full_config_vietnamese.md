

### 1.Chuẩn bị

1.1. Cài đặt WinSCP và Notepad ++

1.2. Mở WinSCP, tạo site với Server với username, password đã cài dặt

### 2.Config với file config.json

2.1. Di chuyển WinSCP tới thư mục vietbot_online/src, mở file config.json bằng Notepad ++

2.2. config MQTT
```sh
    "broker": {
        "host": "broker.vietbot.vn",
        "port": 1883,
        "username": "admin",
        "password": "vietbot123"
    },
```
Tại mục này nhập địa chỉ của MQTT, port, username và password tương ứng
Chú ý: tài khoản cho MQTT phải có quyền pub, sub trên các topic_prefix trong mục server & client

2.3. Config Server
```sh
    "server": {
        "topic_prefix": "loapay",
        "group": "dev",
        "name": "voice_gateway",
        "sub_topic": "state",
        "pub_topic": "controll"
    },
```
### Chú ý:
Tại mục này, nhập giá trị đầu tiên topic_prefix của topic cho server, tiếp đó là giá trị của group, giá trị của server_name, giá trị sub_topic là topic mà Server sẽ lắng nghe để cập nhật các biến toàn cục trong bộ nhớ, giá trị pub_topic là topic mà Server sẽ gửi lên toàn bộ giá trị các biến toàn cục trong bộ nhớ

2.4. Config Client
Ta chỉ cần nhập các mục sau:
```sh
    "client": {
        "topic_prefix": "loapay",
        "pub_message_topic": "client_msg",
        "pub_audio_topic": "client_audio",
        "sub_message_topic": "server_msg",
        "group": "dev",
        "package_timeout": 2,
        "session_timeout": 60,
    },
```
Tại mục này, nhập giá trị đầu tiên topic_prefix của topic cho client, tiếp đó là giá trị của group
### Chú ý:
Server sẽ sub tất cả các topic theo giá trị tương ứng trong mục trên, ví dụ với giá trị default thì Server sẽ sub tất cả topic: "loapay/dev/xxxx/client_audio" và sub tất cả các topic "loapay/dev/xxxx/client_msg" với xxxx là hardware_id hoặc 1 tham số phân biệt được client (ví dụ địa chỉ MAC, phần này do code phía client quyết định)
Khi làm việc với từng client, Server sẽ pub lên topic của client theo giá trị tương ứng trong mục trên, ví dụ với giá trị default thì Server sẽ sub lên: "loapay/dev/xxxx/server_msg"

2.5. Config STT
```sh
    "stt": {
        "channels": 1,
        "rate": 16000,
        "mode": "stt_gg_cloud",
        "recognizer_id": "vietbot",
        "ggcloud_project_id": "vietbot_123456",
        "token": "",
        "credential": "google_stt.json",
        "timeout": 6,
        "lang": "vi-VN"
    },
```
Hiện tại Vietbot Server chỉ hỗ trợ Google Cloud STT, do đó tại mục này chúng ta chỉ cần đổi tên "google_stt.json" thành tên file credential của Google Cloud dành cho dịch vụ Google Cloud STT mà chúng ta đã load xuống khi kích hoạt thành công Google Cloud Speech. Các tham số còn lại nên giữ nguyên

### Chú ý:
Có thể đổi giá trị "lang" sang ngôn ngữ khác, nếu muốn dùng Vietbot với ngôn ngữ từ người dùng là ngôn ngữ khác. Mã code của mỗi ngôn ngữ tuân thủ theo chuẩn IETF BCP 47

2.6. Config TTS
```sh
    "tts": {
        "mode": "tts_gg_cloud",
        "voice_name": "female_southern_voice",
        "voice_profile": "",
        "speed": 1.2,
        "rate": 16000,
        "pitch": "",
        "token": "",
        "credential": "google_tts.json",
        "tts_viettel_url": "https://viettelgroup.ai/voice/api/tts/v1/rest/syn",
        "tts_zalo_url": "https://api.zalo.ai/v1/tts/synthesize",
        "tts_fpt_url": "https://api.fpt.ai/hmi/tts/v5",
        "temp_dir": "/tmp/tts",
        "save_dir": "tts",
        "file_age": 7,
```
Trường mode có các giá trị là: 'tts_gg_free' hoặc 'tts_edge' hoặc 'tts_gg_cloud'
Nếu dùng Google Cloud TTS chúng ta cần đổi tên "google_tts.json" thành tên file credential của Google Cloud dành cho dịch vụ Google Cloud TTS mà chúng ta đã load xuống khi kích hoạt thành công Google Cloud Text to Speech.
Có thể chỉnh speed xuống 1.0 hoặc đổi tên thư mục lưu file 'save_dir' nếu cần. Các tham số còn lại nên giữ nguyên
2.7. Skill Timeout
```sh
    "skill": {
        "timeout": 8
    }
```
Nếu trong trường hợp xử lý skill bị lâu thì sau thời gian timeout, ví dụ 8 ở đây là 8s, thì server sẽ phát 1 bản tin thông báo về Client tương ứng, để Client này có thể phát 1 nội dung để người dùng đỡ sốt ruột
2.7. Lưu lại file config.json

### 3.Config với file skill.json

3.1. Di chuyển WinSCP tới thư mục vietbot_online/src, mở file config.json bằng Notepad ++

3.2. Config Gemini

```sh
	"gemini": {
		"error_answer": "Không thực hiện được Gemini, hãy kiểm tra lại",
		"api": "AIzaSyA-fsdfsdfsdf",
		"model": "gemini-2.0-flash",
		"error_answer": "Không sử dụng được chatbot gemini, hãy kiểm tra lại"		
	},
```
Mục api, hãy nhập API của Gemini do trang Google AI Studio cấp
Mục model, hãy chọn model phù hợp
### Chú ý: 
Chọn đúng tên model là text viết liền có gạch nối giữa các từ
3.3. Lưu lại file skill.json
