import datetime
from dataclasses import dataclass
from .database import File


@dataclass
class ScanInfo:
    folders_to_scan:dict[str,list[File]]
    folders_to_ignore:list[str]


def format_file_size(size_in_bytes):
    """
    Format file size in human-readable format (KB, MB, GB)
    
    Args:
        size_in_bytes (int): File size in bytes
        
    Returns:
        str: Formatted file size
    """
    if size_in_bytes is None:
        return "Unknown"
    
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes/1024:.1f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes/(1024*1024):.1f} MB"
    else:
        return f"{size_in_bytes/(1024*1024*1024):.1f} GB"

def format_date(timestamp):
    """
    Format date in a user-friendly way
    
    Args:
        timestamp (datetime): Date and time to format
        
    Returns:
        str: Formatted date string
    """
    if timestamp is None:
        return "Unknown"
    
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(e)
            return timestamp
    
    now = datetime.datetime.now()
    delta = now - timestamp
    
    if delta.days == 0:
        # Today
        return f"Today {timestamp.strftime('%H:%M')}"
    elif delta.days == 1:
        # Yesterday
        return f"Yesterday {timestamp.strftime('%H:%M')}"
    elif delta.days < 7:
        # This week
        return timestamp.strftime('%A %H:%M')
    elif delta.days < 365:
        # This year
        return timestamp.strftime('%b %d, %H:%M')
    else:
        # Older
        return timestamp.strftime('%b %d, %Y')
