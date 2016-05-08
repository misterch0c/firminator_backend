#!/usr/bin/python
import time
from django.conf import settings
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from subprocess import check_call

class FileCreateEvent(FileSystemEventHandler):
    def on_created(self, event):
        brand = "Netgear"
        number = check_output("python " + settings.FIRMADYNE_DIR + "/sources/extractor/extractor.py -b " + brand + " -sql 127.0.0.1 -np -nk '" + event.src_path.replace("./", "") + "' images")
        check_call(settings.FIRMADYNE_DIR + "/scripts/getArch.sh /home/dev/firmadyne/images/" + number + ".tar.gz")
        check_call(settings.FIRMADYNE_DIR + "/scripts/tar2db.py -i 1 -f " + settings.FIRMADYNE_DIR + "/images/" + number + ".tar.gz")
        check_call("sudo " + settings.FIRMADYNE_DIR + "/scripts/makeImage.sh " + number)
        check_call(settings.FIRMADYNE_DIR + "/scripts/inferNetwork.sh " + number)


if __name__ == "__main__":
    event_handler = FileCreateEvent()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
