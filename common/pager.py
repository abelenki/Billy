from __init__ import *

import logging

class Pager(object):

    _prev_cursor = None
    _next_cursor = None
    _first_cursor = None
    _results = None
    _gql = None
    _fetch_limit = 25

    def __init__(
        self,
        gql,
        current=None,
        first=None,
        ):
        self._prev_cursor = current
        self._first_cursor = first
        self._gql = gql

    def next(self):
        self._fetch_and_init_cursor()
        return self._next_cursor

    def first(self):
        if not self._first_cursor:
            return self._prev_cursor

        if self._prev_cursor == self._first_cursor:
            return

        return self._first_cursor

    def prev(self):
        if self._prev_cursor == self._first_cursor:
            return

        return self._prev_cursor

    def fetch(self, limit=None):
        self._fetch_limit = limit
        self._fetch_and_init_cursor()
        return self._results

    def _fetch_and_init_cursor(self):
        if self._results and self._next_cursor:
            logging.debug(self._prev_cursor)
            return

        if self._prev_cursor:
            self._gql.with_cursor(self._prev_cursor)

        self._results = self._gql.fetch(self._fetch_limit)
        self._next_cursor = self._gql.cursor()
