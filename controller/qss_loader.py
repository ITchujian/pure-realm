from PyQt5.QtCore import QFile, QTextStream


class QSSLoader:
    @staticmethod
    def load(widget, file_path):
        file = QFile(file_path)
        if not file.open(QFile.ReadOnly | QFile.Text):
            return

        stream = QTextStream(file)
        stylesheet = stream.readAll()

        if not stylesheet:
            return

        widget.setStyleSheet(stylesheet)