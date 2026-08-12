# NekoDL
>[!IMPORTANT]
>You need to install ffmpeg

## Prerequisites

To fully enjoy NekoDL (audio/video merging, maximum quality on Bilibili, etc.), you need to have **FFmpeg** installed on your system:

- **Windows**: Execute the following PowerShell command as an administrator:  

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
Then, run the following in a PowerShell window as administrator:
```powershell
choco install ffmpeg
```
- **Linux** : ``sudo apt install ffmpeg`` (or the equivalent for your distribution)
- **macOS** : ``brew install ffmpeg``

If FFmpeg is not installed, NekoDL will still work, but in limited mode:
- No audio/video merging
- Potentially reduced quality

## Installation
To install the package you can simply do this:
```bash
pip install nekodl
```

## Update package
To update nekodl you can do:
```bash
pip install --upgrade nekodl
```

## Features & Modules

### Anime-Sama (`nekodl.animesama`)

Full-featured module for searching, downloading anime episodes, manga scans, and resolving embed links from Anime-Sama.

#### Supported Video Hosters / Resolvers:
- **Sibnet** (`video.sibnet.ru` with automatic 302 CDN location resolution)
- **Vidmoly** (`vidmoly.to`, `vidmoly.net`, `vidmoly.me`)
- **SmoothPre / VidHide / StreamWish** (`smoothpre.com`, `vidhide.com`, `vidhidepro.com`, `streamwish.com`, `streamwish.to`)
- **SendVid** (`sendvid.com`)
- **Ansembed / Movembed** (`ansembed.net`, `ansembed.com`)
- **Embed4me / Lplayer** (`embed4me.com`, `lpayer.embed4me.com`, `player.embed4me.com`)
- **Filemoon**, **Vidoza**, **OneUpload**

#### Usage Examples:

```python
from nekodl import animesama

# 1. Search anime in catalog
results = animesama.search_anime("Frieren", limit=5)
print(results)

# 2. Resolve direct video stream from embed URL
stream_info = animesama.resolve_video_url("https://video.sibnet.ru/shell.php?videoid=12345")
print(stream_info["url"])

# 3. Download anime episodes (Sequential or Concurrent)
animesama.download("https://anime-sama.to/catalogue/frieren-no-renri/", season="saison1", episode=1)
animesama.download_many("https://anime-sama.to/catalogue/frieren-no-renri/", max_workers=4)

# 4. Download manga scans
animesama.download_scans("Solo Leveling", chapter=1)
animesama.download_scans_many("Solo Leveling", max_workers=4)
```

## Thanks to: 
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [spotdl](https://github.com/spotDL/spotify-downloader)