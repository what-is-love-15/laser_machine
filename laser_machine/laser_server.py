import socket
import time


class LaserMachine:
    def __init__(self):  # состояние стонка
        self.x = 0  # текущие координаты
        self.y = 0
        self.is_on = False  # вкл/выкл лазер
        self.speed = 1  # шагов в секунду

    def set_laser(self, state):
        self.is_on = state
        print(f"Лазер {'включен' if state else 'выключен'}")

    def set_speed(self, speed):
        self.speed = max(1, speed)
        print(f'Скорость установлена: {self.speed} шагов/сек')

    def move_to(self, x2, y2):
        path = self.bresenham(self.x, self.y, x2, y2)
        for x, y in path:
            self.x, self.y = x, y
            print(f'Сейчас лазер в точке: ({self.x}, {self.y})')
            time.sleep(1 / self.speed)  # ждем, симуляция движения
        print('Движение завершено')

    def bresenham(self, x1, y1, x2, y2):
        """Алгоритм Брезенхэма для движения по прямой"""
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x2 > x1 else -1
        sy = 1 if y2 > y1 else -1
        err = dx - dy

        while x1 != x2 or y1 != y2:
            points.append((x1, y1))
            e2 = err * 2
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

        points.append((x2, y2))  # Добавляем конечную точку
        return points


# запуск сервера
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 12345))
server.listen(1)

print('Ожидаем подключение...')
conn, addr = server.accept()
print(f'ПОдключение от {addr}')

machine = LaserMachine()  # создали наш станок

while True:
    data = conn.recv(1024).decode()
    if not data:
        break

    print(f'Получена команда: {data}')

    if data.startswith('MOVE'):
        _, x, y = data.split()
        machine.move_to(int(x), int(y))
        conn.send(f'OK MOVED {machine.x} {machine.y}'.encode())

    elif data == 'LASER ON':
        machine.set_laser(True)
        conn.send('OK LASER ON'.encode())

    elif data == 'LASER OFF':
        machine.set_laser(False)
        conn.send('OK LASER OFF'.encode())

    elif data.startswith('SPEED'):
        _, speed = data.split()
        machine.set_speed(int(speed))
        conn.send(f'OK SPEED {machine.speed}'.encode())

    elif data == 'STATUS':
        conn.send(f'STATUS {machine.x} {machine.y} {int(machine.is_on)}'.encode())

conn.close()
server.close()
