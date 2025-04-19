# vietbot_server
"This is an audio microservice that listens for streaming requests from all clients via the client topic on the broker, forwards them to the STT server, processes to get the final text, generates the TTS file based on the processed of final text, and responds to the client with the TTS link or music link."
# This is the list of message from Client& Server:
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
