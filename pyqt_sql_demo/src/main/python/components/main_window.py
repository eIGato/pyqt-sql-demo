from PyQt5.Qt import (
    QAction,
    QMainWindow,
    QTabWidget,
)

from .connection_widget import ConnectionWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(640)
        self.setMinimumHeight(480)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.on_tab_close_clicked)
        self.setCentralWidget(self.tab_widget)

        menu_bar = self.menuBar()
        connection_menu = menu_bar.addMenu('Connection')

        create_connection_action = QAction('Create', self)
        create_connection_action.triggered.connect(self.add_new_tab)
        connection_menu.addAction(create_connection_action)

        close_connection_action = QAction('Close', self)
        close_connection_action.triggered.connect(self.close_current_tab)
        connection_menu.addAction(close_connection_action)

        self.add_new_tab()

    def add_new_tab(self):
        connection_widget = ConnectionWidget(self.tab_widget)
        connection_widget.title_changed.connect(self.on_tab_name_changed)
        self.tab_widget.addTab(connection_widget, 'Untitled')

    def close_current_tab(self):
        idx = self.tab_widget.currentIndex()
        self.tab_widget.removeTab(idx)

    def on_tab_close_clicked(self, idx):
        self.tab_widget.removeTab(idx)

    def on_tab_name_changed(self, widget, name):
        idx = self.tab_widget.indexOf(widget)
        if idx != -1:
            self.tab_widget.setTabText(idx, name)
