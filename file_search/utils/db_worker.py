from typing import List, Dict, Any
from PySide6.QtCore import Signal, QObject, Slot
from .database import DatabaseManager, DbRequest
from .utils import ScanInfo
import threading
import time  # noqa: F401


class DatabaseWorker(QObject):
    """Worker that runs in a separate thread to handle database operations"""

    batchUpdateCompleted = Signal(int)  # number of files updated
    favoritesReady = Signal(list)  # list of favorites
    foldersToScan = Signal(ScanInfo)
    searchResultsReady = Signal(list)  # search results
    operationError = Signal(str, str)  # operation, error_message
    responseReady = Signal(str, dict)  # type: ignore # requestId, result
    errorOccurred = Signal(str, dict)  # requestId, error

    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()

    @Slot()
    def cleanup_database_connections(self):
        """Clean up database connections to prevent resource leakage"""
        try:
            self.db_manager.cleanup_connections()
            print("Database connections cleaned up successfully")
        except Exception as e:
            print(f"Error cleaning up database connections: {e}")
            self.operationError.emit("cleanup_database_connections", str(e))

    @Slot(list)
    def batch_file_table_update(self, files_info: List[Dict[str, Any]], paths_to_delete: list[str]):
        """Handle batch file update request"""

        self.db_manager.bulk_delete_files(paths_to_delete)
        try:
            from .database import File

            session = self.db_manager.get_session()
            try:
                files_updated = 0
                batch_size = 1000

                # Process files in batches of 1000
                for i in range(0, len(files_info), batch_size):
                    batch = files_info[i : i + batch_size]

                    for file_info in batch:
                        # Check if file already exists
                        existing_file = session.query(File).filter(File.file_path == file_info["path"]).first()
                        if existing_file:
                            # Update existing file
                            existing_file.file_size = file_info["file_size"]
                            existing_file.last_modified_date = file_info["modified_time"]
                        else:
                            # Create new file record
                            new_file = File(
                                file_path=file_info["path"],
                                file_size=file_info["file_size"],
                                last_modified_date=file_info["modified_time"],
                                scan_folder=file_info["scan_folder"],
                            )
                            session.merge(new_file)
                        files_updated += 1

                    # Commit each batch with proper mutex handling
                    thread_id = threading.current_thread().ident
                    print(f"thread {thread_id} about to commit batch {i // batch_size + 1} with {len(batch)} files")
                    try:
                        self.db_manager.db_mutex.lock()
                        session.commit()
                    finally:
                        self.db_manager.db_mutex.unlock()

                self.batchUpdateCompleted.emit(files_updated)

            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
        except Exception as e:
            print("error in db worker process batch commit")
            print(e)
            self.operationError.emit("batch_file_table_update", str(e))

    @Slot()
    def get_favorites(self):
        """Get all favorites"""
        try:
            favorites = self.db_manager.get_favorites()
            self.favoritesReady.emit(favorites)
        except Exception as e:
            print(f"Error getting favorites: {e}")
            self.operationError.emit("get_favorites", str(e))

    @Slot()
    def getFoldersForScan(self):
        # folders = self.db_manager.get_folders_to_index()
        self.db_manager.delete_removed()
        folders = self.db_manager._sql_command(
            {"command": "sql_command", "sql": "select file_path from folders_to_index"} # type: ignore
        )["result"]  # type: ignore
        if not folders:
            return
        folders = [x[0] for x in folders]  # type: ignore
        folders.append('recent_files')
        folders_dict = {}

        for f in folders:
            folders_dict[f] = self.db_manager.get_files_for_scan_folder(f)

        for k, v in folders_dict.items():
            print(f'{k}, {len(v)}')


        scan_info = ScanInfo(
            folders_to_scan=folders_dict,
            folders_to_ignore=[
                x[0]
                for x in self.db_manager._sql_command(
                    {"command": "sql_command", "sql": "select file_path from ignore_folders"} # type: ignore
                )["result"]
            ],  # type: ignore
        )

        self.foldersToScan.emit(scan_info)

    @Slot(str, int)
    def search_files(self, search_term: str, limit: int = 1000):
        """Search for files"""
        try:
            results = self.db_manager.get_files_by_search(search_term, limit)
            self.searchResultsReady.emit(results)
        except Exception as e:
            print(f"Error searching files: {e}")
            self.operationError.emit("search_files", str(e))

    @Slot(str, dict)
    def process_request(self, request_id: str, request: DbRequest):
        # print(f'proc req {request_id}, {request}')
        try:
            handlers = {
                "sql_command": self.db_manager._sql_command,
            }

            result = handlers[request["command"]](request)
            self.responseReady.emit(request_id, result)

        except Exception as e:
            self.errorOccurred.emit(request_id, {"error": str(e)})
