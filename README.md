General Windows10 setup
===
choco install -y chocolatey notepadplusplus.install git.install launchy opera speccy far bitdefenderavfree intellijidea-community python2-x86_32 vcpython27 windowsessentials geforce-experience 7zip.install classic-shell arduino zadig pygtk-all-in-one_win32_py2.7

Install VLC-Win32: http://download.videolan.org/pub/videolan/vlc/2.2.4/win32/vlc-2.2.4-win32.exe

git clone https://github.com/W4RH4WK/Debloat-Windows-10.git

Install Lupa
---
c:\tools\python2-x86_32\Scripts\easy_install.exe dist\lupa-1.3-py2.7-win32.egg


OR build Lupa
---
get lupa-1.3.tar.gz to c:\tools\lupa-1.3
unpack LuaJIT-2.0.4 to c:\tools\lupa-1.3\LuaJIT-2.0.4

via "Visual C+ 2008 32bit command prompt"
c:\tools\lupa-1.3\LuaJIT-2.0.4\src>msvcbuild.bat

https://github.com/chemeris/msinttypes/archive/master.zip
extract msinttypes to C:\tools\lupa-1.3\lupa

c:\tools\lupa-1.3>..\python2-x86_32\python.exe setup.py install

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