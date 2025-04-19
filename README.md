# vietbot_server
"This is an audio microservice that listens for streaming requests from all clients via the client topic on the broker, forwards them to the STT server, processes to get the final text, generates the TTS file based on the processed of final text, and responds to the client with the TTS link or music link."
This is the list of message from Client& Server:
1. Client sends to Server
1.1. Message announcing preparation to send Audio
```sh
{"state":"start_send", "package_size": <size_of_package>}
```
1.2. Audio message
```sh
seq (4 byte, Audio PCM n byte)
```
2. Server sends to Client
2.1. Message indicating STT final result is available
```sh
{"state": "finish_transcoding","request":<transcript>}
```
2.2. Message announcing waiting for text processing
```sh
{"state": "wait_text_processing"}
```
2.3. Message announcing text processing is finished and an answer is available
```sh
{"state": "finish_text_process","answer":<answer>}
```
2.4. Message announcing TTS processing is finished, with corresponding TTS and music links
```sh
{"answer":<answer>,"answer_link":<answer_link>,"music_link":<music_link>}
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
    Server-->>Client: [13] Send message back to Client to announce finished text processing
    Note right of Server: [14] Create TTS file from answer (Within Server)
    Note right of Server: [15] Create TTS Link, MP3 Link from answer (Within Server)
    Server-->>Client: [16] Send message back to Client with tts link, music link

