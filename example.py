import sloop
import asyncio
import random


from PyQt5 import QtCore, QtWidgets


sloop.AUTO_CLOSE = True


class MainWindow(QtWidgets.QMainWindow):

    result_signal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout()
        self.button = QtWidgets.QPushButton("Press me")
        layout.addWidget(self.button)
        self.label1 = QtWidgets.QLabel("0")
        self.label2 = QtWidgets.QLabel("0")
        self.label3 = QtWidgets.QLabel("0")
        self.label4 = QtWidgets.QLabel("0")
        lay2 = QtWidgets.QHBoxLayout()
        lay2.addWidget(self.label1)
        lay2.addWidget(self.label2)
        lay2.addWidget(self.label3)
        lay2.addWidget(self.label4)
        layout.addLayout(lay2)
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        self.button.clicked.connect(self.button_click)
        self.result_signal.connect(self._handle_result)

    @sloop.wrap_coro()
    async def button_click(self, *args, **kwargs):
        await asyncio.sleep(random.random() * 10)
        label = random.choice([self.label1, self.label2, self.label3, self.label4])
        self.result_signal.emit(label)

    def _handle_result(self, data):
        text = int(data.text())
        text += 1
        data.setText(str(text))


def main():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
