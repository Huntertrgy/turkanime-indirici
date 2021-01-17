import os
import sys

def dosya(relative_path):
    """ PyInstaller için gömülü dosyaların dizinini getir """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_config():
    """ Kullanıcı klasöründe eğer yoksa TurkAnimu.ini dosyasın oluştur """
    confdir = os.path.join( os.path.expanduser("~"), "TurkAnimu.ini" )
    if not os.path.isfile( confdir ):
        with open(confdir,"w") as f:
            f.write(
            "[TurkAnime]\n"+
            "izlerken kaydet = False\n"+
            "indirilenler = .\n"
            )
    return confdir
