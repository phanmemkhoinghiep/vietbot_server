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
    participant Server
    participant STTServer as STT Server

    User->>Client: [1] Wake up Client
    Client->>User: [2] Indicate readiness via LED, LCD, or sound

    Client->>Server: [3] Send message to announce start of audio transmission
    Note right of Server: [4] Server ready to receive

    User->>Client: [5] Speak a voice command
    Note right of Server: [6] Streamed audio is received and split into packages

    Client->>Server: [7] Send audio packages one by one
    Note right of Server: [8] Receive each audio package from Client

    Server->>STTServer: [9] Forward audio package to STT Server
    STTServer-->>Server: [10] Receive partial transcripts

    Client->>Server: [11] Continue sending audio
    Server->>STTServer: [12] Continue forwarding to STT Server

    STTServer-->>Server: [13] Receive final transcript
    Server-->>Client: [14] Notify Client that transcription is complete

    Client->>User: [15] Optionally display the request via LED or console

    Note right of Server: [16] Process final transcript
    Server-->>Client: [17] Optionally notify Client that processing will take longer
    Client->>User: [18] Optionally display delay message via LED, console, or sound

    Server-->>Client: [19] Notify Client that text processing is complete
    Client->>User: [20] Optionally display the answer via LED, console, or sound

    Note right of Server: [21] Generate TTS file from answer
    Note right of Server: [22] Create TTS and music links

    Server-->>Client: [23] Send TTS and music links
    Note right of Client: [24] Playback audio from the provided link

    Client->>User: [25] Output answer via speaker
