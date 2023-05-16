import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QGridLayout, QSpacerItem, QSizePolicy, QFrame


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        grid_layout = QGridLayout()
        left_layout = QHBoxLayout()
        right_layout = QHBoxLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setContentsMargins(10, 0, 10, 0)
        right_layout.setContentsMargins(10, 0, 10, 0)

        # 标题栏左侧的最小化、最大化和关闭按钮
        close_button = QPushButton("✕", self)
        close_button.setFixedSize(20, 20)
        close_button.setObjectName("CloseButton")
        minimize_button = QPushButton("—", self)
        minimize_button.setFixedSize(20, 20)
        minimize_button.setObjectName("MinimizeButton")
        # 标题栏的标题
        title_label = QLabel(parent.windowTitle() if parent else "Title", self)
        title_label.setObjectName("TitleLabel")
        # left grid_layout
        left_layout.addWidget(close_button)
        left_layout.addWidget(minimize_button)
        spacer_item = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        left_layout.addSpacerItem(spacer_item)
        # right_layout
        # 添加进入GridLayout
        grid_layout.addLayout(left_layout, 0, 0, Qt.AlignVCenter)
        grid_layout.addWidget(title_label, 0, 1, Qt.AlignCenter)
        grid_layout.addLayout(right_layout, 0, 2, Qt.AlignVCenter)
        # 获取父窗口宽度
        parent_width = (parent.width() if parent else 520) - 20
        # 设置每列的宽度或最小宽度
        column_width = parent_width // 3
        grid_layout.setColumnMinimumWidth(0, column_width)
        grid_layout.setColumnMinimumWidth(1, column_width)
        grid_layout.setColumnMinimumWidth(2, column_width)
        self.setLayout(grid_layout)

