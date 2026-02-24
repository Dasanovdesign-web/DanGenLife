import matplotlib.pyplot as plt
import numpy as np
import config
import random
import psutil
import time
import os
from entities import Plankton, Prey, Predator  

# Глобальный таймер для замера общей производительности
start_sim_time = time.time()

class Simulation:
    def __init__(self):
        # 1. Параметры мира [cite: 2026-02-05]
        self.width = config.GRID_WIDTH
        self.height = config.GRID_HEIGHT
        self.grid = np.zeros((self.height, self.width))
        self.log_buffer = []  
        self.iteration = 0
        
        # 2. Очистка логов (чтобы файл не раздувался) [cite: 2026-02-24]
        if os.path.exists("simulation_log.txt"):
            with open("simulation_log.txt", "w") as f:
                f.write("--- New simulation start ---\n")

        # 3. Создание популяций [cite: 2026-01-30]
        self.plankton_list = [Plankton(random.random() * self.width,
                                       random.random() * self.height) for _ in range(150)]
        self.prey_list = [Prey(random.random() * self.width, 
                               random.random() * self.height) for _ in range(15)]
        self.predator_list = [Predator(random.random() * self.width, 
                                       random.random() * self.height) for _ in range(5)]
        
        self.seed_plankton()

    def log_statistics(self):
        self.iteration += 1
        
        # Замер ресурсов раз в 50 шагов [cite: 2026-02-19]
        if self.iteration % 50 == 0:
            process = psutil.Process(os.getpid())
            mem_mb = process.memory_info().rss / (1024 * 1024)
            # Считаем среднюю скорость шага от начала симуляции
            avg_speed_ms = ((time.time() - start_sim_time) / self.iteration) * 1000
            print(f"Шаг {self.iteration} | RAM: {mem_mb:.2f} MB | Speed: {avg_speed_ms:.2f} ms/step")

        # Формируем строку лога [cite: 2026-02-05]
        stats_str = f"It: {self.iteration} | Pl: {len(self.plankton_list)}, Pr: {len(self.prey_list)}, Pred: {len(self.predator_list)}"
        
        # Оптимизированная запись (раз в 10 шагов в буфер) [cite: 2026-02-24]
        if self.iteration % 10 == 0:
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

        # 1. Планктон [cite: 2026-01-30]
        for p in self.plankton_list[:]:
            p.drift(self.width, self.height)

        # 2. Жертвы (охота на планктон)
        for p in self.prey_list[:]:
            p.move(self.width, self.height, self.plankton_list)
            for food in self.plankton_list[:]:
                if abs(p.x - food.x) < 1.5 and abs(p.y - food.y) < 1.5:
                    self.plankton_list.remove(food)
                    p.energy += 30 
            
            child = p.reproduce()
            if child: self.prey_list.append(child)
            if p.energy <= 0: self.prey_list.remove(p)

        # 3. Хищники (охота на жертв) [cite: 2026-01-30]
        for pred in self.predator_list[:]:
            pred.move(self.width, self.height, self.prey_list)
            for prey in self.prey_list[:]:
                if abs(pred.x - prey.x) < 2.0 and abs(pred.y - prey.y) < 2.0:
                    if prey in self.prey_list:
                        self.prey_list.remove(prey)
                        pred.energy += 40
            if pred.energy <= 0: self.predator_list.remove(pred)

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

        # HUD (текст на экране) [cite: 2026-01-26]
        info_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, color='white', fontsize=10)
        ax.set_title("DanGenLife Ecosystem: Balance")

        try:
            while plt.fignum_exists(fig.number):
                self.update_world()
                self.log_statistics()
                
                # Обновление графики
                pl_layer.set_offsets([[p.x, p.y] for p in self.plankton_list])
                pr_layer.set_offsets([[p.x, p.y] for p in self.prey_list] if self.prey_list else np.empty((0, 2)))
                pd_layer.set_offsets([[p.x, p.y] for p in self.predator_list] if self.predator_list else np.empty((0, 2)))
                
                # Обновление HUD
                info_text.set_text(f"Step: {self.iteration} | Prey: {len(self.prey_list)} | Pred: {len(self.predator_list)}")

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