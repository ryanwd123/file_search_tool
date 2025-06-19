"""
File Operations Module

This module provides QObject classes for file operations that can be exposed to QML.
"""
import os
from pathlib import Path
from PySide6.QtCore import QObject, Slot
from PySide6.QtQml import QmlElement, QmlSingleton
import subprocess
import random
import pyperclip

from pygments import highlight
from pygments.lexers import guess_lexer, get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

QML_IMPORT_NAME = "fsearch"
QML_IMPORT_MAJOR_VERSION = 1


def highlight_file_content(file_path, style='default', line_numbers=False):
    """
    Read a text file and return syntax-highlighted HTML.
    
    Args:
        file_path (str): Path to the text file
        style (str): Pygments style name (default: 'default')
        line_numbers (bool): Whether to include line numbers (default: True)
    
    Returns:
        str: HTML string with syntax highlighting
    
    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If there's an error reading the file
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # If file is empty, return empty HTML
        if not content.strip():
            return "<pre><code></code></pre>"
        
        # Try to guess the lexer based on content
        try:
            lexer = guess_lexer(content)
        except ClassNotFound:
            # If guessing fails, try to use filename extension
            try:
                _, ext = os.path.splitext(file_path)
                if ext:
                    lexer = get_lexer_by_name(ext[1:])  # Remove the dot
                else:
                    # Default to plain text if all else fails
                    lexer = get_lexer_by_name('text')
            except ClassNotFound:
                lexer = get_lexer_by_name('text')
        
        # Create HTML formatter
        formatter = HtmlFormatter(
            style=style,
            linenos=line_numbers,
            cssclass='highlight'
        )
        
        # Generate highlighted HTML
        highlighted = highlight(content, lexer, formatter)
        return highlighted
        
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {e}")

def highlight_file_with_css(file_path, style='default', line_numbers=True):
    """
    Read a text file and return both CSS and highlighted HTML.
    
    Args:
        file_path (str): Path to the text file
        style (str): Pygments style name (default: 'default')
        line_numbers (bool): Whether to include line numbers (default: True)
    
    Returns:
        tuple: (css_string, html_string)
    """
    # Get the highlighted HTML
    html = highlight_file_content(file_path, style, line_numbers)
    
    # Generate CSS for the style
    formatter = HtmlFormatter(style=style, linenos=line_numbers, cssclass='highlight')
    css = formatter.get_style_defs('.highlight')
    
    return css, html


def highlighted_file(file_path, style='default', line_numbers=False):
    """
    Read a text file, apply syntax highlighting, and save as HTML file.
    
    Args:
        file_path (str): Path to the input text file
        output_path (str): Path for the output HTML file
        style (str): Pygments style name (default: 'default')
        line_numbers (bool): Whether to include line numbers (default: True)
    """
    css, html = highlight_file_with_css(file_path, style, line_numbers)
    
    # Create complete HTML document
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Syntax Highlighted: {os.path.basename(file_path)}</title>
    <style>
{css}
    </style>
</head>
<body>
{html}
</body>
</html>"""
    
    return full_html



@QmlElement
@QmlSingleton
class FileOps(QObject):
    
    def __init__(self, parent=None):
        print('created FileOps Instance')
        super().__init__(parent)
    
    @Slot(str)
    def openFile(self, file_path: str):
        os.startfile(file_path)

    @Slot(str)
    def revealInExplorer(self, file_path: str):
        subprocess.run(['explorer', '/select,', file_path])

    @Slot(str)
    def copy(self, txt: str):
        pyperclip.copy(txt)

    @Slot(str, str, result=str)
    def isOneDrive(self, file_path: str, text:str):
        if random.randint(1,2) == 1:
            return ""
        else:
            return text
        
    @Slot(str, result=str)
    def readText(self, file_path:str):
        try:
            print('get txt', file_path)

            p = Path(file_path)
            if p.exists():
                txt = highlighted_file(file_path)
            else:
                txt = ''
            return txt
        except Exception as e:
            return str(e)
        


