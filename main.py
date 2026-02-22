import matplotlib.pyplot as plt
import numpy as np
import config
import random
from entities import Plankton, Prey, Predator  

class Simulation:
    def __init__(self):
        # 1. Сначала задаем размеры (исправляет AttributeError)
        self.width = config.GRID_WIDTH
        self.height = config.GRID_HEIGHT
        self.grid = np.zeros((self.height, self.width))
        self.log_buffer = []  

        # 2. Создаем списки существ
        self.plankton_list = [Plankton(random.random() * self.width,
                                       random.random() * self.height) for _ in range(150)]
        self.prey_list = [Prey(random.random() * self.width, 
                               random.random() * self.height) for _ in range(15)]
        self.predator_list = [Predator(random.random() * self.width, 
                                       random.random() * self.height) for _ in range(5)]
        
        self.seed_plankton()

    def log_statistics(self):
        # Считаем по длине списков объектов (так точнее)
        plankton_count = len(self.plankton_list)
        prey_count = len(self.prey_list)
        predator_count = len(self.predator_list)
        
        stats_str = f"Plankton: {plankton_count}, Prey: {prey_count}, Pred: {predator_count}"
        self.log_buffer.append(stats_str)
        
        if len(self.log_buffer) >= 50:
            with open("simulation_log.txt", "a") as f:
                for line in self.log_buffer:
                    f.write(line + "\n")
            self.log_buffer = [] 
            print("--- Статистика сброшена на диск ---")

    def seed_plankton(self):
        for r in range(self.height):
            for c in range(self.width):
                if random.random() < config.INITIAL_PLANKTON_DENSITY:
                    self.grid[r][c] = 1

    def update_world(self):
        self.grid.fill(0) 

        # 1. Планктон
        for p in self.plankton_list[:]:
            p.drift(self.width, self.height)

        # 2. Жертвы
        for p in self.prey_list[:]:
            p.move(self.width, self.height, self.plankton_list) # Передаем список еды
            
            for food in self.plankton_list[:]:
                distance = ((p.x - food.x)**2 + (p.y - food.y)**2)**0.5
                if distance < 1.5:
                    self.plankton_list.remove(food)
                    p.energy += 30 # Увеличили бонус для выживания

            child = p.reproduce()
            if child: self.prey_list.append(child)

            if p.energy <= 0:
                self.prey_list.remove(p)

        # 3. НОВАЯ ЛОГИКА: Хищники (исправляет отсутствие движения)
        for pred in self.predator_list[:]:
            pred.move(self.width, self.height, self.prey_list) # Охота на жертв
            
            for prey in self.prey_list[:]:
                dist = ((pred.x - prey.x)**2 + (pred.y - prey.y)**2)**0.5
                if dist < 2.0:
                    self.prey_list.remove(prey)
                    pred.energy += 40 # Хороший бонус за охоту
            
            if pred.energy <= 0:
                self.predator_list.remove(pred)

        # Регенерация планктона
        if len(self.plankton_list) < 120:
            if random.random() < 0.3:
                self.plankton_list.append(Plankton(random.random() * self.width, 
                                                  random.random() * self.height))

    def run(self):
        plt.ion()
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_facecolor("#1F1F1F") 
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        
        plankton_layer = ax.scatter([], [], c="#FEFAFA", s=2, alpha=0.5)
        prey_layer = ax.scatter([], [], c="#00AD20", s=40, edgecolors='white')
        predator_layer = ax.scatter([], [], c="#C70104", s=100, edgecolors='white')

        ax.set_title("DanGenLife Ecosystem: Predator-Prey Balance")

        try:
            # Исправляет бесконечный цикл: проверяем, существует ли окно
            while plt.fignum_exists(fig.number):
                self.update_world()
                self.log_statistics()
                
                if self.plankton_list:
                    plankton_layer.set_offsets([[p.x, p.y] for p in self.plankton_list])
                
                if self.prey_list:
                    prey_layer.set_offsets([[p.x, p.y] for p in self.prey_list])
                else:
                    prey_layer.set_offsets(np.empty((0, 2)))

                if self.predator_list:
                    predator_layer.set_offsets([[p.x, p.y] for p in self.predator_list])
                else:
                    predator_layer.set_offsets(np.empty((0, 2)))

                plt.pause(0.01)
        except KeyboardInterrupt:
            print("\nСимуляция остановлена")
        finally:
            # Финальный сброс данных при закрытии
            if self.log_buffer:
                with open("simulation_log.txt", "a") as f:
                    for line in self.log_buffer:
                        f.write(line + "\n")
            print("--- Работа завершена, логи сохранены ---")

if __name__ == "__main__":
    sim = Simulation()
    sim.run()