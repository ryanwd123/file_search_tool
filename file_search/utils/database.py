"""
Database module for file search application using SQLAlchemy.
Sets up SQLite database with tables for files, favorites, ignore folders, and folders to index.
"""

from pathlib import Path
from typing import Optional
import os
from typing import List
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    text,
    func,
    and_,
    or_,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from PySide6.QtCore import QMutex
from typing import TypedDict, Literal
Base = declarative_base()


class DbRequest(TypedDict):
    command: Literal['sql_command']
    sql: Optional[str]
    table:Optional[str]
    column_names: Optional[list[str]]
    values: Optional[list[str]]
    column: Optional[str]
    value: Optional[str]


class File(Base):
    """Model for the files table."""

    __tablename__ = "files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(Text, nullable=False, unique=True)  # Full path
    file_size = Column(Integer, nullable=False)
    last_modified_date = Column(String, nullable=False)
    scan_folder = Column(Text, nullable=False)  # Full path


class RecurringFile(Base):
    """Model for the files table."""

    __tablename__ = "recurring_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(Text, nullable=False, unique=True)  # Full path


class Favorite(Base):
    """Model for the favorites table."""

    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(Text, nullable=False, unique=True)


class IgnoreFolder(Base):
    """Model for the ignore_folders table."""

    __tablename__ = "ignore_folders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(Text, nullable=False, unique=True)


class FolderToIndex(Base):
    """Model for the folders_to_index table."""

    __tablename__ = "folders_to_index"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(Text, nullable=False, unique=True)


class ScanHistory(Base):
    """Model for the scan_history table."""

    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(String, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    files_processed = Column(Integer, nullable=False)


class FileAccessed(Base):
    """Model for the file_accessed table."""

    __tablename__ = "file_accessed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(Text, nullable=False)
    accessed_time = Column(String, nullable=False)


class FileAlias(Base):
    """Model for the file_alias table."""

    __tablename__ = "file_alias"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(Text, nullable=False)
    alias = Column(String, nullable=False)


class DatabaseManager:
    """Manages the SQLite database for the file search application using SQLAlchemy."""

    def __init__(self, db_name="file_search.db"):
        """Initialize the database manager."""
        self.db_name = db_name
        self.engine = None
        self.SessionLocal = None
        self.db_mutex = QMutex()  # Mutex to protect database operations
        self.setup_database()
        # self.vaccum_db()

    def setup_database(self):
        db_path = Path(__file__).parent.joinpath(f"{os.getlogin()}_files.db")
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_timeout=30,
            max_overflow=10
        )
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def vaccum_db(self):
        session = self.get_session()
        session.execute(text("VACUUM"))

    def get_session(self) -> Session:
        if not self.SessionLocal:
            raise Exception("Database not initialized. Call setup_database() first.")
        return self.SessionLocal()

    def get_favorites(self):
        self.db_mutex.lock()
        try:
            session = self.get_session()
            try:
                query = session.query(
                    File,
                    Favorite.id.isnot(None).label("is_favorite"),
                ).join(Favorite, File.file_path == Favorite.file_path)
                return query.all()
            except SQLAlchemyError as e:
                raise Exception(f"Failed to get favorites: {str(e)}")
            finally:
                session.close()
        finally:
            self.db_mutex.unlock()


    def bulk_delete_files(self, file_paths: List[str]):
        """Delete multiple files by their paths"""
        self.db_mutex.lock()
        try:
            session = self.get_session()
            try:
                deleted_count = (
                    session.query(File)
                    .filter(File.file_path.in_(file_paths))
                    .delete(synchronize_session=False)
                )
                session.commit()
                return deleted_count
            except SQLAlchemyError as e:
                session.rollback()
                raise Exception(f"Failed to bulk delete files: {str(e)}")
            finally:
                session.close()
        finally:
            self.db_mutex.unlock()

    def get_files_for_scan_folder(self, scan_folder: str):
        self.db_mutex.lock()
        try:
            session = self.get_session()
            try:
                files = session.query(File).filter(File.scan_folder == scan_folder).all()
                return files
            except SQLAlchemyError as e:
                raise Exception(f"Failed to get files for scan folder: {str(e)}")
            finally:
                session.close()
        finally:
            self.db_mutex.unlock()

    def _sql_command(self, request:DbRequest):
        self.db_mutex.lock()
        if not request['sql']:
            return {'result': 0}

        try:
            session = self.get_session()
            sql = request['sql']
            if sql.lower() == 'delete':
                try:
                    if not request['column']:
                        return {'result': 0}

                    value = request['value']
                    col_name = request["column"]
                    table = request["table"]
                    table_ref = f'"{table}"'
                    values_ref = f':{col_name}'
                    col_ref = f'"{col_name}"'
                    params = {col_name:value}
                    sql_txt = f"DELETE FROM {table_ref} WHERE {col_ref} = '{value}'"
                    session.execute(text(sql_txt), params=params)
                    session.commit()
                    session.close()
                    return {'result':1}
                except SQLAlchemyError as e:
                    raise Exception(f"sql command failed: {str(e)}")
            if sql.lower() == 'insert':
                try:
                    if not request['column_names'] or not request['values']: 
                        return {'result': 0}
                    values = request['values']
                    col_names = request["column_names"]
                    table = request["table"]
                    table_ref = f'"{table}"'
                    values_ref = ', '.join([f':{x}' for x in col_names])  # Create named parameters
                    columns_ref = ', '.join([f'"{x}"' for x in col_names])
                    params = {x: values[i] for i, x in enumerate(col_names)}
                    sql_txt = f"INSERT OR IGNORE INTO {table_ref} ({columns_ref}) VALUES ({values_ref})"
                    session.execute(text(sql_txt), params=params)
                    session.commit()
                    session.close()
                    return {'result':1}
                except SQLAlchemyError as e:
                    raise Exception(f"sql command failed: {str(e)}")
            if sql.lower().startswith('select'):
                try:
                    result = session.execute(text(sql)).all()
                    result = [[c for c in row] for row in result]
                    session.close()
                    return {'result':result}
                except SQLAlchemyError as e:
                    raise Exception(f"sql command failed: {str(e)}")
            else:
                try:
                    session.execute(text(sql))
                    session.commit()
                    session.close()
                    return {'result':1}
                except SQLAlchemyError as e:
                    raise Exception(f"sql command failed: {str(e)}")
        finally:
            self.db_mutex.unlock()
            

    def delete_removed(self):
        """Delete files whose scan_folder is not in the folders_to_index list."""
        self.db_mutex.lock()
        try:
            session = self.get_session()
            try:
                # Delete files where scan_folder is not in the folders to index
                deleted_count = (
                    session.query(File)
                    .filter(~File.scan_folder.in_(session.query(FolderToIndex.file_path)))
                    .delete(synchronize_session=False)
                )
                session.commit()
                return deleted_count
            except SQLAlchemyError as e:
                session.rollback()
                raise Exception(f"Failed to delete removed files: {str(e)}")
            finally:
                session.close()
        finally:
            self.db_mutex.unlock()

    def get_file_count(self) -> int:
        """Get the total number of indexed files."""
        self.db_mutex.lock()
        try:
            session = self.get_session()
            try:
                count = session.query(func.count(File.id)).scalar()
                return count or 0
            except SQLAlchemyError as e:
                raise Exception(f"Failed to get file count: {str(e)}")
            finally:
                session.close()
        finally:
            self.db_mutex.unlock()


    def get_files_by_search(self, search_term: str, limit=None):
        self.db_mutex.lock()
        try:
            session = self.get_session()
            try:
                terms = search_term.strip().split()
                if not terms:
                    return []

                query = session.query(
                    File,
                    Favorite.id.isnot(None).label("is_favorite"),
                ).outerjoin(Favorite, File.file_path == Favorite.file_path)
                criteria = []
                for term in terms:
                    term_criteria = or_(
                        File.file_path.ilike(f"%{term}%"),
                    )
                    criteria.append(term_criteria)

                if criteria:
                    query = query.filter(and_(*criteria))

                query = query.order_by(
                    Favorite.id.isnot(None).desc(),  # Favorites first
                    File.last_modified_date.desc(),  # Then alphabetically by file path
                )

                # Apply limit if provided
                if limit is not None:
                    query = query.limit(limit)

                # Execute the query and return the results
                return query.all()

            except SQLAlchemyError as e:
                raise Exception(f"Failed to search files: {str(e)}")
            finally:
                session.close()
        finally:
            self.db_mutex.unlock()

    def cleanup_connections(self):
        """Clean up database connections and reset connection pool."""
        self.db_mutex.lock()
        try:
            if self.engine:
                # Close all connections in the pool
                self.engine.dispose()
                # Recreate the engine to reset the connection pool
                db_path = Path(__file__).parent.joinpath(f"{os.getlogin()}_files.db")
                self.engine = create_engine(
                    f"sqlite:///{db_path}",
                    echo=False,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    pool_timeout=30,
                    max_overflow=10
                )
                self.SessionLocal = sessionmaker(
                    autocommit=False, autoflush=False, bind=self.engine
                )
        finally:
            self.db_mutex.unlock()

    def close_database(self):
        """Close the database connection."""
        self.db_mutex.lock()
        try:
            if self.engine:
                self.engine.dispose()
                self.engine = None
                self.SessionLocal = None
        finally:
            self.db_mutex.unlock()
