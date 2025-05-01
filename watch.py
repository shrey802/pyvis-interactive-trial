import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RefreshHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if not event.is_directory:
            print(f"Change detected in {event.src_path}. Regenerating graph...")
            subprocess.run(["python", "vis.py"])

if __name__ == "__main__":
    path = "."
    observer = Observer()
    observer.schedule(RefreshHandler(), path=path, recursive=False)
    observer.start()
    print("Watching for changes... Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
