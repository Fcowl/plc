from PyQt5 import QtCore, QtWidgets


class ProcessInfoWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._build_ui()
        self._fill_placeholder_processes()

    def _build_ui(self):
        self.setMinimumSize(760, 420)

        root_layout = QtWidgets.QVBoxLayout(self)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        self.header_input = QtWidgets.QLineEdit()
        self.header_input.setPlaceholderText("placeholder name")
        self.header_input.setMinimumHeight(34)
        root_layout.addWidget(self.header_input)

        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setSpacing(16)
        root_layout.addLayout(content_layout)

        content_layout.addWidget(self._build_left_panel(), 3)
        content_layout.addWidget(self._build_right_panel(), 4)

        self.setStyleSheet(
            """
            QWidget {
                background-color: #f6f1ea;
                color: #222222;
                font-size: 14px;
            }
            QLineEdit, QListWidget, QFrame {
                background-color: #fffdf9;
                border: 2px solid #1f1f1f;
                border-radius: 6px;
            }
            QLineEdit {
                padding: 6px 10px;
            }
            QListWidget {
                padding: 6px;
            }
            QListWidget::item {
                min-height: 48px;
                padding: 8px 10px;
                margin: 4px 0;
                border: 2px solid transparent;
            }
            QListWidget::item:selected {
                background-color: #ebe2d5;
                border: 2px solid #1f1f1f;
                color: #222222;
            }
            QLabel[role="title"] {
                font-size: 17px;
                font-weight: 600;
            }
            QLabel[role="subtitle"] {
                font-size: 22px;
                font-weight: 600;
            }
            QLabel[role="meta"] {
                font-size: 16px;
            }
            """
        )

    def _build_left_panel(self):
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        title = QtWidgets.QLabel("Список процессов")
        title.setProperty("role", "title")
        layout.addWidget(title)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.currentTextChanged.connect(self._update_selected_process)
        layout.addWidget(self.list_widget)

        return panel

    def _build_right_panel(self):
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.process_name_label = QtWidgets.QLabel("process_name.exe")
        self.process_name_label.setProperty("role", "subtitle")
        layout.addWidget(self.process_name_label)

        layout.addWidget(self._create_info_row("Запусков сегодня", "00"))
        layout.addWidget(self._create_info_row("Последний запуск", "--:--"))
        layout.addWidget(self._create_info_row("Время за день", "00:00:00"))
        layout.addWidget(self._create_info_row("Среднее время", "00:00:00"))

        calendar_title = QtWidgets.QLabel("Календарь запусков")
        calendar_title.setProperty("role", "title")
        calendar_title.setAlignment(QtCore.Qt.AlignHCenter)
        layout.addWidget(calendar_title)

        self.calendar_placeholder = QtWidgets.QFrame()
        self.calendar_placeholder.setMinimumSize(240, 210)
        calendar_layout = QtWidgets.QVBoxLayout(self.calendar_placeholder)
        calendar_layout.setContentsMargins(16, 16, 16, 16)

        calendar_placeholder_label = QtWidgets.QLabel("placeholder")
        calendar_placeholder_label.setAlignment(QtCore.Qt.AlignCenter)
        calendar_placeholder_label.setProperty("role", "meta")
        calendar_layout.addStretch()
        calendar_layout.addWidget(calendar_placeholder_label)
        calendar_layout.addStretch()

        layout.addWidget(self.calendar_placeholder, alignment=QtCore.Qt.AlignHCenter)
        layout.addStretch()

        return panel

    def _create_info_row(self, label_text, value_text):
        row = QtWidgets.QFrame()
        row_layout = QtWidgets.QHBoxLayout(row)
        row_layout.setContentsMargins(12, 10, 12, 10)
        row_layout.setSpacing(12)

        label = QtWidgets.QLabel(label_text)
        value = QtWidgets.QLabel(value_text)
        value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        value.setProperty("role", "meta")

        row_layout.addWidget(label)
        row_layout.addStretch()
        row_layout.addWidget(value)

        return row

    def _fill_placeholder_processes(self):
        placeholder_items = [
            "browser.exe",
            "game_launcher.exe",
            "editor.exe",
            "music_player.exe",
        ]
        self.list_widget.addItems(placeholder_items)
        self.list_widget.setCurrentRow(0)

    def _update_selected_process(self, process_name):
        self.process_name_label.setText(process_name or "process_name.exe")


class ProcessInfoDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, title="Информация о процессе"):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.resize(860, 520)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.process_info = ProcessInfoWidget(self)
        layout.addWidget(self.process_info)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = ProcessInfoDialog()
    window.show()
    app.exec_()
