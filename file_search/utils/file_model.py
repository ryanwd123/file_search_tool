import os
import random
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, QByteArray, Signal, Slot
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "fsearch"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class FileListModel(QAbstractListModel):
    # Define role names that match the QML delegate requirements
    FilenameRole = Qt.ItemDataRole.UserRole + 1
    ParentFolderRole = Qt.ItemDataRole.UserRole + 2
    FullPathRole = Qt.ItemDataRole.UserRole + 3
    SizeRole = Qt.ItemDataRole.UserRole + 4
    LastModifiedRole = Qt.ItemDataRole.UserRole + 5
    FavoriteRole = Qt.ItemDataRole.UserRole + 6
    # NameAliasRole = Qt.ItemDataRole.UserRole + 7
    IsFolderRole = Qt.ItemDataRole.UserRole + 8
    
    # Additional signals for database operations
    searchError = Signal(str)  # error message
    
    # Signals for communicating with database worker
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._files = []
        
    def rowCount(self, parent=None):
        if parent is None:
            parent = QModelIndex()
        return len(self._files)
    
    @Slot(int, result=str)
    def get_full_path(self, row):
        file_data = self._files[row]
        return file_data['full_path']

    @Slot(str, result=str)
    def getSharePointUrl(self, txt:str):
        return f'1___{txt}'
    
    @Slot(result=int)
    def getRandom(self):
        print('rand')
        return random.randint(1,2)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole.value):
        if not index.isValid() or index.row() >= len(self._files):
            return None
            
        file_data:dict = self._files[index.row()]
        
        if role == self.FilenameRole:
            return file_data.get('filename', '')
        elif role == self.ParentFolderRole:
            return file_data.get('parent_folder', '')
        elif role == self.FullPathRole:
            return file_data.get('full_path', '')
        elif role == self.SizeRole:
            return file_data.get('size', '')
        elif role == self.LastModifiedRole:
            return file_data.get('last_modified', '')
        elif role == self.FavoriteRole:
            return file_data.get('favorite', False)
        # elif role == self.NameAliasRole:
        #     return file_data.get('name_alias', None)
        elif role == self.IsFolderRole:
            return file_data.get('is_folder', False)

            
        return None
        
    def roleNames(self):
        roles = {
            self.FilenameRole: QByteArray(b'filename'),
            self.ParentFolderRole: QByteArray(b'parent_folder'),
            self.FullPathRole: QByteArray(b'full_path'),
            self.SizeRole: QByteArray(b'size'),
            self.LastModifiedRole: QByteArray(b'last_modified'),
            self.FavoriteRole: QByteArray(b'favorite'),
            # self.NameAliasRole: QByteArray(b'name_alias'),
            self.IsFolderRole: QByteArray(b'is_folder'),
        }
        return roles
        
    def setFiles(self, files: List[Dict[str, Any]]):
        self.beginResetModel()
        self._files = files
        self._update_aliases_and_favorites()
        self.endResetModel()
        
    def addFile(self, file_data: Dict[str, Any]):
        """Add a single file to the model."""
        self.beginInsertRows(QModelIndex(), len(self._files), len(self._files))
        self._files.append(file_data)
        self._update_file_metadata(len(self._files) - 1)
        self.endInsertRows()
        
    def removeFile(self, index: int):
        if 0 <= index < len(self._files):
            self.beginRemoveRows(QModelIndex(), index, index)
            self._files.pop(index)
            self.endRemoveRows()
            
    @Slot()
    def clear(self):
        self.beginResetModel()
        self._files.clear()
        self.endResetModel()
        
    def _update_aliases_and_favorites(self):
        """Update alias and favorite information for all files."""
        # Note: With async database operations, metadata is now updated
        # when search results are received, so this method is simplified
        pass
            
    def _update_file_metadata(self, index: int):
        if index >= len(self._files):
            return
        pass
            
    def refreshFile(self, index: int):
        if 0 <= index < len(self._files):
            self._update_file_metadata(index)
            model_index = self.createIndex(index, 0)
            self.dataChanged.emit(model_index, model_index)
            
    def getFileData(self, index: int) -> Optional[Dict[str, Any]]:
        if 0 <= index < len(self._files):
            return self._files[index].copy()
        return None
        
    def findFileByPath(self, full_path: str) -> int:
        for i, file_data in enumerate(self._files):
            if file_data.get('full_path') == full_path:
                return i
        return -1
        
    def formatFileSize(self, size_bytes: int) -> str:
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
            
        return f"{size:.1f} {size_names[i]}"
        
    def formatLastModified(self, timestamp: str) -> str:
        return timestamp
        
    
    @Slot(list)
    def on_search_results(self, results):
        try:
            # Convert database results to model format
            files = []
            for file_obj, is_favorite in results:
                file_data = {
                    'filename': os.path.basename(file_obj.file_path),
                    'parent_folder': os.path.dirname(file_obj.file_path),
                    'full_path': file_obj.file_path,
                    'size': self.formatFileSize(file_obj.file_size),
                    'last_modified': file_obj.last_modified_date,
                    'favorite': bool(is_favorite),
                    'name_alias': None,
                    'is_folder': False  # Files from database are not folders
                }
                files.append(file_data)
                
            self.setFiles(files)
        except Exception as e:
            print(f"Search results processing error: {e}")
            self.searchError.emit(str(e))
            self.clear()
    
    def on_operation_error(self, operation: str, error: str):
        if operation == "search_files":
            print(f"Search error: {error}")
            self.searchError.emit(error)
            self.clear()
    

    
    def on_favorites_ready(self, favorites):
        self.on_search_results(favorites)
    
    @Slot(str)
    def on_favorite_added(self, file_path: str):
        index = self.findFileByPath(file_path)
        if index >= 0:
            self._files[index]['favorite'] = True
            model_index = self.createIndex(index, 0)
            self.dataChanged.emit(model_index, model_index, [self.FavoriteRole])
    
    @Slot(str)
    def on_favorite_removed(self, file_path: str):
        index = self.findFileByPath(file_path)
        if index >= 0:
            self._files[index]['favorite'] = False
            model_index = self.createIndex(index, 0)
            self.dataChanged.emit(model_index, model_index, [self.FavoriteRole])

# qmlRegisterType(FileListModel, QML_IMPORT_NAME, QML_IMPORT_MAJOR_VERSION, 0, 'FileListModel')