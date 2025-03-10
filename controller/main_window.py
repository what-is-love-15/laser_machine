import sys
import socket
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QSpinBox, QFrame, \
    QHBoxLayout
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt


class LaserView(QWidget):
    def __init__(self, client):
        super().__init__()
        self.setFixedSize(500, 500)  # поле
        self.laser_position = (0, 0)  # позиция в начале
        self.past_positions = []  # прошлые линии
        self.is_on = False
        self.client = client  # ссылка на клиент для отправки команд

    def update_laser(self, x, y, is_on):
        self.past_positions.append(self.laser_position)
        self.laser_position = (x, y)
        self.is_on = is_on  # запомнили состояние
        self.update()  # перерисовываем поле

    def mouse_event(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            x = event.position().x()
            y = event.position().y()

            x_scaled = int(x / self.width() * 500)  # переводим координаты из пикселей в систему 500х500
            y_scaled = int(y / self.height() * 500)

            print(f'Клик {x_scaled}, {y_scaled}')

            self.client.send_command(f'MOVE {x_scaled} {y_scaled}', update_view=True)  # отправка команды MOVE

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(240, 240, 240))  # наш фон

        pen = QPen(Qt.GlobalColor.gray, 1, Qt.PenStyle.DotLine)  # рисуем сетку
        painter.setPen(pen)
        for i in range(0, 501, 50):
            painter.drawLine(i, 0, i, 500)
            painter.drawLine(0, i, 500, i)

        pen.setWidth(2)  # рисуем прошлые перемещения лазера
        pen.setColor(Qt.GlobalColor.darkGray)
        painter.setPen(pen)
        for i in range(1, len(self.past_positions)):
            painter.drawLine(*self.past_positions[i - 1], *self.past_positions[i])

        if self.is_on:  # рисуем текущее положение лазера
            color = Qt.GlobalColor.red
        else:
            color = Qt.GlobalColor.blue
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        x, y = self.laser_position
        painter.drawEllipse(x - 5, y - 5, 10, 10)  # кружок лазера


class LaserClient(QWidget):
    def __init__(self):
        super().__init__()

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # подключение к серверу
        self.client.connect(('localhost', 12345))

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        controls_layout = QVBoxLayout()
        layout = QHBoxLayout()

        self.laser_view = LaserView(self)  # поле для визуализации

        self.coord_x = QLineEdit(self)  # ввод x и y
        self.coord_x.setPlaceholderText('Введите X')
        self.coord_y = QLineEdit(self)
        self.coord_y.setPlaceholderText('Введите Y')
        controls_layout.addWidget(QLabel('Координаты:'))
        controls_layout.addWidget(self.coord_x)
        controls_layout.addWidget(self.coord_y)

        self.move_button = QPushButton('Двигаться', self)  # кнопка двигаться
        self.move_button.clicked.connect(self.send_move)
        controls_layout.addWidget(self.move_button)

        self.speed_box = QSpinBox(self)  # ползунок скорости
        self.speed_box.setRange(1, 10)
        self.speed_box.setValue(1)
        self.speed_box.valueChanged.connect(self.set_speed)
        controls_layout.addWidget(QLabel('Скорость:'))
        controls_layout.addWidget(self.speed_box)

        self.laser_on_button = QPushButton('Лазер ВКЛ', self)  # кнопки вкл и выкл
        self.laser_off_button = QPushButton('Лазер ВЫКЛ', self)
        self.laser_on_button.clicked.connect(lambda: self.send_command('LASER ON'))
        self.laser_off_button.clicked.connect(lambda: self.send_command('LASER OFF'))
        controls_layout.addWidget(self.laser_on_button)
        controls_layout.addWidget(self.laser_off_button)

        self.status_button = QPushButton('Проверить статус', self)  # кнопка статуса
        self.status_button.clicked.connect(self.get_status)
        controls_layout.addWidget(self.status_button)

        self.status_label = QLabel('Статус: неизвестно', self)  # поле для вывода статуса
        controls_layout.addWidget(self.status_label)

        layout.addLayout(controls_layout)
        layout.addWidget(self.laser_view)

        main_layout.addLayout(layout)
        self.setLayout(main_layout)
        self.setWindowTitle('Управление лазерным станком')
        self.show()

    def send_move(self):
        x = self.coord_x.text()
        y = self.coord_y.text()
        if x.isdigit() and y.isdigit():
            self.send_command(f'MOVE {x} {y}', update_view=True)

    def set_speed(self):
        speed = self.speed_box.value()
        self.send_command(f'SPEED {speed}')

    def get_status(self):
        self.send_command('STATUS', update_status=True)

    def send_command(self, command, update_status=False, update_view=False):
        try:
            self.client.send(command.encode())
            response = self.client.recv(1024).decode().strip()
            print(f'Ответ сервера: {response}')

            if update_status:
                self.status_label.setText(f'Статус: {response}')

            if update_view:
                parts = response.split()
                if len(parts) == 4 and parts[0] == 'OK':
                    x, y = int(parts[2]), int(parts[3])
                    is_on = self.laser_on_button.isChecked()
                    self.laser_view.update_laser(x, y, is_on)

        except Exception as e:
            self.status_label.setText(f'Ошибка: {e}')


app = QApplication(sys.argv)
window = LaserClient()
sys.exit(app.exec())
