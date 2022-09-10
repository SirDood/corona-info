from gi.repository import GObject

from coronainfo.controllers.controller_main import MainController


class AppController(GObject.Object):
    __gtype_name__ = "AppController"

    _main_controller = None

    @classmethod
    def get_main_controller(cls):
        if not cls._main_controller:
            cls._main_controller = MainController()

        return cls._main_controller
