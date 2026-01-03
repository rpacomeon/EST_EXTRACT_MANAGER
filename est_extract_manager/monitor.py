"""
Folder Monitoring Module.
Monitors watch folder for new EST log files using Watchdog.
"""
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Callable, Optional
import threading
import queue


class ESTLogHandler(FileSystemEventHandler):
    """Handler for EST log file events."""
    
    def __init__(self, callback: Callable[[str], None], file_queue: queue.Queue):
        """
        Initialize handler.
        
        Args:
            callback: Function to call when new file is detected.
            file_queue: Queue to put file paths in.
        """
        super().__init__()
        self.callback = callback
        self.file_queue = file_queue
        self.processed_files = set()
    
    def on_created(self, event):
        """Handle file creation event."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Process CSV and Excel files
        if file_path.suffix.lower() not in ['.csv', '.xlsx', '.xls']:
            return
        
        # Wait a bit for file to be fully written
        time.sleep(2)
        
        # Check if file is still being written (size changes)
        initial_size = file_path.stat().st_size
        time.sleep(1)
        if file_path.stat().st_size != initial_size:
            # File is still being written, wait more
            time.sleep(2)
        
        # Avoid processing same file multiple times
        file_key = str(file_path.absolute())
        if file_key in self.processed_files:
            return
        
        # Verify file exists and is readable
        if not file_path.exists() or not file_path.is_file():
            return
        
        self.processed_files.add(file_key)
        self.file_queue.put(str(file_path))
        
        # Callback is handled in processing thread


class FolderMonitor:
    """Monitors a folder for new EST log files."""
    
    def __init__(self, watch_folder: str, callback: Callable[[str], None]):
        """
        Initialize folder monitor.
        
        Args:
            watch_folder: Folder path to monitor.
            callback: Function to call when new file is detected.
        """
        self.watch_folder = Path(watch_folder)
        self.callback = callback
        self.observer: Optional[Observer] = None
        self.file_queue = queue.Queue()
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start monitoring the folder."""
        if self.is_running:
            return
        
        # Create watch folder if it doesn't exist
        self.watch_folder.mkdir(parents=True, exist_ok=True)
        
        # Create event handler
        event_handler = ESTLogHandler(self.callback, self.file_queue)
        
        # Create observer
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.watch_folder), recursive=False)
        self.observer.start()
        
        self.is_running = True
        
        # Start processing thread
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop monitoring the folder."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
    
    def _process_queue(self):
        """Process files from queue."""
        while self.is_running:
            try:
                file_path = self.file_queue.get(timeout=1)
                if self.callback:
                    self.callback(file_path)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing file from queue: {e}")

