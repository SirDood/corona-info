import os
import subprocess
import sys

from coronainfo.models import CoronaModel


def main(*args):
    model = CoronaModel(*args)
    data = model.get_data()

    for country in data:
        print(country)


def main_ui():
    from gi.repository import Gio

    SOURCE_DIR = os.path.join(os.path.dirname(__file__), "coronainfo")
    GRESOURCE_XML = os.path.join(SOURCE_DIR, "coronainfo.gresource.xml")
    GRESOURCE_BIN = os.path.join(SOURCE_DIR, "resources", "gresource")

    command = [
        "glib-compile-resources",
        f"--sourcedir={SOURCE_DIR}",
        f"--target={GRESOURCE_BIN}",
        GRESOURCE_XML
    ]
    subprocess.call(command)

    resource = Gio.Resource.load(GRESOURCE_BIN)
    resource._register()

    from coronainfo import app
    sys.exit(app.main("0.1.0"))


if __name__ == "__main__":
    sys_args = sys.argv[1:]
    # main(*sys_args)
    main_ui()
