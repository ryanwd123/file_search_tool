from PySide6.QtCore import QObject, Slot, Signal, QThread, Property, QJsonDocument
from PySide6.QtQml import QmlElement, QmlSingleton

from .utils.scanner import FileScanner
from .utils.file_model import FileListModel
from .utils.db_worker import DatabaseWorker
import uuid

QML_IMPORT_NAME = "fsearch"
QML_IMPORT_MAJOR_VERSION = 1
# QQmlDebuggingEnabler.enableDebugging(True)


@QmlElement
@QmlSingleton
class Backend(QObject):
    requestFavoritesSignal = Signal()
    searchSignal = Signal(str, int)
    startScanSignal = Signal()
    cleanupSignal = Signal()
    scanStatusChanged = Signal()
    responseReady = Signal(str, 'QJsonObject')  # type: ignore # requestId, result
    procReq = Signal(str, dict)  # type: ignore # requestId, result
    errorOccurred = Signal(str, dict)  # requestId, error

    def __init__(self, parent=None):
        super().__init__(parent)
        print("created backend Instance")
        self._scan_status = ''
        self._scanner = FileScanner()
        self._pending_requests = {}
        self._file_list_model: FileListModel = FileListModel() # type: ignore
        self._dbworker = DatabaseWorker()
        self._dbworker_thread = QThread()
        self._dbworker.moveToThread(self._dbworker_thread)
        self._dbworker_thread.start()

        self._scanner.scanSignal.connect(self.on_scan_status_update)
        self._scanner.batch_scan_to_send.connect(self._dbworker.batch_file_table_update)

        self._dbworker.foldersToScan.connect(self._scanner.run_scan)
        self._dbworker.batchUpdateCompleted.connect(self._scanner._on_batch_completed)
        self._dbworker.operationError.connect(self._scanner._on_db_error)

        self.searchSignal.connect(self._dbworker.search_files)
        self.requestFavoritesSignal.connect(self._dbworker.get_favorites)
        self.startScanSignal.connect(self._dbworker.getFoldersForScan)
        self.cleanupSignal.connect(self._dbworker.cleanup_database_connections)
        self.procReq.connect(self._dbworker.process_request)

        self._dbworker.responseReady.connect(self.respReadySlot)
        self._dbworker.errorOccurred.connect(self.errOccuredSlot)

        self._dbworker.searchResultsReady.connect(self._file_list_model.on_search_results)
        self._dbworker.favoritesReady.connect(self._file_list_model.on_favorites_ready)
        self._dbworker.operationError.connect(self._file_list_model.on_operation_error)


    @Slot(str)
    def searchFiles(self, search_term: str):
        """Search for files and update the model (async)."""
        if not search_term.strip():
            # When search is empty, load favorites instead of clearing
            self.requestFavoritesSignal.emit()
            return

        # Request search from database worker (async)
        self.searchSignal.emit(search_term, 1000)

    @Property(FileListModel, constant=True) # type: ignore
    def fileListModel(self):
        return self._file_list_model
    
    @Slot()
    def cleanupResources(self):
        """Clean up database connections and scanner resources"""
        print("Triggering resource cleanup...")
        self.cleanupSignal.emit()
        if hasattr(self._scanner, 'reset_scan_state'):
            self._scanner.reset_scan_state()

    @Slot(str)
    def on_scan_status_update(self, status):
        """Handle scan status updates from scanner"""
        if self._scan_status != status:
            self._scan_status = status
            self.scanStatusChanged.emit()

    @Property(str, notify=scanStatusChanged) # type: ignore
    def scanStatus(self):
        return self._scan_status
    
    @Slot()
    def shutdown(self):
        """Properly shutdown the database worker thread"""
        print("Shutting down database worker thread...")
        
        # Signal the worker to clean up
        self.cleanupSignal.emit()
        
        # Stop the thread gracefully
        self._dbworker_thread.quit()
        
        # Wait for the thread to finish (with timeout)
        if not self._dbworker_thread.wait(5000):  # 5 second timeout
            print("Warning: Database worker thread did not stop gracefully, terminating...")
            self._dbworker_thread.terminate()
            self._dbworker_thread.wait()
        
        print("Database worker thread stopped successfully")

    @Slot(dict, result=str) # type: ignore
    def request(self, request: dict):
        """Generic async request - returns request ID"""
        request_id = str(uuid.uuid4())
        # print(request_id, request)
        self.procReq.emit(request_id, request)
        
        return request_id
    
    @Slot(str, dict)  # type: ignore # requestId, result
    def respReadySlot(self, req_id:str, message:dict):
        # print('rsponse ready',req_id,message)
        json_obj = QJsonDocument.fromVariant(message).object()
        self.responseReady.emit(req_id, json_obj)

    @Slot(str, dict)  # type: ignore # requestId, result
    def errOccuredSlot(self, req_id:str, message:dict):
        # print('error occured ',req_id,message)
        json_obj = QJsonDocument.fromVariant(message).object()
        self.errorOccurred.emit(req_id, json_obj)