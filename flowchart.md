# YouTube Shorts Viral Analysis Flowchart

```mermaid
flowchart TD
    A[Start] --> B[Enter YouTube Channel Name]
    B --> C[Get Channel ID via YouTube API]
    
    C --> D{Channel Found?}
    D -->|No| E[Display Error Message]
    E --> Z[End]
    
    D -->|Yes| F[Retrieve Videos from Channel]
    F --> G[Filter for Shorts Videos]
    G --> H[For Each Short Video]
    
    H --> I[Get Video Details]
    I --> J[Calculate Viral Score]
    J --> K[Add to List]
    K --> L{More Videos?}
    L -->|Yes| H
    
    L -->|No| M[Sort Videos by Viral Score]
    M --> N[Select Top 50 Videos]
    N --> O[Save Metadata to JSON]
    
    O --> P[For Each Top Video]
    P --> Q[Download Video using yt-dlp]
    Q --> R{More Videos?}
    R -->|Yes| P
    
    R -->|No| S[Display Completion Message]
    S --> Z
    
    subgraph "Viral Score Calculation"
    J1[Views per Day × 0.6]
    J2[Likes-to-Views Ratio × 0.2]
    J3[Comments-to-Views Ratio × 0.2]
    J1 & J2 & J3 --> J4[Sum Components]
    J4 --> J
    end
```

## Process Description

1. **Input**: User enters a YouTube channel name
2. **Channel Identification**: System retrieves the channel ID using YouTube API
3. **Video Collection**: System fetches all videos from the channel
4. **Shorts Filtering**: Only videos under 60 seconds are considered Shorts
5. **Metrics Analysis**: For each Short, the system collects:
   - View count
   - Like count
   - Comment count
   - Upload date
   - Duration
6. **Viral Score Calculation**: Each video receives a score based on:
   - Views per day (60% weight)
   - Like-to-view ratio (20% weight)
   - Comment-to-view ratio (20% weight)
7. **Ranking**: Videos are sorted by viral score
8. **Selection**: Top 50 videos are selected
9. **Metadata Storage**: Video details are saved to a JSON file
10. **Download**: Selected videos are downloaded using yt-dlp
11. **Completion**: User is notified when the process is complete