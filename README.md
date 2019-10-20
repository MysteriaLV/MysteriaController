General Windows10 setup
===
choco install -y chocolatey notepadplusplus.install git.install launchy opera speccy far bitdefenderavfree intellijidea-community python3 windowsessentials geforce-experience 7zip.install classic-shell arduino zadig vlc

git clone https://github.com/W4RH4WK/Debloat-Windows-10.git

TouchPanel
---
Run Zadig (as Admin?)
Find device with idVendor=0x0eef, idProduct=0x0001
Install/Replace driver with libusb-win32 (original drivers should be removed)
