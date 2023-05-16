from view.view import *
from controller.controller import *
from controller.qss_loader import QSSLoader

if __name__ == '__main__':
    app = QApplication(sys.argv)
    if Controller.is_admin():
        controller = Controller()
        main_window = MainWindow(controller)
        QSSLoader.load(main_window, "view/qss/style.qss")
        main_window.show()
    else:
        dialog = CustomDialog("提示", "请右键以管理员身份运行本程序")
        dialog.show_close_button(False)
        QSSLoader.load(dialog, "view/qss/dialog.qss")
        dialog.show()
    sys.exit(app.exec_())
