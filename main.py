import matplotlib.pyplot as plt
import numpy as np
import config
import random
from entities import Prey
from entities import Plankton


class Simulation:
    def __init__(self):
        #настраиваем параметры
        self.width = config.GRID_WIDTH
        self.height = config.GRID_HEIGHT
        self.grid = np.zeros((self.height, self.width))
        self.log_buffer = []  # Наш список-накопитель 

        self.plankton_list = [Plankton(random.random() * self.width,
                                       random.random() * self.height) for _ in range(150)]
                 
               
        # Создаем начальных жителей (15 штук) 
        self.prey_list = [Prey(random.randint(0, self.width-1), 
                               random.randint(0, self.height-1)) 
                          for _ in range(15)]
        
        self.seed_plankton()

    def log_statistics(self):
        # 1. Считаем текущие показатели популяции 
        plankton_count = np.sum(self.grid == 1)
        prey_count = len(self.prey_list)
        
        # 2. Формируем строку и добавляем в список-буфер 
        stats_str = f"Plankton: {plankton_count}, Prey: {prey_count}"
        self.log_buffer.append(stats_str)
        
        # 3. Пакетная запись при достижении 50 записей 
        if len(self.log_buffer) >= 50:
            with open("simulation_log.txt", "a") as f:
                for line in self.log_buffer:
                    f.write(line + "\n")
            self.log_buffer = [] # Очищаем список после записи
            print("--- Статистика сброшена на диск ---")

    def seed_plankton(self):
        for r in range(self.height):
            for c in range(self.width):
                if random.random() < config.INITIAL_PLANKTON_DENSITY:
                    self.grid[r][c] = 1

    def update_world(self):
        new_grid = self.grid.copy()
        # Повышаем шанс рождения, чтобы компенсировать аппетит жертв
        death_rate = 0.04 
        birth_chance = 0.08  # Увеличил с 0.06 до 0.08 для стабильности
        
        #дрейф планктона
        for p in self.plankton_list:
            p.drift(self.width, self.height)

        #логика жертв
        for p in self.prey_list:
            p.move(self.width, self.height)

            #поиск еды через расстояние
            for food in self.plankton_list[:]:
                distance = ((p.x - food.x)**2 + (p.y - food.y)**2)**0.5
                if distance < 2.0:
                    self.plankton_list.remove(food)
                    p.energy += 12 # бонус к энергии

                    #регенерация планктона
                    if random.random() < birth_chance:
                        self.plankton_list.append(Plankton(random.random() * self.width,
                                                  random.random() * self.height))
            if p.energy <= 0:
                self.prey_list.remove(p)

        

        

            
                
                if self.grid[r][c] == 1:
                    # МЯГКАЯ ЛОГИКА:
                    # Убираем neighbors < 1 (пусть одиночки живут)
                    # Порог перенаселения ставим > 4 (вместо 3), чтобы кучки были погуще
                    if random.random() < death_rate or neighbors > 4:
                        new_grid[r][c] = 0
                elif self.grid[r][c] == 0:
                    # Рождение: если есть хотя бы 1 сосед (быстрее заполняет пустоты)
                    if neighbors > 0 and random.random() < birth_chance:
                        new_grid[r][c] = 1
                    # Чуть увеличили самозарождение (было 0.0001)
                    elif random.random() < 0.0005:
                        new_grid[r][c] = 1

        self.grid = new_grid

        if hasattr(self, "prey_list"):
            for p in self.prey_list[:]: 
                p.move(self.width, self.height)
                
                if p.energy <= 0:
                    self.prey_list.remove(p)
                    continue

                if self.grid[int(p.y)][int(p.x)] == 1:
                    self.grid[int(p.y)][int(p.x)] = 0
                    p.energy += 12 

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
                self.update_world()    # Рассчитываем физику мира 
                self.log_statistics()  # Собираем данные в буфер 
                
                img.set_data(self.grid) 
                plt.pause(3)           # Пауза для HDD 
        except KeyboardInterrupt:
            print("\nСимуляция остановлена")

if __name__ == "__main__":
    sim = Simulation()
    sim.run()