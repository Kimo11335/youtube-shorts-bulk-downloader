# YouTube Shorts Viral Analysis System Flowchart

```mermaid
graph TD
    Start([Start Application]) --> ConfigCheck{API Key Available?}
    ConfigCheck -->|No| KeySetup[API Key Setup]
    KeySetup --> KeySource{Choose Key Storage}
    
    KeySource -->|System Keyring| UseKeyring[Store in System Keyring]
    KeySource -->|Environment Variable| UseEnv[Store in .env File]
    KeySource -->|Local Config| UseLocal[Store in local_config.py]
    
    UseKeyring --> ConfigCheck
    UseEnv --> ConfigCheck
    UseLocal --> ConfigCheck
    
    ConfigCheck -->|Yes| GUI[Launch GUI Interface]
    
    GUI --> AddChannel[Add YouTube Channel]
    GUI --> RemoveChannel[Remove Channel]
    GUI --> SelectFolder[Select Output Folder]
    GUI --> StartAnalysis[Start Analysis Process]
    
    StartAnalysis --> ChannelLoop[For Each Channel]
    ChannelLoop --> GetChannelID[Get Channel ID via YouTube API]
    GetChannelID --> ChannelFound{Channel Found?}
    
    ChannelFound -->|No| ErrorMsg[Display Error Message]
    ErrorMsg --> NextChannel{More Channels?}
    
    ChannelFound -->|Yes| GetVideos[Retrieve Videos from Channel]
    GetVideos --> FilterShorts[Filter for Shorts Videos]
    FilterShorts --> VideoLoop[For Each Short Video]
    
    VideoLoop --> GetDetails[Get Video Details]
    GetDetails --> CalcViralScore[Calculate Viral Score]
    
    CalcViralScore --> AddToList[Add to Video List]
    AddToList --> MoreVideos{More Videos?}
    MoreVideos -->|Yes| VideoLoop
    MoreVideos -->|No| SortVideos[Sort Videos by Viral Score]
    
    SortVideos --> SelectTop[Select Top Videos]
    SelectTop --> SaveMetadata[Save Metadata to JSON]
    
    SaveMetadata --> DownloadLoop[For Each Top Video]
    DownloadLoop --> DownloadVideo[Download Video using yt-dlp]
    DownloadVideo --> UpdateHistory[Update Download History]
    UpdateHistory --> MoreDownloads{More Videos?}
    MoreDownloads -->|Yes| DownloadLoop
    MoreDownloads -->|No| CompleteMsg[Display Completion Message]
    
    CompleteMsg --> NextChannel
    NextChannel -->|Yes| ChannelLoop
    NextChannel -->|No| End([End])
    
    ConfigCheck -.-> APIKeyCheck[API Key Configuration]
    APIKeyCheck --> EnvCheck[Check Environment Variable]
    APIKeyCheck --> KeyringCheck[Check System Keyring]
    APIKeyCheck --> LocalCheck[Check local_config.py]
