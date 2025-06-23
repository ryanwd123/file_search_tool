import sys
# from .app import create_application
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from .utils.file_operations import FileOps  # noqa: F401
from .backend import Backend  # noqa: F401


def main():
    app = QGuiApplication(sys.argv)
    app.setOrganizationDomain('QuickFileSearch')
    app.setOrganizationName('QuickFileSearch')


    engine = QQmlApplicationEngine()
    engine.quit.connect(app.quit)
    qml_file = Path(__file__).parent / 'qml' / 'main.qml'
    engine.load(qml_file)
    # Run the application
    result = app.exec()