import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel
from laser_machine.laser import LaserMachine


class LaserController(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Laser Controller")
        self.setGeometry(100, 100, 400, 300)

        self.laser_machine = LaserMachine()

        self.speed_label = QLabel("Set Speed:")  # установка скорости
        self.speed_input = QLineEdit()
        self.speed_input.setPlaceholderText("Enter speed")

        self.toggle_button = QPushButton("Turn On Laser")  # включенный лазер
        self.toggle_button.clicked.connect(self.toggle_laser)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.speed_label)
        self.layout.addWidget(self.speed_input)
        self.layout.addWidget(self.toggle_button)

        self.setLayout(self.layout)

    def toggle_laser(self):  # вкл/выкл лазер
        current_text = self.toggle_button.text()
        if current_text == "Turn On Laser":
            self.laser_machine.turn_on()
            self.toggle_button.setText("Turn Off Laser")
            print("Laser turned ON")
        else:
            self.laser_machine.turn_off()
            self.toggle_button.setText("Turn On Laser")
            print("Laser turned OFF")

    def move(self):
        try:
            speed = float(self.speed_input.text())
            self.laser_machine.set_speed(speed)
        except ValueError:
            print('Invalid speed')
            return

        self.laser_machine.move_to(100, 100)  # произвольная точка


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LaserController()
    window.show()
    sys.exit(app.exec())
