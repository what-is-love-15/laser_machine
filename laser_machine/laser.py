class LaserMachine:
    def __init__(self, x_max=500, y_max=500):  # состояние стонка
        self.x = 0
        self.y = 0
        self.is_on = False  # выключен
        self.speed = 0  # скорость 0
        self.x_max = x_max
        self.y_max = y_max

    def status(self):
        return {
            'x': self.x,
            'y': self.y,
            'speed': self.speed,
            'is_on': self.is_on
        }

    def turn_on(self, state: bool):  # вкл
        self.is_on = state

    def set_speed(self, speed):
        if 0 <= speed <= 10:
            self.speed = speed
        else:
            print('!!! Error: speed must be between 0 and 10 !!!')

    def move_to(self, x, y):
        if 0 <= x <= self.x_max and 0 <= y <= self.y_max:
            self.x = x
            self.y = y
        else:
            print(f'!!! Error: coordinates are not in area {self.x_max}x{self.y_max} !!!')


if __name__ == "__main__":
    machine = LaserMachine()

    machine.move_to(100, 200)
    print(machine.status())

    machine.set_speed(5)
    print(machine.status())

    machine.turn_on(True)
    print(machine.status())

    machine.move_to(600, 0)
