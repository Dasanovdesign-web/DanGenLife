import random
import config
from organism import Organism

class Plankton(Organism):
    def __init__(self, x, y, parent_genes=None):
        super().__init__(x, y, parent_genes)
        self.energy = 30 

    def drift(self, width, height):
        # Дрейф должен быть всегда, иначе планктон замирает
        self.x = (self.x + random.uniform(-0.3, 0.3)) % width
        self.y = (self.y + random.uniform(-0.3, 0.3)) % height

class Prey(Organism):
    def __init__(self, x, y, parent_genes=None):
        super().__init__(x, y, parent_genes)
        self.energy = 35  # Повысили выживаемость [cite: 2026-02-05]

    def move(self, width, height, food_list=None):
        target = None
        closest_dist = self.genes.get("vision", 10) # Гены из родительского класса

        if food_list:
            for food in food_list:
                dist = ((self.x - food.x)**2 + (p_dist := (self.y - food.y)**2))**0.5
                if dist < closest_dist:
                    closest_dist = dist
                    target = food

        if target:
            # Движение к еде
            self.x = (self.x + (1 if target.x > self.x else -1)) % width
            self.y = (self.y + (1 if target.y > self.y else -1)) % height
        else:
            super().move(width, height)
        
        self.energy -= 0.15 # Уменьшили расход на движение [cite: 2026-01-30]

    def reproduce(self):
        if self.energy >= 50: # Снизили порог для активного роста популяции
            self.energy -= 25
            return Prey(self.x, self.y, parent_genes=self.genes)
        return None

class Predator(Organism): # Унаследовали от Organism, чтобы работали гены и зрение
    def __init__(self, x, y, parent_genes=None):
        super().__init__(x, y, parent_genes)
        self.energy = 20 # Большой стартовый запас
        self.view_radius = 15.0 

    def move(self, width, height, prey_list):
        target = None
        min_dist = self.view_radius

        for p in prey_list:
            dist = ((self.x - p.x)**2 + (self.y - p.y)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                target = p

        if target:
            # Хищник чуть быстрее жертвы (1.2)
            self.x = (self.x + (1.2 if target.x > self.x else -1.2)) % width
            self.y = (self.y + (1.2 if target.y > self.y else -1.2)) % height
        else:
            # Случайный поиск
            self.x = (self.x + random.uniform(-0.8, 0.8)) % width
            self.y = (self.y + random.uniform(-0.8, 0.8)) % height
        
        self.energy -= 0.7 # Трата энергии за шаг

    def reproduce(self):
        # Используем порог из конфига или фиксированный
        threshold = getattr(config, 'PREDATOR_REPRODUCTION_THRESHOLD', 100)
        if self.energy >= threshold:
            self.energy -= 50
            return Predator(self.x, self.y, parent_genes=self.genes)
        return None