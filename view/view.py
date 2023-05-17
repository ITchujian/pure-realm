import os
import sys
from threading import Thread
from PyQt5.QtCore import Qt, QProcess, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QBitmap, QPainter
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem, QFileDialog, QProgressBar, QDesktopWidget)
from view.title_bar import TitleBar
from view.dialog import CustomDialog
from controller.controller import Controller


class DetectionThread(QThread):
    finished = pyqtSignal()
    detected = pyqtSignal(str, str)
    progress = pyqtSignal(int)

    def __init__(self, controller):
        self.controller = controller
        super().__init__()

    def run(self):
        # 在这里实现检测流氓软件的功能
        total = len(self.controller.software_list)
        unit = 0
        for name, version, uninstall, feature in self.controller.software_list:
            if self.controller.is_malware_by_version(name, version) or self.controller.is_malware_by_feature(name,
                                                                                                             feature):
                self.detected.emit(name, version)
            unit += int((1 / total) * 100)
            self.progress.emit(unit)
        self.progress.emit(100)
        self.finished.emit()


class UninstallThread(QThread):
    finished = pyqtSignal()
    uninstalled = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, item: QListWidgetItem, controller):
        self.item = item
        self.controller = controller
        super().__init__()

    def run(self):
        # 在这里实现卸载流氓软件的功能
        if self.controller.uninstall_software(self.item.text()):
            print("卸载成功")
            self.progress.emit(50)
            self.uninstalled.emit()
            for f in self.controller.get_malware_folder(self.item.text(), self.item.data(8888)):
                print(f"发现残余文件夹 {f}")
                Controller.safe_delete_folder(folder=f)
            self.progress.emit(100)
            self.finished.emit()
        else:
            print("未卸载")


class MainWindow(QMainWindow):
    def __init__(self, controller: Controller):
        self.controller = controller
        self.list_widget = None
        self.progress_bar = None
        self.detect_thread = None
        self.uninstall_thread = None
        self.move_tag = False
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 设置主窗口的大小和位置
        self.resize(520, 322)

        # 设置主窗口的图标的标题
        self.setWindowIcon(QIcon('path/to/your/icon.png'))
        self.setWindowTitle("人间净土")
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.center_window()

        # 创建一个 QWidget，作为主窗口的中心窗口
        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")
        self.setCentralWidget(central_widget)

        # 创建一个垂直布局，并设置为中心窗口的布局
        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(v_layout)

        # 创建一个title bar
        title_bar = TitleBar(self)
        v_layout.addWidget(title_bar)
        title_bar.findChild(QPushButton, 'MinimizeButton').clicked.connect(self.showMinimized)
        title_bar.findChild(QPushButton, 'CloseButton').clicked.connect(self.close)

        # 创建一个进度条，用于显示检测和卸载的进度
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setObjectName('ProgressBar')
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(True)
        v_layout.addWidget(self.progress_bar)

        # 创建一个水平布局，并添加到垂直布局中
        h_layout = QHBoxLayout()
        v_layout.addLayout(h_layout)

        # 创建一个“检测流氓软件”按钮，并添加到水平布局中
        detect_button = QPushButton('检  测', self)
        detect_button.setObjectName('DetectButton')
        detect_button.clicked.connect(self.detect)
        h_layout.addWidget(detect_button)

        # 创建一个“卸载流氓软件”按钮，并添加到水平布局中
        uninstall_button = QPushButton('卸  载', self)
        uninstall_button.setObjectName('UninstallButton')
        uninstall_button.clicked.connect(self.uninstall)
        h_layout.addWidget(uninstall_button)

        # 创建一个列表，用于显示检测到的流氓软件
        self.list_widget = QListWidget(self)
        self.list_widget.setObjectName('ListWidget')
        v_layout.addWidget(self.list_widget)

    def center_window(self):
        # 获取屏幕的几何信息
        screen_geometry = QDesktopWidget().availableGeometry()
        window_geometry = self.geometry()

        # 计算主窗口居中时的位置
        x = int((screen_geometry.width() - window_geometry.width()) / 2)
        y = int((screen_geometry.height() - window_geometry.height()) / 2)

        # 设置主窗口的位置
        self.move(x, y)

    def detect(self):
        self.controller.get_installed_software()
        self.progress_bar.setValue(0)
        self.list_widget.clear()
        self.detect_thread = DetectionThread(self.controller)
        self.detect_thread.detected.connect(self.add_to_list)
        self.detect_thread.finished.connect(self.detect_finished)
        self.detect_thread.progress.connect(self.update_progress_bar)
        self.detect_thread.start()

    def add_to_list(self, item, version):
        list_item = QListWidgetItem(item)
        list_item.setData(8888, version)
        self.list_widget.addItem(list_item)

    def detect_finished(self):
        self.progress_bar.setValue(0)

    def uninstall(self):
        self.progress_bar.setValue(0)
        items = self.list_widget.selectedItems()
        if len(items) > 0:
            item = items[0]
            self.uninstall_thread = UninstallThread(item, self.controller)
            self.uninstall_thread.uninstalled.connect(self.remove_from_list)
            self.uninstall_thread.finished.connect(self.uninstall_finished)
            self.uninstall_thread.progress.connect(self.update_progress_bar)
            self.uninstall_thread.start()

    def remove_from_list(self):
        item = self.list_widget.selectedItems()[0]
        self.list_widget.takeItem(self.list_widget.row(item))

    def uninstall_finished(self):
        self.progress_bar.setValue(0)
        self.detect()

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def mousePressEvent(self, a0) -> None:
        self.move_tag = True
        self.mouse_x = a0.globalX()
        self.mouse_y = a0.globalY()
        # print(self.mouse_x, self.mouse_y)
        self.origin_x = self.x()
        self.origin_y = self.y()
        # print(self.origin_x, self.origin_y)

    def mouseMoveEvent(self, a0) -> None:
        if self.move_tag:
            move_x = a0.globalX() - self.mouse_x
            move_y = a0.globalY() - self.mouse_y
            # print(move_x, move_y)
            target_x = self.origin_x + move_x
            target_y = self.origin_y + move_y
            self.move(target_x, target_y)

    def mouseReleaseEvent(self, a0) -> None:
        self.move_tag = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
