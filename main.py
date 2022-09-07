import os
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE_DIR = Path(__file__).parent / "coronainfo"
GRESOURCE_XML = SOURCE_DIR / "coronainfo.gresource.xml"
GRESOURCE_BIN = SOURCE_DIR / "resources" / "gresource"

SCICONS_SRC = SOURCE_DIR.parent / "data" / "icons" / "hicolor" / "scalable" / "apps"
SCICONS_DEST = Path.home() / ".icons" / "hicolor" / "scalable" / "apps"
if not SCICONS_DEST.exists():
    SCICONS_DEST.mkdir(parents=True, exist_ok=True)

SYICONS_SRC = SOURCE_DIR.parent / "data" / "icons" / "hicolor" / "symbolic" / "apps"
SYICONS_DEST = Path.home() / ".icons" / "hicolor" / "symbolic" / "apps"
if not SYICONS_DEST.exists():
    SYICONS_DEST.mkdir(parents=True, exist_ok=True)

ICONS_LIST: list[Path] = []


def install_icons(source: Path, destination: Path):
    for file in source.iterdir():
        if file.is_file() and file.suffix == ".svg":
            dest = destination / file.name
            print(f"Installing: {file} -> {dest}")
            ICONS_LIST.append(dest)
            shutil.copy(file, destination)


def main():
    from gi.repository import Gio

    command = [
        "glib-compile-resources",
        f"--sourcedir={SOURCE_DIR}",
        f"--target={GRESOURCE_BIN}",
        GRESOURCE_XML
    ]
    subprocess.call(command)

    install_icons(SCICONS_SRC, SCICONS_DEST)
    install_icons(SYICONS_SRC, SYICONS_DEST)

    resource = Gio.Resource.load(str(GRESOURCE_BIN))
    resource._register()

    from coronainfo import app
    from coronainfo.enums import App
    code = app.main(App.VERSION)

    for icon in ICONS_LIST:
        print(f"Deleting:", icon)
        os.remove(icon)

    sys.exit(code)


if __name__ == "__main__":
    main()
