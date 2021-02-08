import os
import sys
from configparser import ConfigParser

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
            "manuel fansub = False\n"+
            "izlerken kaydet = False\n"+
            "indirilenler = .\n"
            )
    return confdir

def add_new_options():
    """ 
    Programın önceki sürümünü kullananların config dosyasına
    eğer mevcut değilse yeni eklenmiş ayarları ekler.
    """
    new_options = ["manuel fansub"]
    parser = ConfigParser()
    parser.read(get_config())
    for i in new_options:
        if not parser.has_option("TurkAnime",i):
            parser.set("TurkAnime",i,"False")
    with open(get_config(),"w") as f:
        parser.write(f)
