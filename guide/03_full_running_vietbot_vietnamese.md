### Chạy vietbot

### 1. Chạy Manual từ PC

1.1. Kết nối với Server bằng SSH

1.2. Vào ENV bằng lệnh

```sh
source vietbot_env/bin/active
```
1.3. Sau đó di chuyển đến thư mục chứa file start.py
```sh
cd /vietbot_server/src
```
1.4. Chạy file start.py
```sh
python3 start.py
```

### 2. Chạy Manual từ PC có thể tắt PC:

2.1. Cài đặt tmux

```sh
sudo apt-get install tmux
```

2.2. Chạy tmux

```sh
tmux new -s vietbot
```
Cửa sổ tmux cho phiên vietbot_session mở ra, khi đó lặp lại bước 1

2.2. Đóng Tmux

Có thể đóng luôn cửa sổ SSH lại, sau đó có thể tắt PC

2.3. Vào lại phiên tmux

2.3.1 Nếu chỉ có duy nhất 1 session tmux thì gõ"

Kết nối với Server bằng SSH, sau đó gõ lệnh

```sh
tmux attach
```
2.3.2. Nếu có nhiều session tmux cần gõ:
Kết nối với Server bằng SSH, sau đó gõ lệnh

```sh
tmux attach-session -t vietbot
```
### 3. Chạy tự động từ khi boot:

3.1. Soạn thảo file vietbot.service bằng lệnh sau:

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

3.2. Gõ tiếp các lệnh sau:

```sh
sudo systemctl daemon-reload
```

```sh
sudo systemctl enable vietbot.service
```

```sh
sudo systemctl start vietbot.service
```
3.3. Xem trạng thái & Log 

Để xem trạng thái của service, dùng lệnh

```sh
sudo systemctl status vietbot.service
```
Để xem log của service, dùng lệnh

```sh
sudo journalctl -u vietbot.service -f
```
3.3. Cho chạy lại
```sh
sudo systemctl restart vietbot.service
```
3.4. Dừng tạm thời cho đến khi khởi động
```sh
sudo systemctl stop vietbot.service
```
3.5. Vô hiệu hoàn toàn, khởi động lại cũng không chạy
```sh
sudo systemctl disable vietbot.service
```
