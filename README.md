# vietbot_server
This is audio micro service listen streaming request from client, then response with tts_link or music_link
mermaid
sequenceDiagram
    participant Client
    participant Server
    participant STTServer as STT Server
    Client->>Server: "[1] Send message to announce going to send audio\\n{\"state\":\"start_send\", \"package_size\": <size_of_package>}"
    Note right of Server: [2] Ready to receive (Within Server)
    Client->>Server: [3] Send one by one audio package
    Note right of Server: [4] Receive each audio package from Client
    Server->>STTServer: [5] Forward audio package to STT Server

    STTServer-->>Server: [6] Get each transcript from STT Server

    Client->>Server: [8] Continue sending
    Server->>STTServer: [9] Forward audio package to STT Server

    STTServer-->>Server: [10] Get final transcript
    Server-->>Client: [11] Send message back to Client to announce finished transcoding\\n{\"state\":\"finish_transcoding\", \"request\": <transcript>}"
    Note right of Server: [12] Process text from final transcript (Within Server)
    Note right of Server: [13] Create TTS file from answer (Within Server)
    Note right of Server: [14] Create TTS Link, MP3 Link from answer (Within Server)

    Server-->>Client: [15] Send message back to Client with tts link, music link\\n{\"answer\":\"<answer>\", \"tts_link\": <tts_link>, \"music_link\": <music_link>}"
