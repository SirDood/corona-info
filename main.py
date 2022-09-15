import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
SOURCE_DIR = PROJECT_ROOT / "coronainfo"
DATA_DIR = PROJECT_ROOT / "data"

GRESOURCE_XML = DATA_DIR / "com.izzthedude.CoronaInfo.gresource.xml"
GRESOURCE_BIN = DATA_DIR / "gresource"

GSCHEMA_SRC = Path(DATA_DIR)
GSCHEMA_DEST = Path.home() / ".local" / "share" / "glib-2.0" / "schemas"
GSCHEMA_DEST.mkdir(parents=True, exist_ok=True)

SCICONS_SRC = DATA_DIR / "icons" / "hicolor" / "scalable" / "apps"
SCICONS_DEST = Path.home() / ".icons" / "hicolor" / "scalable" / "apps"
SCICONS_DEST.mkdir(parents=True, exist_ok=True)

SYICONS_SRC = DATA_DIR / "icons" / "hicolor" / "symbolic" / "apps"
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
    # Set environment variable(s)
    os.environ["CORONAINFO_DEBUG"] = "1"

    # Compile resources
    print("Compiling resources... ", end="")
    command = [
        "glib-compile-resources",
        f"--sourcedir={DATA_DIR}",
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
    from gi.repository import Gio
    resource = Gio.Resource.load(str(GRESOURCE_BIN))
    resource._register()

    # Run app
    from coronainfo import app
    code = app.main()

    # Delete icons after app quits
    for icon in installed_icons:
        print(f"Deleting:", icon)
        os.remove(icon)

    sys.exit(code)


if __name__ == "__main__":
    main()
