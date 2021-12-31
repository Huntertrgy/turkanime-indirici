from sys import exit as kapat
import subprocess as sp
from os import name,rename,remove
import os.path
from prompt_toolkit import styles
from prompt_toolkit.shortcuts import confirm
from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import SessionNotCreatedException
from concurrent.futures import as_completed, ThreadPoolExecutor
from rich.progress import Event
from urllib.request import urlopen
from urllib.error import HTTPError
import signal
from shutil import rmtree
from functools import partial

from .compile import dosya

from pprint import pprint
from py7zr import SevenZipFile

from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from .compile import dosya,ROOT

def gereksinim_kontrol(progress=None):
    """ Gereksinimlerin erişilebilir olup olmadığını kontrol eder """
    eksik, stdout, fails, ERR = False, "\n", [], 404

    for gereksinim in ["geckodriver","youtube-dl","mpv"]:
        dizin = os.path.isfile(dosya(f"{gereksinim}.exe"))

        status = sp.Popen(
            f'{dosya(gereksinim)}.exe --version',
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            shell=True
        ).wait() if dizin else ERR

        if status>0:
            errstr = "bulunamadı" if not dizin else f"bulundu ama çalıştırılamadı.{status}"
            stdout += f"x {gereksinim} {errstr}.\n"
            fails.append(gereksinim)
            eksik=True
        else:
            stdout += f"+ {gereksinim} bulundu.\n"
    if eksik:
        progress.stop() if progress else Pass
        print(stdout+"\nBelirtilen program yada programlar",
            "Belgelerim/TurkAnimu dizininde bulunamadı.")

        if not confirm("Otomatik olarak indirilsin mi?"):
            kapat(1)

        dl = DownloadGereksinim(fails)
        if not dl.status:
            print("Gerekli eklentiler kurulamadı, manuel olarak kurmak için wiki sayfasını ziyaret edin:\n",
                "https://github.com/KebabLord/turkanime-indirici/wiki/Manual-olarak-gereksinimleri-indirmek")
            kapat(1)



class DownloadGereksinim:
    def __init__(self,fails=None):
        self.done_event = Event()
        signal.signal(signal.SIGINT, lambda s,f:self.done_event.set())
        self.prog = Progress(
            TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
            BarColumn(bar_width=None),"[self.prog.percentage]{task.percentage:>3.1f}%",
            "•",DownloadColumn(),"•",TransferSpeedColumn(),"•",TimeRemainingColumn()
        )
        self.status=True
        BASE = "https://raw.githubusercontent.com/KebabLord/turkanime-indirici/binary/"

        if fails:
            for fail in fails:
                ext = "exe" if not "mpv" in fail else "7z"
                self.download(f"{BASE}{fail}.{ext}",ROOT)
            if not (self.status and "mpv" in fails):
                return
            # Post install mpv
            self.prog.console.log(f"mpv rar'dan çıkartılıyor")
            mpvzip = SevenZipFile(dosya("mpv.7z"),mode='r')
            mpvzip.extractall(path=dosya("mpv_bin"))
            mpvzip.close()
            rename(
                os.path.join(dosya("mpv_bin"),"mpv.exe"),
                dosya("mpv.exe") )
            rmtree(dosya("mpv_bin"),ignore_errors=True)
            remove(dosya("mpv.7z"))


    def copy_url(self, task_id, url, path):
        """Copy data from a url to a local file."""
        self.prog.console.log(f"Requesting {url}")
        try:
            response = urlopen(url)
        except Exception as e:
            self.prog.console.log("HATA:",str(e))
            self.status=False
            return
        try:
            # This will break if the response doesn't contain content length
            self.prog.update(task_id, total=int(response.info()["Content-length"]))
            with open(path, "wb") as dest_file:
                self.prog.start_task(task_id)
                for data in iter(partial(response.read, 32768), b""):
                    dest_file.write(data)
                    self.prog.update(task_id, advance=len(data))
                    if self.done_event.is_set():
                        print("fail")
                        return
        except Exception as e:
            self.prog.console.log("HATA:",str(e))
            self.status=False
            return

        self.prog.console.log(f"Downloaded {path}")

    def download(self, urls, dest_dir):
        """Download multuple files to the given directory."""
        urls = [urls] if not type(urls) is list else urls
        with self.prog:
            with ThreadPoolExecutor(max_workers=4) as pool:
                for url in urls:
                    filename = url.split("/")[-1]
                    dest_path = os.path.join(dest_dir, filename)
                    task_id = self.prog.add_task("download", filename=filename, start=False)
                    pool.submit(self.copy_url, task_id, url, dest_path)


def webdriver_hazirla(progress):
    """ Selenium webdriver'ı hazırla """
    parser = ConfigParser()
    parser.read(dosya("TurkAnimu.ini"))
    options = Options()
    options.add_argument('--headless')
    if parser.has_option("TurkAnime","firefox konumu"):
        options.binary_location = parser.get("TurkAnime","firefox konumu")
    profile = webdriver.FirefoxProfile()
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference('useAutomationExtension', False)
    profile.set_preference('permissions.default.image', 2)
    profile.set_preference("network.proxy.type", 0)
    profile.update_preferences()
    desired = webdriver.DesiredCapabilities.FIREFOX
    if name == 'nt':
        try:
            return webdriver.Firefox(
                profile, options=options,service_log_path='NUL',
                executable_path=dosya('geckodriver.exe'), desired_capabilities=desired
            )
        except SessionNotCreatedException:
            progress.stop()
            input("Program Firefox'un kurulu olduğu dizini tespit edemedi "+
                  "Manuel olarak firefox.exe'yi seçmek için yönlendirileceksiniz.\n"+
                  "(Devam etmek için entera basın)")
            from easygui import fileopenbox
            indirilenler_dizin=fileopenbox("/")
            if indirilenler_dizin:
                parser.set("TurkAnime","firefox konumu",indirilenler_dizin)
                with open(dosya("TurkAnimu.ini"),"w") as f:
                    parser.write(f)
                input("Programı yeniden başlatmalısınız. (Devam etmek için entera basın)")
            kapat()
    return webdriver.Firefox(
        profile, options=options,
        service_log_path='/dev/null',desired_capabilities=desired
        )

prompt_tema = styles.Style([
    ('qmark', 'fg:#5F819D bold'),
    ('question', 'fg:#289c64 bold'),
    ('answer', 'fg:#48b5b5 bg:#hidden bold'),
    ('pointer', 'fg:#48b5b5 bold'),
    ('highlighted', 'fg:#07d1e8'),
    ('selected', 'fg:#48b5b5 bg:black bold'),
    ('separator', 'fg:#6C6C6C'),
    ('instruction', 'fg:#77a371'),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])
