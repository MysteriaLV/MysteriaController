General Windows10 setup
===
choco feature enable -n=useRememberedArgumentsForUpgrades

choco install --ForceX86 -y chocolatey notepadplusplus.install git.install launchy opera speccy far bitdefenderavfree intellijidea-community python2 vcpython27 windowsessentials geforce-experience 7zip.install classic-shell arduino zadig vlc

git clone https://github.com/W4RH4WK/Debloat-Windows-10.git

Install Lupa
---
c:\Python27\Scripts\easy_install.exe https://github.com/MysteriaLV/lupa/releases/download/lupa-1.6_luajit-2.0.5_build-49/lupa-1.6-cp27-cp27m-win32.whl

Install AVBin
---
http://avbin.github.io/AVbin/Download.html


COM drivers
---


TouchPanel
---
Run Zadig (as Admin?)
Find device with idVendor=0x0eef, idProduct=0x0001
Install/Replace driver with libusb-win32 (original drivers should be removed)
