import csv
import os

class SimulationLogger:
    def __init__(self, filename="simulation_data.csv"):
        self.filename = filename
        self.headers = ["tick", "prey_count", "predator_count", "avg_energy"]
        self.is_finished = False
        
        # Указываем delimiter=';' чтобы Excel сразу открывал по столбцам [cite: 2026-02-05]
        with open(self.filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(self.headers)

    def save_state(self, tick, prey_list, pred_list):
        all_organisms = prey_list + pred_list
        avg_energy = sum(o.energy for o in all_organisms) / len(all_organisms) if all_organisms else 0
            
        with open(self.filename, mode="a", newline="", encoding="utf-8") as f:
            # Здесь тоже добавляем delimiter=';' [cite: 2026-02-05]
            writer = csv.DictWriter(f, fieldnames=self.headers, delimiter=';')
            writer.writerow({
                "tick": tick,
                "prey_count": len(prey_list),
                "predator_count": len(pred_list),
                "avg_energy": round(avg_energy, 2)
            })

    def log_final_result(self, tick, prey_list, pred_list):
        if self.is_finished:
            return
            
        winner = "Никто (Пустота)"
        if len(prey_list) > 0 and len(pred_list) == 0: winner = "Жертвы"
        elif len(pred_list) > 0 and len(prey_list) == 0: winner = "Хищники"
        
        with open("sim_history.txt", "a", encoding="utf-8") as f:
            f.write(f"--- Итог прогона ---\nТик: {tick}\nПобедитель: {winner}\n\n")
        
        self.is_finished = True