

### STEP1. Config vietbot

1.1. Cài đặt WinSCP và Notepad ++

1.2. Mở WinSCP, tạo site với Server với username, password đã cài dặt

1.3. Di chuyển tới thư mục vietbot_online/src, mở file config.json

1.4. config MQTT
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

1.5. Config Server
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

1.6. Config Client
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

1.7. Config STT
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

1.8. Config TTS
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
1.9. Skill Timeout
```sh
    "skill": {
        "timeout": 8
    }
```
Nếu trong trường hợp xử lý skill bị lâu thì sau thời gian timeout, ví dụ 8 ở đây là 8s, thì server sẽ phát 1 bản tin thông báo về Client tương ứng, để Client này có thể phát 1 nội dung để người dùng đỡ sốt ruột

### STEP2. Chạy vietbot

2.1. Chạy Manual từ PC:

Gõ  lệnh sau
```sh
source vietbot_env/bin/active
```

```sh
cd src
```

```sh
python3 start.py
```

2.2. Chạy Manual từ PC có thể tắt PC:

Gõ các lệnh sau

```sh
tmux new-session -s vietbot
```
Cửa sổ tmux cho phiên vietbot_session mở ra, khi đó lặp lại bước 2.1

Sau đó có thể tắt PC

Nếu muốn vào lại, kết nối SSH lại và nếu chỉ có duy nhất 1 session tmux thì gõ"

```sh
tmux attac
```
trong trường hợp có nhiều session tmux cần gõ:
```sh
tmux attach-session -t vietbot
```

2.3. Chạy tự động từ khi boot:

2.3.1 Soạn thảo file vietbot.service bằng lệnh sau:

```sh
sudo nano /etc/systemd/system/vietbot.service
```
Cửa sổ nano mở ra, paste các dòng sau, chú ý có thể thay đổi theo user, ở đây là user admin

```sh
[Unit]
Description=Vietbot
After=network.target

[Service]
User=admin
WorkingDirectory=/admin/pi/vietbot_server/src
ExecStart=/homeadmin/vietbot_env/bin/python /home/admin/vietbot_server/src/start.py
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```
Ấn Ctrl + X sau đó bấm Y để lưu

2.3.2. Gõ tiếp các lệnh sau:

```sh
sudo systemctl daemon-reload
```

```sh
sudo systemctl enable vietbot.service
```

```sh
sudo systemctl start vietbot.service
```
2.3.3. Xem trạng thái & Log 

Để xem trạng thái của service, dùng lệnh

```sh
sudo systemctl status vietbot.service
```
Để xem log của service, dùng lệnh

```sh
sudo journalctl -u vietbot.service -f
```
