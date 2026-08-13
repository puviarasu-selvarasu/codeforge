import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.conf import settings
from .ingestion import index_file, index_all_files, _chunks, rebuild_vectorizer, save_index

logger = logging.getLogger(__name__)

class KnowledgeFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            time.sleep(1)
            index_file(event.src_path)
    def on_modified(self, event):
        if not event.is_directory:
            time.sleep(1)
            index_file(event.src_path)
    def on_deleted(self, event):
        if not event.is_directory:
            source = str(Path(event.src_path).relative_to(settings.KNOWLEDGE_ROOT))
            _chunks[:] = [c for c in _chunks if c['source'] != source]
            rebuild_vectorizer()
            save_index()
            logger.info(f"Removed chunks from {source}")

def start_watchdog():
    knowledge_root = settings.KNOWLEDGE_ROOT
    if not knowledge_root.exists():
        knowledge_root.mkdir(parents=True)
    logger.info("Initial indexing of knowledge folder...")
    index_all_files()
    event_handler = KnowledgeFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(knowledge_root), recursive=True)
    observer.start()
    logger.info("Watchdog started.")
    return observer