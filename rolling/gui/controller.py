# coding: utf-8
import urwid

from rolling.client.http.client import HttpClient
from rolling.gui.view import View


class Controller(object):
    def __init__(self, client: HttpClient) -> None:
        self._client = client
        self._loop = None
        self._view = View(self)

    @property
    def loop(self):
        return self._loop

    def main(self) -> None:
        self._loop = urwid.MainLoop(self._view, palette=[])
        self._loop.run()