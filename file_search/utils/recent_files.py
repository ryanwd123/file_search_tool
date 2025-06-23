# %%
from pathlib import Path
from typing import Any
import winreg
from dataclasses import dataclass
import re
from datetime import datetime, timezone, timedelta
import itertools
import os
import contextlib



@dataclass
class RecentFile:
    path: str
    url:bool
    timespamp: datetime | None

    def dict_for_batch(self):
        try:
            size = 0
            if not self.url and not self.path.lower().startswith('http'):
                if not  Path(self.path).exists():
                    return None
                size = os.stat(self.path).st_size
            mod = (datetime.now() + timedelta(days=-10)).strftime('%Y-%m-%d %H:%M:%S')
            if self.timespamp:
                mod = self.timespamp.strftime('%Y-%m-%d %H:%M:%S')
            return {
                'path': self.path,
                'modified_time': mod,
                'file_size': size,
                'scan_folder':'recent_files'
            }
        except Exception:
            return None




def parse_mru_entry(mru_string):
    pattern = r"\[F([0-9A-Fa-f]{8})\]\[T([0-9A-Fa-f]{16})\]\[O([0-9A-Fa-f]{8})\]\*(.+)"
    match = re.match(pattern, mru_string)

    if match:
        timestamp_hex = match.group(2)
        file_path = match.group(4)
        url = file_path.lower().startswith('http')

        return RecentFile(path=file_path, url=url, timespamp=filetime_to_datetime(int(timestamp_hex, 16)))
    else:
        return None


def filetime_to_datetime(filetime):
    """
    Convert Windows FILETIME (64-bit) to Python datetime
    FILETIME = 100-nanosecond intervals since January 1, 1601 UTC
    """
    # FILETIME epoch starts at January 1, 1601 UTC
    # Unix epoch starts at January 1, 1970 UTC
    # Difference: 11644473600 seconds

    EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970 as FILETIME

    if filetime < EPOCH_AS_FILETIME:
        return None  # Invalid or pre-1970 date

    # Convert to seconds since Unix epoch
    unix_timestamp = (filetime - EPOCH_AS_FILETIME) / 10000000.0

    return datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)


def get_subkeys(base_key, i):
    try:
        subkey_name = winreg.EnumKey(base_key, i)
        return subkey_name
    except Exception as e:
        print(e)


def get_value(base, i):
    try:
        value_name, value_data, value_type = winreg.EnumValue(base, i)
        return [value_name, value_data, value_type]
    except Exception as e:
        print(e)


def get_file_mru_data(base_path, subkey_name):
    file_mru_path = f"{base_path}\\{subkey_name}\\File MRU"

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, file_mru_path) as file_mru_key:
        # Get number of values in File MRU
        num_values = winreg.QueryInfoKey(file_mru_key)[1]
        print(f"Found {num_values} MRU entries")
        mru_files: list[RecentFile] = []
        for j in range(num_values):
            try:
                value_name, value_data, value_type = winreg.EnumValue(file_mru_key, j)

                # Skip the MRU order value
                if value_name.upper() == "MRU":
                    print(f"MRU Order: {value_data}")
                    continue

                # Process file path
                if not isinstance(value_data, str):
                    continue

                match = parse_mru_entry(value_data)
                if not match:
                    continue
                mru_files.append(match)

            except Exception as e:
                print(f"Error reading value {j}: {e}")

        return mru_files


def get_office_MRU(base_path):
    files: list[RecentFile] = []
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, base_path) as base_key:
            print(f"Successfully opened: HKEY_CURRENT_USER\\{base_path}")

            num_subkeys = winreg.QueryInfoKey(base_key)[0]
            print(f"Found {num_subkeys} user profile(s)")

            subkeys = [get_subkeys(base_key, i) for i in range(num_subkeys)]
            subkeys = [x for x in subkeys if x]
            print(subkeys)

            for k in subkeys:
                files.extend(get_file_mru_data(base_path, k))
    except Exception as e:
        print(e)

    return files




def search_registry_for_str(search_txt:str, root=winreg.HKEY_CURRENT_USER, path=""):
    LOOK_FOR = re.compile(r"xlsx", re.I)
    try:
        with winreg.OpenKey(root, path) as k:
            # search values in the current key
            for i in itertools.count():
                try:
                    name, data, _ = winreg.EnumValue(k, i)
                    if isinstance(data, str) and LOOK_FOR.search(data):
                        print(rf"{root}\\{path}\\{name} -> {data.split('*', 1)[-1]}")
                except OSError:  # no more values
                    break

            # recurse into sub-keys
            sub_count, _, _ = winreg.QueryInfoKey(k)
            for j in range(sub_count):
                sub = winreg.EnumKey(k, j)
                new_path = f"{path}\\{sub}" if path else sub  # <- fix
                search_registry_for_str(search_txt, root, new_path)

    except (PermissionError, FileNotFoundError):
        # skip keys we can't open, or that vanished between EnumKey and OpenKey
        pass




def _resolve_lnk(path):
    """
    Return the real target of a Windows .lnk file
    Requires pywin32 (pip install pywin32) which ships with
    the standard WinPython and many corporate images.
    """
    import win32com.client  # noqa: E402

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(str(path))
    return shortcut.TargetPath or ""  # '' if dangling


def _parse_url(path):
    """
    Extract URL=… line from an .url text file.
    (These are just INI files.)
    """
    with path.open(encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.lower().startswith("url="):
                return line[4:].strip()
    return ""


def app_data_recent_files(path:Path):
    results:list[RecentFile] = []
    if not path.is_dir():
        return results

    for entry in path.glob("*"):
        url = False
        target = ""
        if entry.suffix.lower() == ".lnk":
            with contextlib.suppress(Exception):
                target = _resolve_lnk(entry)
                path = Path(target)
                if path.is_dir():
                    continue
        elif entry.suffix.lower() == ".url":
            target = _parse_url(entry)
            if target.endswith('/'):
                continue
            url = True

        if target:
            opened = datetime.fromtimestamp(
                entry.stat().st_mtime,  # ‘last modified’ of the shortcut
                tz=timezone.utc,  # convert to UTC; localise later if you like
            ).astimezone()  # become local time (America/Chicago for you)
            results.append(
                RecentFile(
                    path=target,
                    url=url,
                    timespamp=opened
                )
            )

    return results

def collect_appdata_recent(file_list:list[RecentFile],path:Path):
    try:
        r = app_data_recent_files(path)
        print(f'{path}: {len(r)}')
        
        file_list.extend(r)
    except Exception as e:
        print(e)
    return file_list

def get_recent_file_data():
    OfficeApps = [
        "Excel",
        "Word",
        "PowerPoint",
        "Access",
    ]

    files: list[RecentFile] = []

    for app in OfficeApps:
        base_path = rf"Software\Microsoft\Office\16.0\{app}\User MRU"
        files.extend(get_office_MRU(base_path))


    appdata_path = os.getenv("APPDATA")
    if appdata_path:
        collect_appdata_recent(files,Path(appdata_path) / r"Microsoft\Office\Recent")
        collect_appdata_recent(files,Path(appdata_path) / r"Microsoft\Windows\Recent")
    
    files.sort(key=lambda x: f'{x.timespamp}', reverse=True)

    result:list[dict[str, Any]] = []
    paths = set()

    for f in files:
        d = f.dict_for_batch()
        if not d:
            continue
        if f.path in paths:
            continue
        paths.add(f.path)
        result.append(d)

    return result

