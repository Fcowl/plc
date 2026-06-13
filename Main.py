import json
import os
import time

import logging
import logging.handlers
import atexit
from types import TracebackType
from typing import Optional, Any
import inspect
from pathlib import Path
import colorlog

import psutil
import threading
import io
import sys
import argparse

from PyQt5 import QtWidgets, QtGui, QtCore


import pygetwindow as gw

from Interfaces.Process_btn import AddWindowDialog

global_buffer = io.BytesIO()
buffer_lock = threading.Lock()
LOGGING_LV = ''

@atexit.register
def exit_save():
    save_buffer_2_json('atExit save')

def load_logger():
    global LOGGING_LV
    open_method = 'a'
    # if Path(logging_path).stat().st_size > 209715200: #clears file if size > 25mb
    #     open_method = 'w'

    with open(LOGGING_PATH, open_method, encoding='utf-8') as f:
        f.write('\n')


    parser = argparse.ArgumentParser(description="Пример с логированием")

    parser.add_argument(
        "-l", "--log",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Уровень логирования"
    )

    args = parser.parse_args()
    logging_level = getattr(logging, args.log)
    LOGGING_LV = args.log

    file_formatter = logging.Formatter(
        '[{asctime} - {levelname} - {funcName} - {lineno}] {message}',
        style='{',
        #datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s[%(asctime)s - %(levelname)s - %(funcName)s] %(message)s',
        #datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )

    file_handler = logging.handlers.RotatingFileHandler(
        LOGGING_PATH, mode='a', maxBytes=0, backupCount=0, encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    logging.basicConfig(
        level=logging_level,
        handlers=[file_handler, console_handler]
    )
    logging.debug("Логгер запущен")

def exception_handler(exc_type:type[BaseException], exc_value:BaseException, exc_traceback: Optional[TracebackType]):
    if exc_value.__class__.__name__ == 'KeyboardInterrupt':
        logging.info('Exiting')
        sys.exit()
    logging.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit()

LOGGING_PATH = r'C:\Users\Fcowl\PycharmProject\playtime_counter\logs\playtime.log'
load_logger()
sys.excepthook = exception_handler

# ------------- json сохранение -------------
SAVE_FILE = r'C:\Users\Fcowl\PycharmProject\playtime_counter\all_in1.json'

def load_user_data(encoding:str = "UTF-8",filename:str|Path = SAVE_FILE):
    if not os.path.exists(filename):
        return {}
    with open(filename, "r", encoding=encoding) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_user_data(data:Any, filename:str|Path=SAVE_FILE):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def update_value(key:Any, value:Any, filename:str|Path=SAVE_FILE):
    data = load_user_data(filename)
    data[key] = value
    save_user_data(data)

def save_buffer_2_json(save_reason: str | None = None, filename: str = SAVE_FILE) -> None:
    """сохраняет инфу из буферов в джейсон"""
    data = read_io(global_buffer)
    data.pop('process_time')
    save_user_data(data, filename)
    logging.info(f'buffer saved (reason: {save_reason})')

# ------------- io сохранение -------------
def read_io(buffer: io.BytesIO) -> dict:

    try:
        with buffer_lock:
            buffer.seek(0)
            return json.loads(buffer.read().decode('utf-8'))
    except Exception as e:
        logging.critical(f'unhandled exception in count_tab1_runtime {e.__class__.__name__, e}')
        stack = [f.function for f in inspect.stack()]
        logging.critical(f"Path: {stack}")
        os._exit(0)

def wright_io(buffer: io.BytesIO, info) -> None:

    try:
        with buffer_lock:
            buffer.seek(0)
            buffer.truncate(0)
            buffer.write(json.dumps(info).encode('utf-8'))
    except Exception as e:
        logging.critical(f'unhandled exception in count_tab1_runtime {e.__class__.__name__, e}')
        stack = [f.function for f in inspect.stack()]
        logging.critical(f"Path: {stack}")
        os._exit(0)

def update_value_io(buffer: io.BytesIO, path: str, value) -> None:
    """Обновляет значение по пути вида 'a/b/c' в JSON"""
    data = read_io(buffer)
    keys = path.split('/')
    current = data
    # идём по всем ключам кроме последнего
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}  # создаём вложенность если её нет
        current = current[key]
    # обновляем последнее значение
    current[keys[-1]] = value
    wright_io(buffer, data)

def increment_value_io(buffer: io.BytesIO, path:str, step:int=1) -> None:
    data = read_io(buffer)
    keys = path.split('/')
    current = data
    for key in keys[:-1]:
        current = current.setdefault(key, {})
    current[keys[-1]] = current.get(keys[-1], 0) + step
    wright_io(buffer, data)

def get_pids_by_name(exe_name: str) -> list[int]:
    """Возвращает список PID всех процессов с указанным именем exe"""
    pids = []
    # Получаем список всех PID
    process_ids = win32process.EnumProcesses()

    for pid in process_ids:
        try:
            # Открываем процесс с правами на чтение информации
            h_process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)

            exe_path = win32process.GetModuleFileNameEx(h_process, 0)
            exe_file = os.path.basename(exe_path)

            if exe_file.lower() == exe_name.lower():
                pids.append(pid)

            win32api.CloseHandle(h_process)

        except pywintypes.error:  # Процесс может быть системным или недоступным — игнорируем
            pass
    return pids

def format_hms(seconds) -> str:
    seconds = round(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02}"


class PlaytimeCounter(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Счетчик плейтайма: {__file__.split('\\')[-1]} - {LOGGING_LV}")
        self.resize(450, 450)

        self.process_items: dict[str,QtWidgets.QTreeWidgetItem] = {}
        self.prev_games:list[str] = []
        self.prev_prev_games:list[str] = []

        self.win_items: dict[str,QtWidgets.QTreeWidgetItem] = {}
        self.prev_win:list[str] = []
        self.prev_prev_win:list[str] = []

        icon = QtGui.QIcon(r"C:\Users\Fcowl\PycharmProject\playtime_counter\dist\images.ico")
        self.setWindowIcon(icon)

        # Основной контейнер и layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QtWidgets.QVBoxLayout(central_widget)  # type: ignore

        # Вкладки
        self.tabs = QtWidgets.QTabWidget()
        self.layout.addWidget(self.tabs)  # type: ignore

        # === Первая вкладка (отслеживание по exe) ===
        self.tab_exe = QtWidgets.QWidget()
        tab1_layout = QtWidgets.QVBoxLayout(self.tab_exe)

        self.tree_tab1 = QtWidgets.QTreeWidget()
        self.column_count:int = 3
        self.tree_tab1.setColumnCount(self.column_count)
        self.tree_tab1.setHeaderLabels(["Имя процесса", "плейтайм (ч)", "process time"])
        self.tree_tab1.setColumnWidth(0, 170)

        # убираем стрелочки и отступы
        self.tree_tab1.setRootIsDecorated(False)
        self.tree_tab1.setItemsExpandable(False)
        self.tree_tab1.setUniformRowHeights(True)

        tab1_layout.addWidget(self.tree_tab1)
        self.tabs.addTab(self.tab_exe, "Счет по exe")

        # === Вторая вкладка (отслеживание по названию окна) ===
        self.tab_procName = QtWidgets.QWidget()
        tab2_layout = QtWidgets.QVBoxLayout(self.tab_procName)

        self.tree_tab2 = QtWidgets.QTreeWidget()
        self.tree_tab2.setColumnCount(self.column_count)
        self.tree_tab2.setHeaderLabels(["Имя окна", "плейтайм (ч)", "process time"])
        self.tree_tab2.setColumnWidth(0, 170)

        self.tree_tab2.setRootIsDecorated(False)
        self.tree_tab2.setItemsExpandable(False)
        self.tree_tab2.setUniformRowHeights(True)

        tab2_layout.addWidget(self.tree_tab2)
        self.tabs.addTab(self.tab_procName, "отслеживание по названию окна")

        self.tabs.currentChanged.connect(self.tab_switched_to)

        # === КНОПКИ ===
        self.new_process_btn = QtWidgets.QToolButton()
        self.new_process_btn.setText("Добавить процесс")
        self.new_process_btn.clicked.connect(self.open_add_process_dialog)
        self.new_process_btn.setMaximumWidth(200)

        self.remove_process_btn = QtWidgets.QToolButton()
        self.remove_process_btn.setText("Убрать процесс")
        self.remove_process_btn.clicked.connect(self.open_remove_process_dialog)
        self.remove_process_btn.setMaximumWidth(200)

        # === кнопки для второй вкладки ===
        self.new_win_title_btn = QtWidgets.QToolButton()
        self.new_win_title_btn.setText("Добавить окно")
        self.new_win_title_btn.clicked.connect(self.open_add_win_title_dialog)
        self.new_win_title_btn.setMaximumWidth(200)

        self.remove_win_title_btn = QtWidgets.QToolButton()
        self.remove_win_title_btn.setText("Убрать окно")

        self.remove_win_title_btn.clicked.connect(self.open_remove_win_title_dialog)
        self.remove_win_title_btn.setMaximumWidth(200)

        # кнопка настроек общая
        self.settings_btn = QtWidgets.QToolButton()
        self.settings_btn.setText("Настройки")
        self.settings_btn.clicked.connect(self.settings_dialog)
        self.settings_btn.setMaximumWidth(200)

        # нажатие на элемент таблицы

        self.tree_tab1.itemDoubleClicked.connect(lambda item, column: self.on_process_double_clicked(item, column, mode='process'))
        self.tree_tab2.itemDoubleClicked.connect(lambda item, column: self.on_process_double_clicked(item, column, mode='window'))

        self.button_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.timer_first_tab = QtCore.QTimer()
        self.timer_second_tab = QtCore.QTimer()
        self.tab_switched_to(0)

    def tab_switched_to(self, tab_num):
        self.update_buttons(tab_num)
        self.change_updating_tab(tab_num)

    def change_updating_tab(self, tab_num):
        if tab_num == 0:
            self.timer_first_tab.timeout.connect(self.update_exe_display)
            self.timer_first_tab.start(1000)
            self.update_exe_display()
            self.timer_second_tab.stop()

        if tab_num == 1:
            self.timer_second_tab.timeout.connect(self.update_win_display)
            self.timer_second_tab.start(1000)
            self.update_win_display()
            self.timer_first_tab.stop()

    def update_exe_display(self):
        global updates_counter
        data  = read_io(global_buffer)
        processes, active_processes_time = data['playtime'], data['process_time']

        self.setWindowTitle(f"Счетчик плейтайма: {__file__.split('\\')[-1]} - {LOGGING_LV}, {updates_counter}")

        # === Добавление и обновление процессов ===
        for proc_name, seconds in processes.items():
            time_str = format_hms(seconds)

            if proc_name in self.process_items:
                # обновляем существующую строку
                item = self.process_items[proc_name]
                item.setText(1, time_str)
                try:
                    item.setText(2, str(format_hms(active_processes_time[proc_name])))
                except KeyError:
                    item.setText(2, '')
            else:
                # создаём новую строку
                try:
                    item = QtWidgets.QTreeWidgetItem([proc_name, time_str, str(format_hms(active_processes_time[proc_name]))])
                except KeyError:
                    item = QtWidgets.QTreeWidgetItem([proc_name, time_str, ''])

                self.tree_tab1.addTopLevelItem(item)
                self.process_items[proc_name] = item

        # === Удаление процессов, которых больше нет ===
        for proc_name in list(self.process_items.keys()):
            if proc_name not in processes:
                item = self.process_items.pop(proc_name)
                index = self.tree_tab1.indexOfTopLevelItem(item)
                if index != -1:
                    self.tree_tab1.takeTopLevelItem(index)

        # === Обновление цвета строк (если используется подсветка активных игр) ===
        if updated_exes is not None:
            for proc_name, item in self.process_items.items():
                for column in range(self.column_count):
                    if type(item) is not QtWidgets.QTreeWidgetItem:
                        continue

                    if (proc_name not in self.prev_games) and (proc_name in updated_exes):
                        # новый процесс
                        item.setBackground(column, QtGui.QBrush(QtGui.QColor("#7fff00")))
                    elif (proc_name not in self.prev_games) and (proc_name not in updated_exes) and (
                            proc_name in self.prev_prev_games):
                        # удалённый
                        item.setBackground(column, QtGui.QBrush(QtGui.QColor("red")))
                    elif proc_name in updated_exes:
                        # активный
                        item.setBackground(column, QtGui.QBrush(QtGui.QColor("#cee8ff")))
                    else:  # неактивный
                        item.setBackground(column, QtGui.QBrush(QtGui.QColor("white")))

                    item.setForeground(column, QtGui.QBrush(QtGui.QColor("black")))

        # сохраняем предыдущие состояния
        self.prev_prev_games = self.prev_games
        self.prev_games = updated_exes
        self.tree_tab1.expandAll()

    def update_win_display(self):
        global updated_windows
        wins: dict = read_io(global_buffer)['win_title']
        #logging.debug(f"{wins=}")

        for window, seconds in wins.items():
            time_str = format_hms(seconds)
            if window in self.win_items:
                item = self.win_items[window]
                item.setText(1, time_str)
            else:
                item = QtWidgets.QTreeWidgetItem([window, time_str, ''])

            self.tree_tab2.addTopLevelItem(item)
            self.win_items[window] = item

        # === Удаление процессов, которых больше нет ===
        for window in list(self.win_items.keys()):
            if window not in wins:
                item = self.win_items.pop(window)
                index = self.tree_tab2.indexOfTopLevelItem(item)
                if index != -1:
                    self.tree_tab2.takeTopLevelItem(index)

        # === Обновление цвета строк (если используется подсветка активных игр) ===
        if updated_windows is not None:
            for window, item in self.win_items.items():
                for column in range(self.column_count):
                    if (window not in self.prev_win) and (window in updated_windows):
                        # новый процесс
                        item.setBackground(column, QtGui.QBrush(QtGui.QColor("#7fff00")))
                    elif (window not in self.prev_win) and (window not in updated_windows) and (
                            window in self.prev_prev_win):  # удалённый
                        item.setBackground(column, QtGui.QBrush(QtGui.QColor("red")))
                    elif window in updated_windows:
                        item.setBackground(column, QtGui.QBrush(QtGui.QColor("#cee8ff")))  # активный
                    else:
                        item.setBackground(column, QtGui.QBrush(QtGui.QColor("white")))  # неактивный
                    item.setForeground(column, QtGui.QBrush(QtGui.QColor("black")))

            #print(self.prev_win)
            self.prev_prev_win = self.prev_win
            self.prev_win = updated_windows

    # === кнопка добавления процесса ===
    def open_add_process_dialog(self):
        dialog = AddWindowDialog(self, mode="process", title='Добавить элемент')

        all_proc = sorted(set([proc.name() for proc in psutil.process_iter(['name']) if proc.name() != '' and
                               proc.name().endswith('.exe')]))
        dialog.list_widget.addItems(all_proc)

        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            return
        proc_name = dialog.get_selected()

        if not proc_name:
            return
        logging.info(f'app_process_to_track "{proc_name}"')

        exe_list = [exe for exe in read_io(global_buffer)['playtime'].keys()]
        if proc_name in exe_list:  # если введенный процесс в списке отслеживаемых exe
            QtWidgets.QMessageBox.warning(self, "Внимание", "Этот процесс уже есть в списке.")
            return

        if proc_name[-4:] != ".exe":
            QtWidgets.QMessageBox.warning(self, "Внимание", "название должно оканчиваться на .exe")
            return

        # обнова буфера, в основном цикле добавляется процесс
        update_value_io(global_buffer, f'playtime/{proc_name}', 0)
        save_buffer_2_json('add_proc_to_extra')

        QtWidgets.QMessageBox.information(self, "Успех", f"Процесс '{proc_name}' добавлен в список игр.")

    # === добавление окна (таб2)
    def open_add_win_title_dialog(self):
        dialog = AddWindowDialog(self, mode="window", title='Добавить элемент')

        all_wins = [window.title for window in gw.getAllWindows() if window.title != '']
        dialog.list_widget.addItems(all_wins)

        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            return
        window_to_add = dialog.get_selected()
        if not window_to_add:
            return

        if window_to_add in read_io(global_buffer)['playtime'].keys():
            QtWidgets.QMessageBox.warning(self, "Внимание", "Это окно уже есть в списке.")
            return

        update_value_io(global_buffer, f'win_title/{window_to_add}', 0)
        save_buffer_2_json('add_window_to_track')
        QtWidgets.QMessageBox.information(self, "Успех", f"Окно '{window_to_add}' добавлено в список.")


    #при нажатии на элемент таблицы
    def on_process_double_clicked(self, item:QtWidgets.QTreeWidgetItem, column:int, mode:str) -> None:
        proc_name = item.text(0)  # имя процесса из первой колонки
        print(type(item))
        print(f"Clicked: {proc_name},{column},{item.text(column)}")
        # todo usage

    def closeEvent(self, event) -> None:
        QtWidgets.qApp.quit()
        logging.info('user exit')


def count_tab1_runtime() -> None:
    global updated_exes,updates_counter
    updates_counter = 0
    while True:
        try:
            start_time = time.time()
            updated_exes = []

            # получение настроек
            playtime_recovery_setting: bool = read_io(global_buffer)['settings']['playtime_recovery']

            # получение списка exe для отслеживания
            exes_to_find: list[str] = [exe for exe in read_io(global_buffer)['playtime'].keys()]

            for process in psutil.process_iter():
                if process.name() not in exes_to_find or process.name() == 'System Idle Process' or process.name() in updated_exes:
                    continue

                if updates_counter == 0 and playtime_recovery_setting:
                    increment_value_io(global_buffer, f'playtime/{process.name()}', int(time.time() - process.create_time()))

                increment_value_io(global_buffer, f'playtime/{process.name()}')
                update_value_io(global_buffer, f'process_time/{process.name()}',int(time.time() - process.create_time()))

                updated_exes.append(process.name())
            updates_counter += 1


            # correct delay
            elapsed = time.time() - start_time
            logging.debug(f"est sleep_time={1 - elapsed} c; {updates_counter=}")
            sleep_time = max(1 - elapsed, 0)  # max для того чтобы длительность сна не могла быть отрицательной
            time.sleep(sleep_time)
            # todo fix error in this function randomly stopping
        except Exception as e:
            logging.critical(f'unhandled exception in count_tab1_runtime {e.__class__.__name__,e}')
            os._exit(0)

def count_tab2_runtime() -> None:
    global updated_windows
    while True:
        try:
            start_time = time.thread_time()
            updated_windows = []
            windows = gw.getAllWindows()
            windows_to_find = [k for k in load_user_data()['win_title']]

            for window in windows:
                window = window.title
                if (window is None) or (window not in windows_to_find) or (window in updated_windows):
                    continue

                increment_value_io(global_buffer, f"win_title/{window}")
                updated_windows.append(window)

            # correct delay
            elapsed = time.thread_time() - start_time
            logging.debug(f"est sleep_time={1-elapsed} c")
            sleep_time = max(1 - elapsed, 0)
            time.sleep(sleep_time)
        except Exception as e:
            logging.critical(f'unhandled exception in count_tab2_runtime {e.__class__.__name__,e}')
            os._exit(0)

def save_every_min() -> None:
    """сохраняет файлы из буферов в файлы джейсон с промежутком из настроек"""
    while True:
        try:
            time_ts = read_io(global_buffer)['settings']['autosave_every']
            if time_ts == 0:
                time.sleep(60)
                continue

            time.sleep(time_ts)
            save_buffer_2_json('autosave')
        except Exception as e:
            logging.critical(f'unhandled exception in save_every_min {e.__class__.__name__,e}')



if __name__ == '__main__':
    if len(get_pids_by_name(Path(__file__).name)) > 1:
        logging.error('приложение уже запущено')
        exit()
    logging.info('Playtime counter started')
    updated_exes: list[str] = []
    updated_windows: list[str] = []

    wright_io(global_buffer, load_user_data()) # начальная запись буфера

    threading.Thread(target=count_tab1_runtime, daemon=True).start()
    threading.Thread(target=count_tab2_runtime, daemon=True).start()
    threading.Thread(target=save_every_min, daemon=True).start()

    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    PlaytimeCounter:PlaytimeCounter = PlaytimeCounter()
    PlaytimeCounter.show()

    sys.exit(app.exec_())

# TODO разобраться с тем что когда тыкаешь на процесс,
# он выделяется тем же цветом что выделяются запущенные процессы\окна

# TODO добавить возможность сортировки процессов в списках (по плейтайму, алфавиту, и по дефолту)

# TODO сделать настройку по добавлению плейтайма процесса при добавлении в список
# (добавил игру с список отслеживания и время процесса добавилось автоматически)

# TODO при нажатии на процесс появление окна с подробной информацией
# (последний запуск, последняя длительность игры и тд)
# количество запусков, последняя длительность, последний запуск, среднее время, календарь запусков

#todo сделать корректировку, проверять чему равен ожидаемый результат для приложения с реальным (прошел час у приложения должен быть +3600с
#а на деле 3599, и корректировать несоответствие

#todo фикс бля хуйни с отчещением джейсон файла со всей инфой (бекап файл или ещё ченибуть)
