from PyQt5.Qt import (
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    Qt,
)
from PyQt5.QtCore import pyqtSignal

from .connection_model import ConnectionModel
from .error_handler import ErrorHandler

DEFAULT_CONNECTION_LINE = ':memory:'


class ConnectionWidget(QWidget):
    title_changed = pyqtSignal(QWidget, str, name='title_changed')

    def __init__(self, parent):
        super().__init__(parent)
        self.title = 'Untitled'
        self.model = ConnectionModel(self)
        self.model.connected.connect(self.on_connection_changed)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        control_bar = self.init_control_bar()
        layout.addWidget(control_bar)
        workspace = self.init_workspace()
        layout.addWidget(workspace)
        self.setLayout(layout)

    def init_control_bar(self):
        control_row_layout = QHBoxLayout(self)
        control_row_layout.setContentsMargins(0, 0, 0, 0)
        db_combo_box = QComboBox(self)
        db_combo_box.addItem('SQLite')
        # db_combo_box.addItem('PostgreSQL')
        control_row_layout.addWidget(db_combo_box)
        self.connection_line = QLineEdit(self)
        self.connection_line.setPlaceholderText(DEFAULT_CONNECTION_LINE)
        self.connection_line.setText('')
        control_row_layout.addWidget(self.connection_line)
        connection_button = QPushButton(self)
        connection_button.setText('Connect')
        connection_button.clicked.connect(self.on_connect_click)
        control_row_layout.addWidget(connection_button)
        control_row = QWidget(self)
        control_row.setLayout(control_row_layout)
        return control_row

    def init_workspace(self):
        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Vertical)
        splitter.sizePolicy().setVerticalPolicy(QSizePolicy.Maximum)
        query_edit = self.init_query_text_edit()
        self.on_disconnected()
        splitter.addWidget(query_edit)
        results_widget = self.init_results_widget()
        splitter.addWidget(results_widget)
        splitter.setSizes([100, 900])
        return splitter

    def init_query_text_edit(self):
        query_edit_layout = QVBoxLayout(self)
        query_edit_layout.setContentsMargins(0, 0, 0, 0)

        query_control_layout = QHBoxLayout(self)
        query_control_layout.setContentsMargins(0, 0, 0, 0)

        self.query_execute_button = QPushButton('Execute', self)
        self.query_execute_button.clicked.connect(self.on_execute_click)
        query_control_layout.addWidget(self.query_execute_button)

        self.query_fetch_button = QPushButton('Fetch', self)
        self.query_fetch_button.clicked.connect(self.on_fetch_click)
        self.model.fetch_changed.connect(self.on_fetch_changed)
        query_control_layout.addWidget(self.query_fetch_button)

        self.query_commit_button = QPushButton('Commit', self)
        self.query_commit_button.clicked.connect(self.on_connect_click)
        query_control_layout.addWidget(self.query_commit_button)

        self.query_rollback_button = QPushButton('Rollback', self)
        self.query_rollback_button.clicked.connect(self.on_rollback_click)
        query_control_layout.addWidget(self.query_rollback_button)

        query_control = QWidget(self)
        query_control.setLayout(query_control_layout)
        query_edit_layout.addWidget(query_control)

        self.query_text_edit = QTextEdit(self)
        self.query_text_edit.setText(
           "SELECT name FROM sqlite_master WHERE type='table'",
        )
        query_edit_layout.addWidget(self.query_text_edit)

        self.model.connected.connect(self.on_connected)
        self.model.disconnected.connect(self.on_disconnected)

        query_edit = QWidget(self)
        query_edit.setLayout(query_edit_layout)
        query_edit.sizePolicy().setVerticalPolicy(QSizePolicy.Minimum)
        return query_edit

    def init_results_widget(self):
        results_widget = QTabWidget(self)
        results_widget.setTabsClosable(False)
        table_view = QTableView(self)
        table_view.setModel(self.model)
        table_view.sizePolicy().setVerticalPolicy(
            QSizePolicy.MinimumExpanding)
        results_widget.addTab(table_view, 'Data')
        log = QTextEdit(self)
        log.setReadOnly(True)
        self.model.executed.connect(log.append)
        results_widget.addTab(log, 'Events')
        return results_widget

    def on_connect_click(self):
        with ErrorHandler():
            connection_string = (
                self.connection_line.text()
                or DEFAULT_CONNECTION_LINE
            )
            self.model.connect(connection_string)

    def on_execute_click(self):
        with ErrorHandler():
            query = self.query_text_edit.toPlainText()
            self.model.execute(query)

    def on_fetch_click(self):
        with ErrorHandler():
            self.model.fetch_more()

    def on_rollback_click(self):
        with ErrorHandler():
            self.model.rollback()

    def on_connected(self):
        self.query_commit_button.setEnabled(True)
        self.query_execute_button.setEnabled(True)
        self.query_fetch_button.setEnabled(False)
        self.query_rollback_button.setEnabled(True)
        self.query_text_edit.setEnabled(True)

    def on_disconnected(self):
        self.query_commit_button.setEnabled(False)
        self.query_execute_button.setEnabled(False)
        self.query_fetch_button.setEnabled(False)
        self.query_rollback_button.setEnabled(False)
        self.query_text_edit.setEnabled(False)

    def on_fetch_changed(self, state):
        self.query_fetch_button.setEnabled(state)

    def on_connection_changed(self, name):
        self.title_changed.emit(self, name)
