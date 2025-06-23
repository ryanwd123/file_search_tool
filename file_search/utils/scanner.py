import traceback
import time
import os
import datetime
import threading
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QThreadPool, QRunnable, Slot
from .utils import ScanInfo
from .database import File
from .recent_files import get_recent_file_data
# from .thread_check import print_active_threads

ignored_file_types = set([
    '.pyc',
])


class ScanTask(QRunnable):
    def __init__(self, scanner, folder_path, folders_to_ignore, folder_files:list[File]):
        super().__init__()
        self.scanner:'FileScanner' = scanner
        self.folder_path = folder_path
        self.folders_to_ignore = folders_to_ignore
        self.folder_files = folder_files
    
    def run(self):
        """Execute the folder scan"""
        self.scanner.scan_folder(self.folder_path, self.folders_to_ignore, self.folder_files)

class ScanRecentTask(QRunnable):
    def __init__(self, scanner, recent:list[File], ignore:list[str]):
        super().__init__()
        self.scanner:'FileScanner' = scanner
        self.recent = recent
        self.ignore = ignore

    
    def run(self):
        """Execute the folder scan"""
        try:
            self.scanner.recent_files(self.recent, self.ignore)
        except Exception as e:
            print(f'Error with recent files: {e}')
            print("Full traceback:")
            traceback.print_exc()

class FileScanner(QObject):
    scanSignal = Signal(str)  # current_path, files_processed, total_files
    scan_error = Signal(str)               # error_message
    batch_scan_to_send = Signal(list,list)      # batch of files to send to database worker
    
    
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup threadpool with 8 threads
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(8)
        
        # State tracking
        self.active_tasks = 0
        self.task_lock = threading.Lock()

        self._is_scanning = False
        
        self.scan_status = 'not scanned'
        self.scanned_folders:int = 0
        self.total_folders:int = 0
        self.batches_emitted = 0
        self.batches_completed = 0
        self.start_time = 0


    
    def scan_folder(self, folder_to_scan, folders_to_ignore:list[str], folder_files_prior:list[File]):
        """
        Main scanning function: scan one folder and emit all files in that folder at once.
        
        Args:
            folder_to_scan: Path to the folder to scan
            folders_to_ignore: List of folder paths to ignore
        """
        folder_files = []  # Collect all files in this folder
        found_paths = set()
        files_in_folder = 0

        folder_files_prior_dict = {f.file_path:f for f in folder_files_prior}
        
        # Normalize ignored paths for consistent comparison
        normalized_ignored = [os.path.normpath(ignored) for ignored in folders_to_ignore]
        
        def is_path_ignored(path):
            """Check if a path is within any ignored folder"""
            normalized_path = os.path.normpath(path)
            return any(
                normalized_path.startswith(ignored + os.sep) or normalized_path == ignored
                for ignored in normalized_ignored
            )
            
        def is_file_type_ignored(file_path):
            """Check if a file should be ignored based on its extension"""
            if not ignored_file_types:
                return False
            
            _, ext = os.path.splitext(file_path)
            return ext.lower() in ignored_file_types

        try:
            if not os.path.exists(folder_to_scan):
                print(f"Folder not found: {folder_to_scan}")
                return
            
            print(f"Scanning folder: {folder_to_scan}")
            
            # Walk through the folder and collect all files
            for root, dirs, files in os.walk(folder_to_scan, topdown=True):
                # Skip this directory entirely if it's ignored
                if is_path_ignored(root):
                    dirs.clear()  # Don't recurse into subdirectories
                    continue
                
                # Remove ignored folders from dirs list
                dirs[:] = [d for d in dirs if not is_path_ignored(os.path.join(root, d))]
                
                # Process each file in current directory
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Skip files in ignored paths (extra safety check)
                    if is_path_ignored(file_path):
                        print(file_path)
                        continue

                    if is_file_type_ignored(file_path):
                        continue

                    found_paths.add(file_path)
                    
                    try:
                        # Get file information
                        file_stat = os.stat(file_path)
                        modified_time = datetime.datetime.fromtimestamp(file_stat.st_mtime)
                        current_modified_str = modified_time.strftime('%Y-%m-%d %H:%M:%S')
                        if file_path in folder_files_prior_dict and current_modified_str == folder_files_prior_dict[file_path].last_modified_date:
                            continue
                        
                        # Add to folder's file list
                        folder_files.append({
                            'path': file_path,
                            'modified_time': current_modified_str,
                            'file_size': file_stat.st_size,
                            'scan_folder':folder_to_scan
                        })
                        files_in_folder += 1
                        
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
                        continue
            
            paths_to_delete = list(set(folder_files_prior_dict).difference(found_paths))
            # Emit entire folder's file list at once to database worker
            if folder_files or paths_to_delete:

                self.batch_scan_to_send.emit(folder_files, paths_to_delete)

            with self.task_lock:
                self.batches_emitted += 1
                self.scanned_folders += 1
                print(f'on folder completed, scanned folder {self.scanned_folders} of {self.total_folders}, batch completed {self.batches_completed} of {self.batches_emitted}')
                if self.scanned_folders == self.total_folders:
                    self.scan_status = f'scanned {self.scanned_folders} of {self.total_folders} folders, processing db updates'
                    self.scanSignal.emit(self.scan_status)
                else:
                    self.scan_status = f'scanned {self.scanned_folders} of {self.total_folders} folders'
                    self.scanSignal.emit(self.scan_status)
            self._check_scan_complete()
            
                # Emit progress with last file path from this folder
                


                    
            
            print(f"Completed scanning {folder_to_scan}: {files_in_folder} files")
            
        except Exception as e:
            error_msg = f"Error scanning {folder_to_scan}: {e}"
            print(error_msg)
            self.scan_error.emit(error_msg)
    
    def recent_files(self, recent:list[File], folders_to_ignore:list[str]):
        new_data = get_recent_file_data()
        old_data = {r.file_path:r for r in recent}
        print(f'recent count new: {len(new_data)}, count old: {len(old_data)}')
        
        result = []
        new_paths = set([f.file_path for f in recent])

        for f in new_data:
            new_path = f['path']
            new_time = f['modified_time']
            new_size = f['file_size']
            new_folder = f['scan_folder']

            if new_path in old_data:
                if new_time == old_data[new_path].last_modified_date:
                    continue
            result.append({
                    'path': new_path,
                    'modified_time': new_time,
                    'file_size': new_size,
                    'scan_folder':new_folder
                })

        delete = []

        for path, item in old_data.items():
            if path in new_paths:
                continue
            if str(path).lower().startswith('http'):
                continue
            if Path(str(path)).exists():
                continue
            delete.append(path)

        print(f'emit recent update: {len(result)}, delete: {len(delete)}')
        self.batch_scan_to_send.emit(result, delete)


        with self.task_lock:
            self.batches_emitted += 1
            self.scanned_folders += 1
            print(f'on folder completed, scanned folder {self.scanned_folders} of {self.total_folders}, batch completed {self.batches_completed} of {self.batches_emitted}')
            if self.scanned_folders == self.total_folders:
                self.scan_status = f'scanned {self.scanned_folders} of {self.total_folders} folders, processing db updates'
                self.scanSignal.emit(self.scan_status)
            else:
                self.scan_status = f'scanned {self.scanned_folders} of {self.total_folders} folders'
                self.scanSignal.emit(self.scan_status)



    
    @Slot(ScanInfo)
    def run_scan(self, scan_info:ScanInfo):
        """
        Function to run scan: gets folders from db and submits scan_folder tasks to threadpool.
        """
        try:
            if self._is_scanning:
                return

            print("Starting file scan...")
            self.start_time = time.time()
            
            self._is_scanning = True
            self.batches_emitted = 0
            self.batches_completed = 0
            self.scanned_folders = 0
            self.total_folders = len(scan_info.folders_to_scan.keys())
            self.scan_status = f'scanned {self.scanned_folders} of {self.total_folders} folders'
            self.scanSignal.emit(self.scan_status)
            
            

            
            print(f"Got {len(scan_info.folders_to_scan.keys())} folders to scan, {len(scan_info.folders_to_ignore)} folders to ignore")
            if 'recent_files' in scan_info.folders_to_scan:
                recent = scan_info.folders_to_scan.pop('recent_files')
                task = ScanRecentTask(self, recent,scan_info.folders_to_ignore)
            else:
                self.total_folders += 1
                task = ScanRecentTask(self, [],scan_info.folders_to_ignore)
            
            self.threadpool.start(task)
            
            print(f"Submitting {len(scan_info.folders_to_scan.keys())} folders to threadpool with {self.threadpool.maxThreadCount()} threads")
            
            for folder in scan_info.folders_to_scan:
                task = ScanTask(self, folder, scan_info.folders_to_ignore, scan_info.folders_to_scan[folder])
                self.threadpool.start(task)
            
            print("All folder scan tasks submitted to threadpool")
                
        except Exception as e:
            error_msg = f"Error starting scan: {e}"
            print(error_msg)
            self._is_scanning = False
            self._status_text = f"Error: {error_msg}"
            self._progress_text = ""

            self.scan_error.emit(error_msg)
    
    def _check_scan_complete(self):
        with self.task_lock:
            print(f'scanned folder {self.scanned_folders} of {self.total_folders}, batch completed {self.batches_completed} of {self.batches_emitted}')
            if self.scanned_folders == self.total_folders and self.batches_completed == self.batches_emitted:
                self._is_scanning = False
                last_scanned = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.scan_status = f'last scanned: {last_scanned}'
                self._status_text = self.scan_status
                self.scanSignal.emit(self.scan_status)
                # print_active_threads()
                # Clean up thread pool after scan completion
                # self._cleanup_threadpool()


    def reset_scan_state(self):
        """Reset all scan state variables for a fresh start"""
        with self.task_lock:
            self._is_scanning = False
            self.scanned_folders = 0
            self.total_folders = 0
            self.batches_emitted = 0
            self.batches_completed = 0
            self.active_tasks = 0
            self.start_time = 0
            self.scan_status = 'not scanned'

    def _on_batch_completed(self, files_updated):
        """Handle batch update completed signal"""
        print(f"Database batch completed: {files_updated} files updated")
        with self.task_lock:
            self.batches_completed += 1
        self._check_scan_complete()

    
    def _on_db_error(self, operation, error):
        """Handle database error signal"""
        error_msg = f"Database error during {operation}: {error}"
        print(error_msg)
        # Reset scanning state on error to prevent hanging
        with self.task_lock:
            self._is_scanning = False
        self.scan_error.emit(error_msg)
    


# Global file scanner instance
_file_scanner = None


def get_file_scanner():
    """Get or create the global file scanner instance"""
    global _file_scanner
    if _file_scanner is None:
        _file_scanner = FileScanner()
    return _file_scanner