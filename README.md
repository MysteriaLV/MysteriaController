General Windows10 setup
===
choco install -y chocolatey notepadplusplus.install git.install launchy opera speccy far bitdefenderavfree pycharm-community  python2-x86_32 vcpython27 windowsessentials vlc geforce-experience 7zip.install classic-shell arduino

git clone https://github.com/W4RH4WK/Debloat-Windows-10.git

Install Lupa
---
c:\tools\python2-x86_32\Scripts\easy_install.exe dist_lupa\lupa-1.3-py2.7-win32.egg


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
