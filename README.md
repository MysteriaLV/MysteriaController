General Windows10 setup
===
choco install -y chocolatey notepadplusplus.install git.install launchy opera speccy far bitdefenderavfree intellijidea-community python3 windowsessentials geforce-experience 7zip.install classic-shell arduino zadig vlc

git clone https://github.com/W4RH4WK/Debloat-Windows-10.git

TouchPanel
---
Run Zadig (as Admin?)
Find device with idVendor=0x0eef, idProduct=0x0001
Install/Replace driver with libusb-win32 (original drivers should be removed)


VLC Cache
---
(as admin)
```
C:\Program Files\VideoLAN\VLC\vlc-cache-gen.exe C:\Program Files\VideoLAN\VLC\plugins
```

PotPlayer Config
===
```ini

[OptionList_DISPLAY2]
AttachWindowIndex=2
BroadcastAttachToMain2=0
BroadcastListX=458
BroadcastListY=163
BroadcastToolX=814
BroadcastToolY=163
ChatAttachToMain2=0
ChatTextColor=2236962
ChatWindowVisible=0
ChatX=889
ChatY=163
ControlBoxHeight=227
ControlBoxLeft=889
ControlBoxTop=569
ControlBoxWidth=301
EffectCastOnly=1
EffectPage=0
FullScreenMonitor=2
IsZoomFull=1
LastSkinXmlName=VideoSkin.xml
LastSkinXmlNameVideo=VideoSkin.xml
MainHeight2=819
MainWidth2=1603
MainWindowState=129
MainX=2560
MainY=20
MessageVisible=0
OpenWithSameName=0
PlayListWidth=300
PlayListWindowVisible=1
PlayListX=458
PlayListY=120
RepeatPlay2=2
RestoreLastState=1
SeamlessPlay=2
SkipCastPreview=0
StartScreenSize=5
TopMostWindow0=0
TopMostWindow1=0
TopMostWindow2=0
TopMostWindow3=0
TopMostWindow4=0
TopMostWindow5=0
TopMostWindow6=0
TopMostWindow7=0
TopMostWindow8=0
TopMostWindow9=0
VideoWindowHeight=-1
VideoWindowRectB0=839
VideoWindowRectB1=528
VideoWindowRectB2=796
VideoWindowRectL0=2560
VideoWindowRectL1=458
VideoWindowRectL2=889
VideoWindowRectR0=4163
VideoWindowRectR1=758
VideoWindowRectR2=1190
VideoWindowRectT0=20
VideoWindowRectT1=120
VideoWindowRectT2=569
VideoWindowState1=1
VideoWindowState2=0
VideoWindowWidth=-1
```