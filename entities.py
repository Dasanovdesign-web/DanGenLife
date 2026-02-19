import random
import config

class Plankton:
    def __init__(self, x, y): # Добавили x, y сюда [cite: 2026-02-05]
        self.x = x
        self.y = y
        
    def drift(self, width, height):
        # Исправлено: запятые в uniform и использование self.y для координаты Y
        self.x = (self.x + random.uniform(-0.1, 0.1)) % width
        self.y = (self.y + random.uniform(-0.1, 0.1)) % height

class Prey:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 20 # Поднял базу, чтобы не умирали слишком быстро [cite: 2026-01-30]

    def move(self, width, height):
        self.x = (self.x + random.randint(-1, 1)) % width
        self.y = (self.y + random.randint(-1, 1)) % height
        self.energy -= 0.5 # Уменьшил расход, чтобы дать шанс найти еду [cite: 2026-02-05]

    def reproduce(self): # Теперь этот метод внутри класса Prey [cite: 2026-02-05]
        # Используем параметры из config [cite: 2026-02-05]
        if self.energy >= config.REPRODUCTION_THRESHOLD:
            self.energy -= 10 # Трата энергии на роды
            return Prey(self.x, self.y) # Создаем нового ребенка [cite: 2026-02-05]
        return None