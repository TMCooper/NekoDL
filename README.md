# NekoDL
>[!IMPORTANT]

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