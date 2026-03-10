import matplotlib.pyplot as plt
import numpy as np
import random
import psutil
import time
import os
from entities import Plankton, Herbivore, Predator, Apex_Predator
from logger import SimulationLogger 
import pandas as pd

# Глобальный таймер для замера общей производительности
start_sim_time = time.time()

class Simulation:
    def __init__(self, width=100, height=100):
        self.width = width
        self.height = height
        self.iteration = 0
        self.log_buffer = []
        self.data_logger = SimulationLogger()
        
        # Инициализация популяций
        self.plankton_list = [Plankton(random.random()*width, random.random()*height) for _ in range(100)]
        self.herbivore_list = [Herbivore(random.random()*width, random.random()*height) for _ in range(15)]
        self.predator_list = [Predator(random.random()*width, random.random()*height) for _ in range(5)]
        self.apex_predator_list = [Apex_Predator(random.random()*width, random.random()*height) for _ in range(2)]

    def log_statistics(self):
        # Замер ресурсов раз в 100 шагов
        if self.iteration % 100 == 0:
            process = psutil.Process(os.getpid())
            mem_mb = process.memory_info().rss / (1024 * 1024)
            avg_speed_ms = ((time.time() - start_sim_time) / max(1, self.iteration)) * 1000
            print(f"Шаг {self.iteration} | RAM: {mem_mb:.2f} MB | Speed: {avg_speed_ms:.2f} ms/step")

        # Оптимизированная запись в буфер каждые 20 шагов
        if self.iteration % 20 == 0:
            stats_str = f"It: {self.iteration} | Pl: {len(self.plankton_list)}, Herb: {len(self.herbivore_list)}, Pred: {len(self.predator_list)}, Apex: {len(self.apex_predator_list)}"
            self.log_buffer.append(stats_str)

        if len(self.log_buffer) >= 50:
            with open("simulation_log.txt", "a") as f:
                f.writelines(line + "\n" for line in self.log_buffer)
            self.log_buffer = [] 
            print("--- Логи сброшены на диск ---")

    def update_world(self):
        # Проверка на полное вымирание
        if not self.herbivore_list and not self.predator_list and not self.apex_predator_list:
            self.data_logger.log_final_result(self.iteration, self.herbivore_list, self.predator_list)
            return False

        self.iteration += 1
        
        if self.iteration % 20 == 0:
            self.data_logger.save_state(self.iteration, self.herbivore_list, self.predator_list)
            
        # 1. Планктон 
        for p in self.plankton_list[:]:
            p.drift(self.width, self.height)

        # 2. Травоядные
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

        # 3. Хищники
        for pred in self.predator_list[:]:
            pred.move(self.width, self.height, self.herbivore_list)
            for herb in self.herbivore_list[:]:
                if abs(pred.x - herb.x) < 2.0 and abs(pred.y - herb.y) < 2.0:
                    if herb in self.herbivore_list:
                        self.herbivore_list.remove(herb)
                        pred.energy += 25
            
            pred.energy -= 0.5 
            if pred.energy <= 0: self.predator_list.remove(pred)  
            
        # 4. Суперхищники
        for ax_p in self.apex_predator_list[:]:
            ax_p.move(self.width, self.height, self.predator_list) 
            for predator in self.predator_list[:]:
                if abs(ax_p.x - predator.x) < 3.0 and abs(ax_p.y - predator.y) < 3.0:
                    if predator in self.predator_list:
                        self.predator_list.remove(predator)
                        ax_p.energy += 50
            
            ax_p.energy -= 1.0 
            if ax_p.energy <= 0: 
                self.apex_predator_list.remove(ax_p)

        # Регенерация планктона
        if len(self.plankton_list) < 120 and random.random() < 0.3:
            self.plankton_list.append(Plankton(random.random() * self.width, 
                                               random.random() * self.height))
        return True

    def run(self, max_steps=None):
        plt.ion()
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_facecolor("#1F1F1F") 
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        
        pl_layer = ax.scatter([], [], c="#FEFAFA", s=2, alpha=0.5)
        pr_layer = ax.scatter([], [], c="#00AD20", s=40, edgecolors='white')
        pd_layer = ax.scatter([], [], c="#C70104", s=100, edgecolors='white')
        ax_layer = ax.scatter([], [], c="#FACE0C", s=120, edgecolors='white', marker='*')

        info_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, color='white', fontsize=10)
        ax.set_title("DanGenLife Ecosystem: Apex Predator Level")

        try:
            while plt.fignum_exists(fig.number):
                if max_steps and self.iteration >= max_steps: break
                
                active = self.update_world()
                self.log_statistics()
                
                # Обновление графики
                pl_layer.set_offsets([[p.x, p.y] for p in self.plankton_list] if self.plankton_list else np.empty((0, 2)))
                pr_layer.set_offsets([[p.x, p.y] for p in self.herbivore_list] if self.herbivore_list else np.empty((0, 2)))
                pd_layer.set_offsets([[p.x, p.y] for p in self.predator_list] if self.predator_list else np.empty((0, 2)))
                ax_layer.set_offsets([[p.x, p.y] for p in self.apex_predator_list] if self.apex_predator_list else np.empty((0, 2)))
                
                info_text.set_text(f"Step: {self.iteration} | Herb: {len(self.herbivore_list)} | Pred: {len(self.predator_list)} | Apex: {len(self.apex_predator_list)}")
                plt.pause(0.01) 
                
                if not active: break

        except KeyboardInterrupt:
            print("\nСимуляция остановлена пользователем.")
        finally:
            if self.log_buffer:
                with open("simulation_log.txt", "a") as f:
                    f.writelines(line + "\n" for line in self.log_buffer)
            plt.close(fig)

def run_batch_simulation(cycles=15):
    # Список для хранения данных каждого прогона
    batch_data = []
    summary_results = {"Herbivore_Wins": 0, "Predator_Wins": 0, "Apex_Wins": 0, "Extinction": 0}
    
    for i in range(1, cycles + 1):
        print(f"\n>>> Запуск цикла №{i} из {cycles} <<<")
        sim = Simulation()
        # Запускаем симуляцию с лимитом шагов для ускорения анализа
        sim.run(max_steps=500) 
        
        # Определяем исход
        winner = "Extinction"
        if len(sim.apex_predator_list) > 0:
            winner = "Apex_Wins"
        elif len(sim.predator_list) > 0:
            winner = "Predator_Wins"
        elif len(sim.herbivore_list) > 0:
            winner = "Herbivore_Wins"
        
        summary_results[winner] += 1
        
        # Собираем детальные показатели для Excel
        batch_data.append({
            "Cycle_ID": i,
            "Winner": winner,
            "Total_Steps": sim.iteration,
            "Final_Plankton": len(sim.plankton_list),
            "Final_Herbivores": len(sim.herbivore_list),
            "Final_Predators": len(sim.predator_list),
            "Final_Apex": len(sim.apex_predator_list)
        })

    # 1. Сохранение в Excel через Pandas
    df = pd.DataFrame(batch_data)
    excel_file = "ecosystem_batch_analysis.xlsx"
    df.to_excel(excel_file, index=False)
    print(f"\n[Анализ завершен] Данные сохранены в: {excel_file}")

    # 2. Итоговый отчет в консоль
    print("\n" + "="*30)
    print("ИТОГОВАЯ КОРРЕЛЯЦИЯ:")
    for key, value in summary_results.items():
        print(f"{key:15}: {value} ({(value/cycles)*100:.1f}%)")
    print("="*30)
    
    # 3. Визуализация итогов
    
    plt.figure(figsize=(10, 6))
    colors = ['#2ca02c', '#d62728', '#bcbd22', '#7f7f7f']
    plt.bar(summary_results.keys(), summary_results.values(), color=colors)
    plt.title(f"Результаты пакетного запуска (n={cycles})")
    plt.ylabel("Количество исходов")
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.show()

if __name__ == "__main__":
    run_batch_simulation(15)