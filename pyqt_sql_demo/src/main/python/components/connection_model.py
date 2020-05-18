import os.path
import sqlite3

from PyQt5.Qt import (
    QAbstractTableModel,
    Qt,
)
from PyQt5.QtCore import pyqtSignal

from . import exceptions


class ConnectionModel(QAbstractTableModel):
    executed = pyqtSignal(str, name='executed')
    connected = pyqtSignal(str, name='connected')
    disconnected = pyqtSignal()
    fetch_changed = pyqtSignal(bool, name='fetch_changed')

    def __init__(self, parent):
        super().__init__(parent)
        self.url = None
        self.attempted_url = None
        self.connection = None
        self.cursor = None

        self._headers = []
        self._data = []
        self._row_count = 0
        self._column_count = 0

    def connect(self, connection_string):
        self.disconnect()
        self.attempted_url = connection_string.strip()
        self.verify_attempted_url()
        self.connection = sqlite3.connect(self.attempted_url)
        self.connection.row_factory = sqlite3.Row
        self.url = self.attempted_url
        self.connected.emit(self.url)
        self.executed.emit('Connected: ' + connection_string)

    def disconnect(self):
        # Attempt to disconnect
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None
        self.disconnected.emit()

    def verify_attempted_url(self):
        url = self.attempted_url
        if url == ':memory:':
            return
        if os.path.isfile(url):
            return
        raise exceptions.FileNotFoundError(url)

    def execute(self, query):
        self.cursor = self.connection.cursor()
        self.cursor.execute(query)
        first_row = self.cursor.fetchone()
        if first_row:
            self.beginResetModel()
            self._column_count = len(first_row)
            self._headers = first_row.keys()
            self._data = [first_row]
            self._row_count = 1
            self.endResetModel()
            self.fetch_more()
        else:
            self.beginResetModel()
            if self.cursor.description:
                self._headers = [h[0] for h in self.cursor.description]
                print('headers:', self._headers)
                self._column_count = len(self._headers)
            else:
                self._headers = []
                self._column_count = 0
            self._row_count = 0
            self._data = []
            self.endResetModel()
            self.fetch_changed.emit(False)
        self.executed.emit('Executed: ' + query)

    def fetch_more(self):
        limit = 500
        more = self.cursor.fetchmany(limit)
        if len(more) > 0:
            self.beginResetModel()
            count = self._row_count + len(more)
            print('fetched {} rows in total'.format(count))
            self._data.extend(more)
            self._row_count = count
            self.endResetModel()
        self.fetch_changed.emit(len(more) >= limit)

    def commit(self):
        self.connection.commit()
        self.executed.emit('Committed')

    def rollback(self):
        self.connection.rollback()
        self.executed.emit('Rollback')

    def rowCount(self, parent):
        return self._row_count

    def columnCount(self, parent):
        return self._column_count

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if len(self._headers) > 0:
                return self._headers[section]

    def data(self, index, role):
        if index.isValid() and role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
