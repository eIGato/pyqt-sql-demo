import sys

from fbs_runtime.application_context.PyQt5 import ApplicationContext

from components.main_window import MainWindow

if __name__ == '__main__':
    appctxt = ApplicationContext()
    window = MainWindow()
    window.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
