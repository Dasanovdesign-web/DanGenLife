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

class Herbivore(Organism):
    def __init__(self, x, y, parent_genes=None):
        super().__init__(x, y, parent_genes)
        self.energy = 35  # Повысили выживаемость 

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
        
        self.energy -= 0.15 # Уменьшили расход на движение 

    def reproduce(self):
        if self.energy >= 50: # Снизили порог для активного роста популяции
            self.energy -= 25
            return Herbivore(self.x, self.y, parent_genes=self.genes)
        return None

class Predator(Organism):
    def __init__(self, x, y, parent_genes=None):
        super().__init__(x, y, parent_genes)
        self.energy = 40 # Увеличил, чтобы не умирали сразу
        self.view_radius = 15.0 

    def move(self, width, height, herbivore_list):
        target = None
        min_dist = self.view_radius

        for p in herbivore_list:
            dist = ((self.x - p.x)**2 + (self.y - p.y)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                target = p

        if target:
            step = 0.9
            # ИСПРАВЛЕНО: теперь они бегут К цели, а не ОТ нее
            self.x = (self.x + (step if target.x > self.x else -step)) % width
            self.y = (self.y + (step if target.y > self.y else -step)) % height
        else:
            super().move(width, height) # Используем случайное движение родителя
        
        self.energy -= 0.5 # Сбалансированная трата

class Apex_Predator(Organism):
    def __init__(self, x, y, parent_genes=None):
        super().__init__(x, y, parent_genes)
        self.energy = 80 # Увеличил в 8 раз, чтобы они жили долго
        self.view_radius = 25.0 
            
    def move(self, width, height, food_list=None):
        target = None
        closest_dist = self.view_radius

        if food_list:
            for food in food_list:
                dist = ((self.x - food.x)**2 + (self.y - food.y)**2)**0.5
                if dist < closest_dist:
                    closest_dist = dist
                    target = food

        if target:
            step = 1.2 # Быстрее обычных
            self.x = (self.x + (step if target.x > self.x else -step)) % width
            self.y = (self.y + (step if target.y > self.y else -step)) % height
        else:
            super().move(width, height)
        
        self.energy -= 0.2 # Высшие хищники очень экономны