General Windows10 setup
===
choco install -y chocolatey notepadplusplus.install git.install launchy opera speccy far bitdefenderavfree intellijidea-community python3 windowsessentials geforce-experience 7zip.install classic-shell arduino zadig vlc

git clone https://github.com/W4RH4WK/Debloat-Windows-10.git

TouchPanel
---
Run Zadig (as Admin?)
Find device with idVendor=0x0eef, idProduct=0x0001
Install/Replace driver with libusb-win32 (original drivers should be removed)

Audio Normalize
---
```asciidoc
ffmpeg-normalize * -of . -v -of normalized -ofmt mp3 -ext mp3 -vn -nt rms -c:a mp3 -t -10 -f
```
VLC Cache
---
(as admin)
```
C:\Program Files\VideoLAN\VLC\vlc-cache-gen.exe C:\Program Files\VideoLAN\VLC\plugins
```

PotPlayer Config
===
```ini
[Settings]
AutoDownloadFile=0
CheckAutoUpdate=0
RestoreLastState=1
StartScreenSize=5
RepeatPlay2=2

[Positions]
IsZoomFull=1
MainWindowState=129
VideoWindowHeight=-1
VideoWindowWidth=-1
```

#### DISPLAY1 (not used, VLC hardcoded position)
```ini
[Positions]
MainX=-1900
MainY=0
```

#### DISPLAY2
```ini
[Positions]
MainX=-768
MainY=0
```

#### DISPLAY3
```ini
[Positions]
MainX=0
MainY=0
```

#### DISPLAY4
```ini
[Positions]
MainX=1280
MainY=0
```

#### DISPLAY5
```ini
[Positions]
MainX=2560
MainY=0
```

#### DISPLAY6
```ini
[Positions]
MainX=3840
MainY=0
```
