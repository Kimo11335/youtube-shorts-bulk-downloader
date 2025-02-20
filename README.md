<div align='center'>

# YouTube Shorts Bulk Downloader

A Python-based tool for bulk downloading YouTube Shorts videos from specified channels.

<h4> <span> · </span> <a href="https://github.com/Kimo11335/youtube-shorts-bulk-downloader/blob/main/README.md"> Documentation </a> <span> · </span> <a href="https://github.com/Kimo11335/youtube-shorts-bulk-downloader/issues"> Report Bug </a> <span> · </span> <a href="https://github.com/Kimo11335/youtube-shorts-bulk-downloader/issues"> Request Feature </a> </h4>

</div>

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Screenshots](#screenshots)
- [Getting Started](#getting-started)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Security Notes](#security-notes)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🌟 About the Project

This tool allows you to efficiently download YouTube Shorts videos in bulk from specified channels using Python 3.10.0 and above. Perfect for content creators and researchers who need to analyze or archive Shorts content.

### 📸 Screenshots
<div align="center">
<img src="https://cdn.discordapp.com/attachments/1083921622513225818/1175934302320590988/image.png?ex=656d0929&is=655a9429&hm=77a5955511826e443f5a0324e5f5aef968b004a592baf9e454bec2711a84781f&" alt='GUI Screenshot' width='800'/>
</div>

## 🛠️ Getting Started

### Prerequisites
- Python 3.10.0 or higher
- Internet connection
- YouTube account (for cookies)

### Installation
1. Clone the repository:
```bash
git clone https://github.com/Kimo11335/youtube-shorts-bulk-downloader.git
cd youtube-shorts-bulk-downloader
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## 📝 Setup Instructions

### Configure cookies.txt
1. Create a new file named `cookies.txt`
2. Copy your YouTube cookies into this file:
   - Log into YouTube in your browser
   - Use a browser extension like "Cookie-Editor"
   - Export cookies and save them in cookies.txt

### Configure channels.txt
1. Create a new file named `channels.txt`
2. Add YouTube channel URLs, one per line:
```
https://www.youtube.com/@ChannelName/shorts
https://www.youtube.com/@AnotherChannel/shorts
```

## 🎯 Usage

1. Run the application:
```bash
python main.py
```

2. Use the GUI to:
   - Select download directory
   - Choose channels
   - Start downloading
   - Monitor progress

## 🔒 Security Notes
- Never share your cookies.txt file
- Keep your credentials secure
- The .gitignore file protects sensitive data

## ❗ Troubleshooting

If downloads fail:
- Verify your cookies.txt is up to date
- Check your internet connection
- Ensure channel URLs are correct

If GUI doesn't launch:
- Verify Python 3.10.0+ installation
- Check all dependencies are installed
- Run from command line to see error messages

## 🤝 Contributing

We welcome contributions! See `contributing.md` for ways to get started.

<a href="https://github.com/Kimo11335/youtube-shorts-bulk-downloader/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Louis3797/awesome-readme-template" />
</a>

## ⚠️ Disclaimer
This tool is for educational purposes only. Please respect YouTube's terms of service and content creators' rights.