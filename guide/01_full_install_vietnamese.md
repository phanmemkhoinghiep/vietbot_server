### CÀI ĐẶT VIETBOT TỪ ĐẦU TIÊN

### STEP0. Chuẩn bị Server
0.1. Phần cứng: Nền tảng x86,x64 hoặc arm tùy chọn

0.2. Phần mềm: Ubuntu, debian, armbian hoặc raspbian tùy chọn

0.3. Thông tin hệ thống bao gồm user có quyền sudo, IP local, Public IP

0.4. Python: Python bản 3.11 trở lên

### STEP1. Kết nối Console

1.1. Chờ Hệ thống boot up xong, xác định IP của Server

1.2. Sử dụng các phần mêm SSH như putty/Securec CRT truy cập ssh vào địa chỉ IP của Server, ví dụ

```sh
username: admin
password: 1Qaz@123
```
### STEP2. Cài đặt môi trường

2.1. Nâng cấp gói
Trên console của Pi, sử dụng lần lượt các lệnh sau

```sh
sudo apt-get update
```
Sau khi chạy xong, chạy tiếp
```sh
sudo apt-get upgrade -y
```
2.2. Cài gói cơ bản
```sh
sudo apt-get install nano git -y
```
2.3. Cài đặt Swap 2G (Nếu cần)

```sh
sudo dphys-swapfile swapoff
```

```sh
sudo nano /etc/dphys-swapfile
```
Cửa sổ nano mở ra
Tại dòng 
```sh
CONF_SWAPSIZE=512
```
tăng giá trị 512 thành 2048, sau đó bấm Ctrl + Alt + X để save lại

### STEP3. Download code vietbot

3.6. Download code vietbot từ github

Tại thư mục gốc của user ví dụ 'home/admin' với user admin

Chạy lệnh

```sh
git clone --depth 1 https://github.com/phanmemkhoinghiep/vietbot_offline.git
```
Chờ cho đến khi kết thúc

### STEP4. Cài các gói Python

4.1. Cài các gói phục vụ cho Python

```sh
sudo apt-get install python3 python3-pip python3-venv python3-dev 
```
4.2. Tạo env
```sh
python3 -m venv vietbot_env
```
4.3. Chạy Env (Với Armbian, Debian, Raspbian)
```sh
source vietbot_env/bin/activate
```
Nếu ra dấu nhắc lệnh như sau:
```sh
(vietbot_env) admin@hostname:~ 
```
là thành công

4.4. Chạy Env (Với Windows)
```sh
vietbot_env\Scripts\activate
```
Nếu ra dấu nhắc lệnh như sau:
```sh
(vietbot_env) admin@hostname:~ 
```
là thành công

4.5. Cài đặt toàn bộ các thư viện Python cần thiết 

Trong môi trường evn ở 3.3 hoặc 3.4, gõ
```sh
cd /vietbot_server/src
```
Sau đó gõ tiếp
```sh
pip install -r requirements.txt

```
Chờ đến khi cài đặt hoàn tất


