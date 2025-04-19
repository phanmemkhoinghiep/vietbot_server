### The entire process of installing, configuring, and running Vietbot is illustrated in the following flowchart.

```mermaid
sequenceDiagram
    participant User
    participant SystemOS as System OS
    participant ENV
    participant Vietbot

    Note right of User: [1] Prepare user information
    User->>SystemOS: [2] Create sudo user and set password
    Note right of SystemOS: [3] Assign username, password, and home directory

    User->>SystemOS: [4] Request to download Vietbot repo from GitHub
    Note right of SystemOS: [5] Downloading repository
    SystemOS->>User: [6] Notify when download completes

    Note right of User: [7] Prepare virtual environment
    User->>ENV: [8] Create virtual environment with given name
    Note right of ENV: [9] Assign ENV name, create directory, and copy files
    ENV->>User: [10] Virtual environment created successfully

    Note right of User: [11] Install Python libraries
    User->>ENV: [12] Install libraries using `requirements.txt` from Vietbot repo
    Note right of ENV: [13] Installing libraries into ENV directory
    ENV->>User: [14] Notify when installation is complete

    Note right of User: [15] Configure Vietbot
    User->>SystemOS: [16] Open and edit Vietbot config file
    Note right of SystemOS: [17] Saving config file
    SystemOS->>User: [18] Config file saved successfully

    User->>SystemOS: [19] Open and edit Vietbot skill file
    SystemOS->>User: [20] Skill file saved successfully

    Note right of User: [21] Run Vietbot
    User->>ENV: [22] Start Vietbot
    Note right of ENV: [23] Loading libraries and initializing
    ENV->>User: [24] Notify when Vietbot is ready
    Vietbot->>User: [25] Show logs during runtime
