# %%
import re
import os
from pathlib import Path
import subprocess

def run_print(command):

    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, env=os.environ
    )

    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)


root = Path(__file__).parent
os.chdir(root)
proj_file = root / "pyproject.toml"

toml_txt = proj_file.read_text()
#%%
for f in root.joinpath('fsearch').glob('*'):
    f.unlink()


qml_files = [x.relative_to(root) for x in root.joinpath("file_search").rglob("*.qml")]
py_files = [x.relative_to(root) for x in root.joinpath("file_search").rglob("*.py")]

files = qml_files + py_files

files_txt = ",\n".join([f'    "{f}"' for f in files])
files_txt = files_txt.replace("\\", "\\\\")
print(files_txt)

re.match(r"#files(.*)#files", toml_txt)

pattern = r"#files\n.*?\n    #files"
pattern = r"#files\n.*?\n    #files"

result = re.sub(
    pattern, lambda m: f"#files\n{files_txt}\n    #files", toml_txt, flags=re.DOTALL
)

proj_file.write_text(result)
# %%
run_print("pyside6-project.exe clean")
run_print("pyside6-project.exe qmllint")

for f in root.joinpath('fsearch').rglob('*.cpp'):
    f.unlink()
for f in root.joinpath('fsearch').rglob('*.json'):
    f.unlink()