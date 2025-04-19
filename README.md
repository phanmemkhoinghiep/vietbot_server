# vietbot_server
This is audio micro service listen streaming request from client, then response with tts_link or music_link
Danh mục các bản tin Server và Client gửi cho nhau:
1. Client gửi Server
1.1. Bản tin thông báo chuẩn bị gửi Audio
```sh
{"state":"start_send", "package_size": <size_of_package>}
```
1.2. Bản tin Audio
```sh
seq (4 byte, Audio PCM n byte)
```
2. Server gửi Client
2.1. Bản tin báo đã có kết quả STT
```sh
{"state": "finish_transcoding","request":<transcript>}
```
2.2. Bản tin thông báo chờ xử lý text
```sh
{"state": "wait_text_processing"}
```
2.3. Bản tin thông báo đã kết thúc xử lý text và có câu trả lời
```sh
{"state": "finish_text_process","answer":<answer>}
```
2.3. Bản tin thông báo đã kết thúc quá trình tts, các link tts và music tương ứng
```sh
{"state": "finish_tts_process","answer":<answer>,"answer_link":<link>,"music_link":<link>}
```


```mermaid
sequenceDiagram
    participant Client
    participant Server
    participant STTServer as STT Server
    Client->>Server: [1] Send message to announce going to send audio
    Note right of Server: [2] Ready to receive (Within Server)
    Client->>Server: [3] Send one by one audio package
    Note right of Server: [4] Receive each audio package from Client
    Server->>STTServer: [5] Forward audio package to STT Server

    STTServer-->>Server: [6] Get each transcript from STT Server

    Client->>Server: [8] Continue sending
    Server->>STTServer: [9] Forward audio package to STT Server

    STTServer-->>Server: [10] Get final transcript
    Server-->>Client: [11] Send message back to Client to announce finished transcoding
    Note right of Server: [12] Process text from final transcript (Within Server)
    Note right of Server: [13] Create TTS file from answer (Within Server)
    Note right of Server: [14] Create TTS Link, MP3 Link from answer (Within Server)

    Server-->>Client: [15] Send message back to Client with tts link, music link

