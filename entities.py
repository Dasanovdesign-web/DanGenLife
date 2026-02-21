from organism import Organism
import random
import config # Импортируем конфиг для порогов

class Plankton(Organism):
    def __init__(self, x, y, parent_genes=None):
        super().__init__(x, y, parent_genes)
        # У рачков очень маленький расход энергии (метаболизм)
        self.energy = 10 

    def drift(self, width, height):
        # Дрейф — это хаотичное движение, зависящее от гена скорости
        if random.random() < self.genes["speed"]:
            self.x = (self.x + random.uniform(-0.5, 0.5)) % width
            self.y = (self.y + random.uniform(-0.5, 0.5)) % height


class Prey(Organism):
    def eat(self, grid):
        # Логика поедания планктона из сетки
        cell = grid[self.y][self.x]
        if cell.plankton > 0:
            self.energy += cell.plankton * self.genes["efficiency"]
            cell.plankton = 0


    def move(self, width, height, food_list=None):
        target = None
        closest_dist = self.genes["vision"]

        # 1. Ищем ближайшую еду в радиусе зрения
        if food_list:
            for food in food_list:
                dist = ((self.x - food.x)**2 + (self.y - food.y)**2)**0.5
                if dist < closest_dist:
                    closest_dist = dist
                    target = food

        # 2. Если нашли цель — идем к ней
        if target:
            dx = 1 if target.x > self.x else -1 if target.x < self.x else 0
            dy = 1 if target.y > self.y else -1 if target.y < self.y else 0
            self.x = (self.x + dx) % width
            self.y = (self.y + dy) % height
        else:
            # Если еды нет, используем обычное случайное движение родителя
            super().move(width, height)
            

    def reproduce(self):
        if self.energy >= 40:
            self.energy /= 2
            return Prey(self.x, self.y, parent_genes=self.genes)
        return None

class Predator(Organism):
    def __init__(self, x, y, parent_genes=None):
        # Вызываем родительский конструктор для работы с генами
        super().__init__(x, y, parent_genes)
        # У хищников база энергии чуть выше, так как охотиться труднее
        self.energy = 30 

    def eat(self, prey_list):
        """Хищник ищет жертву в своей клетке"""
        for prey in prey_list:
            if prey.x == self.x and prey.y == self.y:
                self.energy += 20  # Получаем энергию от поедания Prey
                prey_list.remove(prey) # Жертва погибает
                return True
        return False

    def reproduce(self):
        """Размножение хищника с передачей мутаций"""
        if self.energy >= config.PREDATOR_REPRODUCTION_THRESHOLD:
            self.energy -= 15 # Трата на роды
            # Создаем потомка, передавая текущие гены для мутации
            return Predator(self.x, self.y, parent_genes=self.genes)
        return None
    
    
