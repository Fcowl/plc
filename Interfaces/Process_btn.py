import logging

from PyQt5 import QtWidgets


class AddWindowDialog(QtWidgets.QDialog):
    def __init__(self, parent=None,mode:str=None,title:str=''):
        super().__init__(parent)

        self.mode = mode
        if self.mode not in ['window','process']:
            logging.critical('AddWindowDialog: Error: Режим отслеживания указан неверно')
            raise ValueError("")

        self.setWindowTitle(title)
        self.setMinimumWidth(400)

        layout = QtWidgets.QVBoxLayout(self)

        # --- Создаём вкладки ---
        self.tabs = QtWidgets.QTabWidget()
        layout.addWidget(self.tabs)

        # --------------------------
        # ВКЛАДКА 1 — ручной ввод
        # --------------------------
        tab_manual = QtWidgets.QWidget()
        manual_layout = QtWidgets.QVBoxLayout(tab_manual)

        if self.mode == "window":
            label_text = "Введите название окна:"
        else:
            label_text = "Введите имя процесса:"

        manual_layout.addWidget(QtWidgets.QLabel(label_text))

        self.line_edit = QtWidgets.QLineEdit()
        manual_layout.addWidget(self.line_edit)

        self.tabs.addTab(tab_manual, "Ввести вручную")

        # --------------------------
        # ВКЛАДКА 2 — список процессов
        # --------------------------
        tab_list = QtWidgets.QWidget()
        list_layout = QtWidgets.QVBoxLayout(tab_list)

        self.list_widget = QtWidgets.QListWidget()

        if self.mode == "window":
            list_label = "Окна:"
        else:
            list_label = "Процессы:"

        list_layout.addWidget(QtWidgets.QLabel(list_label))
        list_layout.addWidget(self.list_widget)

        self.tabs.addTab(tab_list, "Выбрать из списка")

        # --- OK / Cancel ---
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def get_selected(self):
        """
        Возвращает строку, выбранную пользователем:
        - либо из поля ввода
        - либо из выбранного процесса
        """

        # Если выбрана вкладка процессов
        if self.tabs.currentIndex() == 1:
            item = self.list_widget.currentItem()

            return item.text() if item else None


        # Если выбрана вкладка ручного ввода
        return self.line_edit.text().strip()

