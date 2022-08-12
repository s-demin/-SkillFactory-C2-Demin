from random import randint

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrangShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid = False, size = 6):
        self.hid = hid
        self.size = size

        self.count = 0  # количество поражённых кораблей

        self.field = [["o"] * size for _ in range(size)]

        self.busy = []  # занятые клетки - либо кораблями, либо в них уже делали выстрелы
        self.ships = []

    def __str__(self):
        res = ""  # переменная, в которую мы будем запивсывать всю нашу доску
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "o")
        return res

    def out(self, d):  # метод out проверяет находится ли точка за пределами доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb = False):  # определение контура корабля и бизлежащих точек
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1),
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                # self.field[cur.x][cur.y] = "+"
                if not(self.out(cur)) and cur not in self.busy:  # если точка не выходит за границы доски и ещё не занята
                    if verb:
                        self.field[cur.x][cur.y] = "."  # мы ставим на месте этой точки символ точки
                    self.busy.append(cur)  # добавляем точку в список занятых точек

    def add_ship(self, ship):  # метод для размещения корабля
        for d in ship.dots:
            if self.out(d) or d in self.busy:  # каждая точка корабля не выходит за границы и не занята
                raise BoardWrangShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"  # поставим к каждую точку корабля
            self.busy.append(d)  # запишем жту точкукорабля в список занятых

        self.ships.append(ship)  # добавляем в список кораблей
        self.contour(ship)  # обводим по контуру

    def shot(self, d):  # делаем выстрел
        if self.out(d):  # если выстрел попадает за пределы инрового поля
            raise BoardOutException()  # выбрасываем исключение

        if d in self.busy:  # проверяем занята ли точка
            raise BoardUsedException()  # если точка занята - выбрасываем исключение

        self.busy.append(d)  # отмечаем выстрел как занятую точку

        for ship in self.ships:  # проверяем принадлежит ли точка какому-нибудь кораблю
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "⛝"  # если попали, ставим крест (X)
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."  # если промах, то ставим символ точки
        print("Мимо")
        return False

    def begin(self):  # перед началом игры обнуляем  список занятых точек
        self.busy =[]
        
    def defeat(self):  
        return self.count == len(self.ships)


class Player:  # создаём общий класс игрока
    def __init__(self, board, enemy):  # создаём доску игрока и доску противника
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()  # запрашиваем координаты выстрела
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):  # класс игрока-компьтера
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))  # случайно генерируем 2 точки от 0 до 5
        print(f"Ход компьютера {d.x + 1} {d.y + 1}")
        return d

class User(Player):  # класс игрока-пользователя
    def ask(self):
        while True:
            coords = input("Ваш ход: ").split()

            if len(coords) != 2:
                print("Введите две координаты: ")
                continue

            x, y = coords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа: ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)  # индексация списков с 0, а пользователю показывается с 1


class Game:  # класс игры
    def __init__(self, size = 6):  # задаём размер доски
        self.size = size
        self.lengths = [3, 2, 2, 1, 1, 1, 1]  # длины кораблей (один 3-палубный, два 2-палубных, четыре однопалубных)       
        pl = self.random_board()  # создаём случайную доску для игрока
        co = self.random_board()  # создаём случайную доску для компьютера
        co.hid = True  # скрываем корабли компьютера

        self.ai = AI(co, pl)  # создаём игрока компьютер
        self.us = User(pl, co)  # создаём игрока пользователь

    def try_board(self):  # создаём доску
        board = Board(size = self.size)
        attempts = 0
        for l in self.lengths:
            while True:
                attempts += 1
                if attempts > 2000:  # если попыток больше 2000 - возвращаем пустую доску
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrangShipException:
                    pass

        board.begin()
        return board

    def random_board(self):  # метод, гарантированно создающий доску
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):  # приветствие
        print("-------------------")
        print(" Приветсвуем вас")
        print("     в игре")
        print("   Морской бой")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки ")
        print(" y - номер столбца ")

    def print_boards(self):
        print("-" * 20)
        print("Доска пользователя:")
        print(self.us.board)
        print("-" * 27)
        print("Доска компьютера:")
        print(self.ai.board)

    def loop(self):  # игровой цикл
        num = 0  # номер хода
        while True:
            self.print_boards()
            if num % 2 == 0:  # если номер хода чётный - ходит пользователь
                print("-" * 27)
                print("Ходит пользователь")
                repeat = self.us.move()                    
            else:    # если номер хода нечётный - ходит компьютер
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
                
            if repeat:  # если игрок должен повторить ход, 
                num -= 1  # то номер хода уменьшается на единицу, чтобы остался прежним
            
            if self.ai.board.defeat():  # если все корабли поражены
                self.print_boards()
                print("-" * 20)
                print("Вы выиграли!")
                break
            
            if self.us.board.defeat():
                self.print_boards()
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1
                
    def start(self):
        self.greet()
        self.loop()
                                    
g = Game()
g.start()
