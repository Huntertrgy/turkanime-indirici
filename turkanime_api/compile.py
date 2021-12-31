from os import path,replace,mkdir
import sys
from configparser import ConfigParser
from rich.progress import Progress

ROOT = path.join( path.expanduser("~"), "TurkAnimu" )

def dosya(hedef,testing=False):
    """ Binary'lerin path'larını getir. """
    result = path.join(ROOT,hedef)
    if testing and not path.isfile(result):
        fancy = Progress()
        fancy.console.log(f"{hedef} dosyası silinmiş ya da taşınmış, düzeltmek için lütfen uygulamayı yeniden başlatın.")
        input("[[Uygulamayı kapatmak için ENTER'a basın]]")
        exit(1)
    return result

def dosya_init():
    """ Yazılımın config dosyasını ve binary dizinini teyit et """
    if not path.isdir(ROOT):
        mkdir(ROOT)

    # Eski sürümü kullananların config dosyasını yeni dizin Belgelerim/TurkAnimu'ya taşı
    oldpath = path.join( path.expanduser("~"), "TurkAnimu.ini" )
    newpath = path.join( ROOT, "TurkAnimu.ini" )
    if path.isfile(oldpath):
        replace(oldpath,newpath)

    # Eğer yoksa belgelerim/TurkAnimu klasöründe yeni config dosyasını oluştur.
    if not path.isfile(newpath):
        with open(newpath,"w") as f:
            f.write(
            "[TurkAnime]\n"+
            "manuel fansub = False\n"+
            "izlerken kaydet = False\n"+
            "indirilenler = " + f"{ROOT}\n"
            )

    # Yazılıma eklenen yeni ayarları config dosyasına ekler.
    new_options = ["manuel fansub"]
    parser = ConfigParser()
    parser.read(newpath)
    for i in new_options:
        if not parser.has_option("TurkAnime",i):
            parser.set("TurkAnime",i,"False")
    with open(newpath,"w") as f:
        parser.write(f)
