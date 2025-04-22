# vietbot_server
"This is an audio microservice that listens for streaming requests from all clients via the client topic on the broker, forwards them to the STT server, processes to get the final text, generates the TTS file based on the processed of final text, and responds to the client with the TTS link or music link."
Luồng xử lý dữ liệu âm thanh và văn bản trong hệ thống này diễn ra theo các bước chính sau:
•
Tiếp nhận Dữ liệu Âm thanh:
◦
Hệ thống lắng nghe dữ liệu âm thanh được gửi đến thông qua giao thức MQTT
.
◦
Dữ liệu âm thanh từ các client được publish lên các topic MQTT cụ thể, theo định dạng: {CLIENT_TOPIC_PREFIX}/{CLIENT_GROUP}/{hw_id}/{CLIENT_PUB_AUDIO_TOPIC}
. Trong đó, hw_id là định danh của thiết bị client.
◦
Hàm on_message sẽ được gọi khi có tin nhắn mới trên các topic đã subscribe
. Khi nhận được gói tin âm thanh, số lượng gói tin cho hw_id tương ứng sẽ được tăng lên và thông tin này được log lại
.
◦
Payload của tin nhắn âm thanh sẽ được đặt vào hàng đợi (queue) audio thuộc client_queues[hw_id] để xử lý tiếp
.
•
Xử lý Gói tin Âm thanh (receiver_worker):
◦
Coroutine receiver_worker liên tục lấy dữ liệu âm thanh từ hàng đợi client_queues[hw_id]["audio"]
.
◦
Khi bắt đầu phiên gửi âm thanh mới, client có thể gửi một tin nhắn JSON chứa thông tin package_size (kích thước chunk âm thanh)
. Nếu nhận được tin nhắn này, một instance của class Transcoder sẽ được khởi tạo cho hw_id tương ứng
.
◦
Các gói tin âm thanh được nhận sau đó (không phải là JSON khởi tạo) được kiểm tra độ dài và số sequence
. Hệ thống sẽ cố gắng sắp xếp lại các gói tin dựa trên số sequence và đưa dữ liệu âm thanh đã sắp xếp vào buffer của Transcoder thông qua phương thức write
.
◦
Coroutine này cũng giám sát thời gian timeout nếu không nhận được gói tin tiếp theo trong khoảng thời gian cấu hình
.
◦
Nếu Transcoder bị đóng (transcoder.closed là True), tài nguyên liên quan đến hw_id này sẽ được dọn dẹp
.
•
Chuyển đổi Âm thanh thành Văn bản (Transcoder):
◦
Class Transcoder chịu trách nhiệm chuyển đổi luồng âm thanh thành văn bản bằng cách sử dụng Google Cloud Speech-to-Text API nếu cấu hình stt_gg_cloud được kích hoạt
.
◦
Phương thức process của Transcoder chạy trong một thread riêng
. Nó lấy các chunk âm thanh từ buffer thông qua stream_generator và gửi chúng đến API của Google Cloud Speech
.
◦
async_response_loop xử lý các phản hồi từ API. Khi nhận được một transcript cuối cùng (result.is_final), transcript này sẽ được đặt vào hàng đợi request thuộc client_queues[self.hw_id] để xử lý văn bản tiếp theo
. Đồng thời, một tin nhắn MQTT thông báo hoàn thành việc chuyển mã và nội dung transcript cũng được publish. Quá trình nhận âm thanh của Transcoder sẽ dừng lại khi có transcript cuối cùng
.
•
Xử lý Văn bản (text_worker):
◦
Coroutine text_worker liên tục lấy transcript từ hàng đợi client_queues[hw_id]["request"]
.
◦
Nó gọi hàm text_process (được import từ text_process.py) để xử lý transcript
. Hàm này có thể trả về một đoạn văn bản trả lời (answer) và/hoặc một đường dẫn đến file nhạc (music_file).
◦
Dựa trên kết quả trả về từ text_process:
▪
Nếu chỉ có answer (dạng text), nó sẽ được đặt vào hàng đợi answer thuộc client_queues[hw_id] và một tin nhắn MQTT chứa kết quả TTS (tts_result) sẽ được publish
.
▪
Nếu chỉ có music_file, một đường dẫn music_link sẽ được tạo dựa trên cấu hình giao diện HTTP (secure hoặc non-secure) và publish qua MQTT với state là music_result
.
▪
Trường hợp cả hai đều rỗng, một cảnh báo sẽ được log
.
▪
Nếu có lỗi trong quá trình xử lý văn bản, một tin nhắn MQTT thông báo lỗi (error_text_process) sẽ được publish
.
•
Chuyển đổi Văn bản thành Âm thanh (tts_worker):
◦
Coroutine tts_worker liên tục lấy văn bản trả lời từ hàng đợi client_queues[hw_id]["answer"]
.
◦
Nó gọi hàm tts_process (được import từ tts_process.py) để chuyển văn bản thành dữ liệu âm thanh (BYTE) hoặc tạo file âm thanh (FILE)
.
◦
Cách thức gửi âm thanh TTS về client phụ thuộc vào cấu hình tts_sending_mode:
▪
Nếu là 1, dữ liệu âm thanh TTS sẽ được chia thành các chunk nhỏ bằng hàm chunk_pcm_audio và gửi tuần tự về client thông qua topic CLIENT_SUB_AUDIO_TOPIC. Thông báo bắt đầu và kết thúc gửi cũng được publish
.
▪
Nếu là 2, toàn bộ dữ liệu âm thanh TTS sẽ được gửi một lần qua topic CLIENT_SUB_AUDIO_TOPIC
.
▪
Nếu là 3, một đường dẫn tts_link đến file âm thanh TTS sẽ được tạo và publish qua MQTT
.
◦
Nếu có lỗi trong quá trình xử lý TTS, một tin nhắn MQTT thông báo lỗi (error_tts_process) sẽ được publish
.
•
Khởi tạo và Quản lý Workers (start_audio_server):
◦
Hàm start_audio_server chạy một vòng lặp vô hạn để kiểm tra các hw_id mới xuất hiện trong client_queues
.
◦
Đối với mỗi hw_id mới, nó sẽ tạo ra các asyncio task cho receiver_worker, text_worker, và tts_worker để xử lý dữ liệu cho client đó một cách độc lập
.
Tóm lại, luồng xử lý dữ liệu bắt đầu bằng việc nhận âm thanh qua MQTT, sau đó âm thanh được chuyển đổi thành văn bản bằng Google Cloud STT. Văn bản này tiếp tục được xử lý để tạo ra phản hồi (văn bản hoặc đường dẫn nhạc). Cuối cùng, văn bản phản hồi có thể được chuyển đổi thành âm thanh (TTS) và gửi lại cho client theo nhiều phương thức khác nhau thông qua MQTT. Các hàng đợi (client_queues) đóng vai trò trung gian để truyền dữ liệu giữa các bước xử lý khác nhau, đảm bảo tính bất đồng bộ của hệ thống.
# This is the list of message from Client& Server:
1. Client sends to Server
   
1.1. Message announcing client preparation to send Audio
```sh
{"state":"start_send", "package_size": <size_of_package>,"tts_mode":<tts_mode>}
```
```sh
"Mode 1: TTS content is splited then send over MQTT
Mode 2: Whole TTS content is send over MQTT
Mode 3: Send directly to TTS file
```
1.2. Audio message
```sh
seq 4 byte, Audio PCM n byte
```
1.3. Finish sending
```sh
{"state":"finish_send"}
```
2. Server sends to Client
   
2.1. Message indicating STT final result is available
```sh
{"state": "finish_transcoding","request":<transcript>}
```
2.2. Message announcing text processing is finished and an answer is available, answer is tts only
```sh
{"state": "tts_result","answer":answer}
```
#Mode 1: TTS content is splited then send over MQTT

2.2.1. Message announcing client preparation to send Audio
```sh
{"state": "start_send","package_number":<package_number>}
```
2.2.2. Audio message
```sh
seq 4 byte, Audio PCM n byte
```
2.2.3. Finish sending
```sh
{"state":"finish_send",}
```
#Mode 2: TTS content send over MQTT

2.2.1. Audio message
```sh
Audio PCM n byte
```
#Mode 3: 
2.2.1. Json Message
{"state": "tts_result","tts_link"<tts_link>}

2.2. Message announcing text processing is finished and an answer is available, answer is music link only
```sh
{"state": "music_result","music_link":<music_link>}
```

# This is the diagram

```mermaid
%% Arrows:
%% ->>  : request / action
%% -->> : response / async result

sequenceDiagram
    participant User
    participant Client
    participant Broker
    participant Server
    participant STTServer as STT Server
    User->>Client: [1] Wake up Client
    Client->>User: [2] Indicate readiness via LED, LCD, or sound

    Client->>Broker: [3] Publish message: start of audio transmission
    Server->>Broker: [4] Subscribe to topic for incoming audio
    Broker-->>Server: [5] Deliver start message to Server
    Note right of Server: [6] Server ready to receive audio

    User->>Client: [7] Speak a voice command
    Note right of Client: [8] Capture and stream audio

    Client->>Broker: [9] Publish audio packages one by one
    Broker-->>Server: [10] Deliver each audio package to Server
    Note right of Server: [11] Receive and handle each audio package

    Server->>STTServer: [12] Forward audio package to STT Server
    STTServer-->>Server: [13] Receive partial transcript

    Client->>Broker: [14] Continue publishing audio
    Broker-->>Server: [15] Deliver more audio to Server
    Server->>STTServer: [16] Forward more audio to STT Server
    STTServer-->>Server: [17] Receive final transcript

    Server->>Broker: [18] Publish message: transcription complete
    Broker-->>Client: [19] Deliver transcription complete message
    Client->>User: [20] Optionally display transcript via LED or console

    Note right of Server: [21] Process final transcript
    Server->>Broker: [22] Optionally publish: processing will take longer
    Broker-->>Client: [23] Deliver long-processing notification
    Client->>User: [24] Optionally notify via LED, console, or sound

    Server->>Broker: [25] Publish message: text processing complete
    Broker-->>Client: [26] Deliver text processing result
    Client->>User: [27] Optionally display the answer via LED, console, or sound

    Note right of Server: [28] Generate TTS file and music link
    Server->>Broker: [29] Publish TTS and music links
    Broker-->>Client: [30] Deliver message with links to Client
    Note right of Client: [31] Playback link
    Client->>User: [32] Sound Announcement via speaker
