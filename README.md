# Windows için PyInstaller ile build
```
pyinstaller --noconfirm --onefile --console --icon "ta.ico" --name "TurkAnimu" --add-binary "geckodriver.exe;." --add-binary "mpv.exe;." --add-binary "youtube-dl.exe;."  "turkanime.py"
```
