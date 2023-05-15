import os
import sys
from PyQt5.QtCore import Qt, QProcess, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem, QFileDialog, QProgressBar)


class DetectionThread(QThread):
    finished = pyqtSignal()
    detected = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        # 在这里实现检测流氓软件的功能
        for i in range(1, 101):
            self.progress.emit(i)
        self.detected.emit('2345全家桶')
        self.detected.emit('腾讯QQ电脑管家')
        self.detected.emit('百度卫士')
        self.finished.emit()


class UninstallThread(QThread):
    finished = pyqtSignal()
    uninstalled = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, item):
        super().__init__()
        self.item = item

    def run(self):
        # 在这里实现卸载流氓软件的功能
        for i in range(1, 101):
            self.progress.emit(i)
        self.uninstalled.emit()
        self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        self.list_widget = None
        self.progress_bar = None
        self.detect_thread = None
        self.uninstall_thread = None
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置主窗口的大小和位置
        self.setGeometry(100, 100, 520, 322)

        # 设置主窗口的图标的标题
        self.setWindowIcon(QIcon('path/to/your/icon.png'))
        self.setWindowTitle("人间净土")

        # 创建一个 QWidget，作为主窗口的中心窗口
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 创建一个垂直布局，并设置为中心窗口的布局
        v_layout = QVBoxLayout()
        central_widget.setLayout(v_layout)

        # 创建一个标签，并设置为标题
        label = QLabel('人间净土', self)
        label.setAlignment(Qt.AlignCenter)
        label.setObjectName('TitleLabel')
        v_layout.addWidget(label)

        # 创建一个水平布局，并添加到垂直布局中
        h_layout = QHBoxLayout()
        v_layout.addLayout(h_layout)

        # 创建一个“检测流氓软件”按钮，并添加到水平布局中
        detect_button = QPushButton('检测流氓软件', self)
        detect_button.setObjectName('DetectButton')
        detect_button.clicked.connect(self.detect)
        h_layout.addWidget(detect_button)

        # 创建一个“卸载流氓软件”按钮，并添加到水平布局中
        uninstall_button = QPushButton('卸载流氓软件', self)
        uninstall_button.setObjectName('UninstallButton')
        uninstall_button.clicked.connect(self.uninstall)
        h_layout.addWidget(uninstall_button)

        # 创建一个列表，用于显示检测到的流氓软件
        self.list_widget = QListWidget(self)
        self.list_widget.setObjectName('ListWidget')
        v_layout.addWidget(self.list_widget)

        # 创建一个进度条，用于显示检测和卸载的进度
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setObjectName('ProgressBar')
        self.progress_bar.setVisible(True)
        v_layout.addWidget(self.progress_bar)

        # 设置窗口的样式表
        with open('./view/style.qss', 'r', encoding="utf-8") as f:
            self.setStyleSheet(f.read())
        # 显示主窗口
        self.show()

    def detect(self):
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.list_widget.clear()
        self.detect_thread = DetectionThread()
        self.detect_thread.detected.connect(self.add_to_list)
        self.detect_thread.finished.connect(self.detect_finished)
        self.detect_thread.progress.connect(self.update_progress_bar)
        self.detect_thread.start()

    def add_to_list(self, item):
        self.list_widget.addItem(item)

    def detect_finished(self):
        self.progress_bar.setVisible(True)

    def uninstall(self):
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        items = self.list_widget.selectedItems()
        if len(items) > 0:
            item = items[0]
            self.uninstall_thread = UninstallThread(item)
            self.uninstall_thread.uninstalled.connect(self.remove_from_list)
            self.uninstall_thread.finished.connect(self.uninstall_finished)
            self.uninstall_thread.progress.connect(self.update_progress_bar)
            self.uninstall_thread.start()

    def remove_from_list(self):
        item = self.list_widget.selectedItems()[0]
        self.list_widget.takeItem(self.list_widget.row(item))

    def uninstall_finished(self):
        self.progress_bar.setVisible(False)

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
