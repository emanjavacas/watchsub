#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import sys
import os
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from subliminal import download_best_subtitles
from subliminal import save_subtitles, region, scan_video
from subliminal.video import VIDEO_EXTENSIONS
from babelfish import Language

logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)
LANGS = set([Language(l) for l in ['eng', 'deu', 'rom', 'spa']])


def get_extension(path):
    if os.path.isfile(path):
        basename = os.path.basename(path)
        return ("." + basename.split(".")[-1]).lower()
    return ""


class MovieHandler(FileSystemEventHandler):
    def on_created(self, event):
        print event.src_path
        if not get_extension(event.src_path) in VIDEO_EXTENSIONS:
            return
        try:
            movie = scan_video(event.src_path)
            subtitles = download_best_subtitles([movie], LANGS)
            logging.info("Downloaded subtitles for movie %s" % movie.name)
            save_subtitles(movie, subtitles[movie])
        except Exception as e:
            logging.info("Exception [%s] while downloading" % str(e))

if __name__ == '__main__':
    # subliminal config
    region.configure('dogpile.cache.dbm',
                     arguments={'filename': '.cachefile.dbm'})
    # event handlers
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = MovieHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
