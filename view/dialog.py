from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout


class CustomDialog(QDialog):
    def __init__(self, title: str, content: str, ok_text: str = None, cancel_text: str = None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.title = title
        self.content = content

        self.title_label = QLabel(title)
        self.title_label.setObjectName("TitleLabel")

        self.content_label = QLabel(content)
        self.content_label.setObjectName("ContentLabel")

        self.close_button = QPushButton(cancel_text or "取消")
        self.close_button.setObjectName("CloseButton")
        self.close_button.clicked.connect(self.close)

        self.ok_button = QPushButton(ok_text or "确定")
        self.ok_button.setObjectName("OKButton")
        self.ok_button.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.close_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label, alignment=Qt.AlignTop)
        layout.addWidget(self.content_label)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(255, 255, 255, 230)  # 半透明白色背景
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)  # 圆角矩形

    def show_close_button(self, visible: bool):
        self.close_button.setVisible(visible)

    def show_ok_button(self, visible: bool):
        self.ok_button.setVisible(visible)

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
