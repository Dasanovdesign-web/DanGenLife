import matplotlib.pyplot as plt
import numpy as np
import config
import random
from entities import Prey

class Simulation:
    def __init__(self):
        self.width = config.GRID_WIDTH
        self.height = config.GRID_HEIGHT
        self.grid = np.zeros((self.height, self.width))
        
        # Создаем начальных жителей (15 штук)
        self.prey_list = [Prey(random.randint(0, self.width-1), 
                               random.randint(0, self.height-1)) 
                          for _ in range(15)]
        
        self.seed_plankton()

    def seed_plankton(self):
        for r in range(self.height):
            for c in range(self.width):
                if random.random() < config.INITIAL_PLANKTON_DENSITY:
                    self.grid[r][c] = 1

    def update_world(self):
        new_grid = self.grid.copy()
        death_rate = 0.02 
        birth_chance = 0.1 

        # 1. Жизненный цикл планктона
        for r in range(self.height):
            for c in range(self.width):
                # Если в клетке жертва, очищаем её след на новой сетке (мы перерисуем её позже)
                if self.grid[r][c] == 2:
                    new_grid[r][c] = 0
                    continue

                # Считаем соседей
                neighbors = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0: continue
                        nr, nc = (r + dr) % self.height, (c + dc) % self.width
                        if self.grid[nr][nc] == 1:
                            neighbors += 1

                # Логика планктона
                if self.grid[r][c] == 1:
                    if random.random() < death_rate or neighbors > 6:
                        new_grid[r][c] = 0
                elif self.grid[r][c] == 0:
                    if neighbors > 0 and random.random() < birth_chance:
                        new_grid[r][c] = 1
                    elif random.random() < 0.001:
                        new_grid[r][c] = 1

        self.grid = new_grid

        # 2. Логика Жертв (Prey)
        if hasattr(self, "prey_list"):
            for p in self.prey_list[:]: # Тот самый срез-копия [:]
                p.move(self.width, self.height)
                
                # Смерть от голода
                if p.energy <= 0:
                    self.prey_list.remove(p)
                    continue

                # Поедание планктона
                if self.grid[int(p.y)][int(p.x)] == 1:
                    self.grid[int(p.y)][int(p.x)] = 0
                    p.energy += 5 # Даем энергию за еду

                # Рисуем жертву (тип 2)
                self.grid[int(p.y)][int(p.x)] = 2

    def run(self):
        plt.ion()
        fig, ax = plt.subplots(figsize=(8, 8))
        from matplotlib.colors import ListedColormap
        cmap = ListedColormap(["#1F1F1F", "#FEFAFA", "#00AD20", "#C70104"])
        img = ax.imshow(self.grid, cmap=cmap, vmin=0, vmax=3)
        ax.set_title("DanGenLife Ecosystem: Plankton & Prey")

        try:
            while True:
                self.update_world()
                img.set_data(self.grid) 
                plt.pause(3)
        except KeyboardInterrupt:
            print("\nСимуляция остановлена")

if __name__ == "__main__":
    sim = Simulation()
    sim.run()