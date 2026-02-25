import matplotlib.pyplot as plt
import numpy as np
import config
import random
import psutil
import time
import os
from entities import Plankton, Herbivore, Predator, Apex_Predator

# Глобальный таймер для замера общей производительности
start_sim_time = time.time()

class Simulation:
    def __init__(self):
        # 1. Параметры мира 
        self.width = config.GRID_WIDTH
        self.height = config.GRID_HEIGHT
        self.grid = np.zeros((self.height, self.width))
        self.herbivores = []
        self.predators = []
        
        self.log_buffer = []  
        self.iteration = 0
        
        # 2. Очистка логов (чтобы файл не раздувался) 
        if os.path.exists("simulation_log.txt"):
            with open("simulation_log.txt", "w") as f:
                f.write("--- New simulation start ---\n")

        # 3. Создание популяций [cite: 2026-01-30]
        self.plankton_list = [Plankton(random.random() * self.width,
                                       random.random() * self.height) for _ in range(150)]
        self.herbivore_list = [Herbivore(random.random() * self.width, 
                               random.random() * self.height) for _ in range(15)]
        self.predator_list = [Predator(random.random() * self.width, 
                                       random.random() * self.height) for _ in range(5)]
        self.apex_predator_list = [Predator(random.random() * self.width,
                                       random.random() * self.height) for _ in range(2)]
        self.seed_plankton()

    def log_statistics(self):
        self.iteration += 1
        
        # Замер ресурсов раз в 50 шагов 
        if self.iteration % 100 == 0:
            process = psutil.Process(os.getpid())
            mem_mb = process.memory_info().rss / (1024 * 1024)
            # Считаем среднюю скорость шага от начала симуляции
            avg_speed_ms = ((time.time() - start_sim_time) / self.iteration) * 1000
            print(f"Шаг {self.iteration} | RAM: {mem_mb:.2f} MB | Speed: {avg_speed_ms:.2f} ms/step")

        # Формируем строку лога 
        stats_str = f"It: {self.iteration} | Pl: {len(self.plankton_list)}, Pr: {len(self.herbivore_list)}, Pred: {len(self.predator_list)}"
        
        # Оптимизированная запись (раз в 10 шагов в буфер) [cite: 2026-02-24]
        if self.iteration % 20 == 0:
            self.log_buffer.append(stats_str)

        # Сброс буфера на диск
        if len(self.log_buffer) >= 50:
            with open("simulation_log.txt", "a") as f:
                f.writelines(line + "\n" for line in self.log_buffer)
            self.log_buffer = [] 
            print("--- Логи сохранены ---")

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

        # 2. Жертвы (охота на планктон)
        for p in self.herbivore_list[:]:
            p.move(self.width, self.height, self.plankton_list)
            for food in self.plankton_list[:]:
                if abs(p.x - food.x) < 1.5 and abs(p.y - food.y) < 1.5:
                    if food in self.plankton_list:
                        self.plankton_list.remove(food)
                        p.energy += 30 
            
            child = p.reproduce()
            if child: self.herbivore_list.append(child)
            if p.energy <= 0: self.herbivore_list.remove(p)

        # 3. Хищники (охота на жертв)
        for pred in self.predator_list[:]:
            pred.move(self.width, self.height, self.herbivore_list)
            for herbivore in self.herbivore_list[:]:
                if abs(pred.x - herbivore.x) < 2.0 and abs(pred.y - herbivore.y) < 2.0:
                    if herbivore in self.herbivore_list:
                        self.herbivore_list.remove(herbivore)
                        pred.energy += 25
            
            pred.energy -= 0.5 # Трата энергии за ход
            if pred.energy <= 0: self.predator_list.remove(pred)  
            
        # 4. Суперхищники (Желтые) - Исправлено [cite: 2026-02-05]
        for ax_p in self.apex_predator_list[:]:
            # Апексы охотятся на КРАСНЫХ хищников
            ax_p.move(self.width, self.height, self.predator_list) 
    
            for predator in self.predator_list[:]:
                if abs(ax_p.x - predator.x) < 3.0 and abs(ax_p.y - predator.y) < 3.0:
                    if predator in self.predator_list:
                        self.predator_list.remove(predator)
                        ax_p.energy += 50
    
            ax_p.energy -= 1 # Апексы тратят больше энергии, так как они большие
            
            if ax_p.energy <= 0: 
                self.apex_predator_list.remove(ax_p)

        # Регенерация планктона
        if len(self.plankton_list) < 120 and random.random() < 0.3:
            self.plankton_list.append(Plankton(random.random() * self.width, 
                                               random.random() * self.height))

    def run(self):
        plt.ion()
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_facecolor("#1F1F1F") 
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        
        pl_layer = ax.scatter([], [], c="#FEFAFA", s=2, alpha=0.5)
        pr_layer = ax.scatter([], [], c="#00AD20", s=40, edgecolors='white')
        pd_layer = ax.scatter([], [], c="#C70104", s=100, edgecolors='white')
        ax_layer = ax.scatter([], [], c="#FACE0C", s=120, edgecolors='white')

        info_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, color='white', fontsize=10)
        ax.set_title("DanGenLife Ecosystem: Balance")

        try:
            while plt.fignum_exists(fig.number):
                self.update_world()
                self.log_statistics()
                
                # Обновление графики
                pl_layer.set_offsets([[p.x, p.y] for p in self.plankton_list] if self.plankton_list else np.empty((0, 2)))
                pr_layer.set_offsets([[p.x, p.y] for p in self.herbivore_list] if self.herbivore_list else np.empty((0, 2)))
                pd_layer.set_offsets([[p.x, p.y] for p in self.predator_list] if self.predator_list else np.empty((0, 2)))
                ax_layer.set_offsets([[p.x, p.y] for p in self.apex_predator_list] if self.apex_predator_list else np.empty((0, 2)))
                
                # Обновление HUD (Добавлены Apex)
                info_text.set_text(f"Step: {self.iteration} | Herb: {len(self.herbivore_list)} | Pred: {len(self.predator_list)} | Apex: {len(self.apex_predator_list)}")

                plt.pause(0.02) 
        except KeyboardInterrupt:
            print("\nОстановлено")
        finally:
            print("--- Готово ---")

    def run(self):
        plt.ion()
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_facecolor("#1F1F1F") 
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        
        pl_layer = ax.scatter([], [], c="#FEFAFA", s=2, alpha=0.5)
        pr_layer = ax.scatter([], [], c="#00AD20", s=40, edgecolors='white')
        pd_layer = ax.scatter([], [], c="#C70104", s=100, edgecolors='white')
        ax_layer = ax.scatter([], [], c="#FACE0C", s=120, edgecolors='white')

        # HUD (текст на экране) [cite: 2026-01-26]
        info_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, color='white', fontsize=10)
        ax.set_title("DanGenLife Ecosystem: Balance")

        try:
            while plt.fignum_exists(fig.number):
                self.update_world()
                self.log_statistics()
                
                # Обновление графики
                pl_layer.set_offsets([[p.x, p.y] for p in self.plankton_list] if self.plankton_list else np.empty((0, 2)))
                pr_layer.set_offsets([[p.x, p.y] for p in self.herbivore_list] if self.herbivore_list else np.empty((0, 2)))
                pd_layer.set_offsets([[p.x, p.y] for p in self.predator_list] if self.predator_list else np.empty((0, 2)))
                ax_layer.set_offsets([[p.x, p.y] for p in self.apex_predator_list] if self.apex_predator_list else np.empty((0, 2)))
                
                # Обновление HUD
                info_text.set_text(f"Step: {self.iteration} | herbivore: {len(self.herbivore_list)} | Pred: {len(self.predator_list)}")

                plt.pause(0.02) # Ускорили отрисовку [cite: 2026-02-05]
        except KeyboardInterrupt:
            print("\nОстановлено")
        finally:
            if self.log_buffer:
                with open("simulation_log.txt", "a") as f:
                    f.writelines(line + "\n" for line in self.log_buffer)
            print("--- Готово ---")

if __name__ == "__main__":
    Simulation().run()