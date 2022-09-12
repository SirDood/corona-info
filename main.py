import os
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE_DIR = Path(__file__).parent / "coronainfo"
GRESOURCE_XML = SOURCE_DIR / "coronainfo.gresource.xml"
GRESOURCE_BIN = SOURCE_DIR / "resources" / "gresource"

GSCHEMA_SRC = Path(__file__).parent / "data"
GSCHEMA_DEST = Path.home() / ".local" / "share" / "glib-2.0" / "schemas"
GSCHEMA_DEST.mkdir(parents=True, exist_ok=True)

SCICONS_SRC = SOURCE_DIR.parent / "data" / "icons" / "hicolor" / "scalable" / "apps"
SCICONS_DEST = Path.home() / ".icons" / "hicolor" / "scalable" / "apps"
SCICONS_DEST.mkdir(parents=True, exist_ok=True)

SYICONS_SRC = SOURCE_DIR.parent / "data" / "icons" / "hicolor" / "symbolic" / "apps"
SYICONS_DEST = Path.home() / ".icons" / "hicolor" / "symbolic" / "apps"
SYICONS_DEST.mkdir(parents=True, exist_ok=True)


def install_icons(source: Path, destination: Path):
    icons_list = []
    for file in source.iterdir():
        if file.is_file() and file.suffix == ".svg":
            dest = destination / file.name
            print(f"Installing: {file} -> {dest}")
            icons_list.append(dest)
            shutil.copy(file, destination)

    return icons_list


def main():
    from gi.repository import Gio

    # Compile resources
    print("Compiling resources... ", end="")
    command = [
        "glib-compile-resources",
        f"--sourcedir={SOURCE_DIR}",
        f"--target={GRESOURCE_BIN}",
        GRESOURCE_XML
    ]
    subprocess.call(command)
    print("Done!")

    # Compile schemas
    print("Compiling gschemas... ", end="")
    command = [
        "glib-compile-schemas",
        GSCHEMA_SRC,
        f"--targetdir={GSCHEMA_DEST}"
    ]
    subprocess.call(command)
    print("Done!")

    # Install icons
    installed_icons = install_icons(SCICONS_SRC, SCICONS_DEST) + install_icons(SYICONS_SRC, SYICONS_DEST)

    # Load resources
    resource = Gio.Resource.load(str(GRESOURCE_BIN))
    resource._register()

    # Run app
    from coronainfo import app
    from coronainfo.enums import App
    code = app.main(App.VERSION)

    # Delete icons after app quits
    for icon in installed_icons:
        print(f"Deleting:", icon)
        os.remove(icon)

    sys.exit(code)


if __name__ == "__main__":
    main()
