import random
import config

class Prey:
    def __init__(self,x ,y):
        self.x = x
        self.y = y
        self.energy = 10

    def move(self, width, height):
         
         self.x = (self.x + random.randint(-1, 1)) % width
         self.y = (self.y + random.randint(-1, 1)) % height
         self.energy -= 1 #energy by step wasted      


def reproduce(self):
        # Если накопили достаточно энергии (из конфига)
        if self.energy >= config.REPRODUCTION_COST:
            self.energy -= config.REPRODUCTION_COST // 2  # Отдаем часть энергии детям
            # Создаем потомка с мутировавшими генами
            child = Prey(self.x, self.y, parent_genes=self.genes)
            return child
        return None