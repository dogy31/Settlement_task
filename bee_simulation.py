import tkinter as tk
from tkinter import messagebox
import random
import os


class BeeSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Симуляция пчелиной семьи")
        self.root.configure(bg="#1e1e1e")
        self.root.geometry("1200x800")
        self.root.resizable(False, False)

        self.day = 0
        self.queen_alive = True
        self.honey_storage = 1000
        self.auto_running = False

        self.larvae = []
        self.drones = []
        self.workers_honey = []
        self.workers_cleaner = []
        self.dead_bees = []

        self.starved_counts = {
            "larvae": 0,
            "drones": 0,
            "workers_honey": 0,
            "workers_cleaner": 0
        }

        self.setup_ui()
        self.update_ui()

    def setup_ui(self):
        self.bg = "#1e1e1e"
        self.fg = "#f0f0f0"
        self.font_main = ("Segoe UI", 12)
        self.font_bold = ("Segoe UI", 14, "bold")

        self.day_label = tk.Label(self.root, text="День 0", font=("Segoe UI", 24, "bold"), bg=self.bg, fg=self.fg)
        self.day_label.pack(pady=10)

        self.img_alive = tk.PhotoImage(file="queen_alive.png").subsample(2, 2)
        self.img_dead = tk.PhotoImage(file="queen_dead.png").subsample(2, 2)

        main_frame = tk.Frame(self.root, bg=self.bg)
        main_frame.pack()

        self.left_data = tk.Label(main_frame, justify="left", anchor="n", bg=self.bg, fg=self.fg,
                                  font=self.font_main, width=35, height=25)
        self.left_data.pack(side=tk.LEFT, padx=10, pady=10)

        self.image_label = tk.Label(main_frame, image=self.img_alive, bg=self.bg)
        self.image_label.pack(side=tk.LEFT, padx=10, pady=10)

        self.right_data = tk.Label(main_frame, justify="left", anchor="n", bg=self.bg, fg=self.fg,
                                   font=self.font_main, width=35, height=25)
        self.right_data.pack(side=tk.LEFT, padx=10, pady=10)

        button_frame = tk.Frame(self.root, bg=self.bg)
        button_frame.pack(pady=20)

        self.next_day_button = self.create_button(button_frame, "Следующий день", self.next_day)
        self.next_day_button.grid(row=0, column=0, padx=10)

        self.auto_button = self.create_button(button_frame, "Авто симуляция", self.toggle_auto)
        self.auto_button.grid(row=0, column=1, padx=10)

        self.pause_button = self.create_button(button_frame, "Показать параметры", self.show_stats)
        self.pause_button.grid(row=0, column=2, padx=10)

        self.exit_button = self.create_button(button_frame, "Выход", self.root.quit)
        self.exit_button.grid(row=0, column=3, padx=10)

    def create_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=self.font_bold,
            bg="#444",
            fg=self.fg,
            activebackground="#666",
            activeforeground="#fff",
            relief="ridge",
            bd=1,
            highlightthickness=0,
            padx=20,
            pady=10
        )

    def update_ui(self):
        total_starved = sum(self.starved_counts.values())
        cleaners_waiting = sum(
            1 for cleaner in self.workers_cleaner
            if not any(corpse.get("weight", 3) < cleaner["weight"] for corpse in self.dead_bees)
        )

        self.day_label.config(text=f"День {self.day}")
        self.left_data.config(text=f"""
Личинок: {len(self.larvae)}
Трутней: {len(self.drones)}
Рабочих (добыча): {len(self.workers_honey)}
Рабочих (уборка): {len(self.workers_cleaner)}
        """)
        self.right_data.config(text=f"""
Мед в хранилище: {self.honey_storage}
Мертвых пчел: {len(self.dead_bees)}

Смертей от голода: {total_starved}
  - Трутни: {self.starved_counts['drones']}
  - Рабочие (добыча): {self.starved_counts['workers_honey']}
  - Рабочие (уборка): {self.starved_counts['workers_cleaner']}

Выметающих в ожидании: {cleaners_waiting}
        """)
        self.image_label.config(image=self.img_alive if self.queen_alive else self.img_dead)

        if not self.queen_alive:
            self.next_day_button.config(state=tk.DISABLED)
            self.auto_running = False

    def next_day(self):
        if not self.queen_alive:
            return

        self.day += 1
        self.produce_eggs()
        self.process_larvae()
        self.feed_and_collect()
        self.clean_dead_bees()

        if self.check_queen_death():
            self.queen_alive = False
            self.update_ui()
            self.root.after(300, lambda: messagebox.showinfo("Матка умерла", f"Матка погибла на {self.day}-й день. Причина: {'старость' if self.day > 50 else 'недостаток мёда'}"))
            return

        self.update_ui()
        if self.auto_running:
            self.root.after(500, self.next_day)

    def toggle_auto(self):
        self.auto_running = not self.auto_running
        if self.auto_running:
            self.auto_button.config(text="Пауза")
            self.next_day()
        else:
            self.auto_button.config(text="Авто симуляция")

    def produce_eggs(self):
        productivity = 5 + int(self.honey_storage / 200)
        if len(self.dead_bees) > 20:
            productivity = max(0, productivity - len(self.dead_bees) // 10)
        self.larvae += [{"weight": 1, "age": 0} for _ in range(productivity)]

    def process_larvae(self):
        new_drones = []
        new_workers_honey = []
        new_workers_cleaner = []
        survived = []

        for larva in self.larvae:
            larva["age"] += 1
            larva["weight"] += 1
            if larva["age"] >= 3:
                roll = random.random()
                if roll < 0.3:
                    new_drones.append({"weight": 5, "age": 0})
                elif roll < 0.65:
                    new_workers_honey.append({"weight": 3, "age": 0})
                else:
                    new_workers_cleaner.append({"weight": 3, "age": 0})
            else:
                survived.append(larva)

        self.larvae = survived
        self.drones += new_drones
        self.workers_honey += new_workers_honey
        self.workers_cleaner += new_workers_cleaner

    def feed_and_collect(self):
        honey_collected = sum(w["weight"] for w in self.workers_honey)
        all_bees = self.workers_honey + self.workers_cleaner + self.drones
        honey_eaten = sum(bee["weight"] for bee in all_bees)

        self.honey_storage += honey_collected - honey_eaten

        if self.honey_storage < 0:
            self.honey_storage = 0
            deaths = random.sample(all_bees, min(5, len(all_bees)))
            for bee in deaths:
                if bee in self.drones:
                    self.drones.remove(bee)
                    self.starved_counts["drones"] += 1
                elif bee in self.workers_honey:
                    self.workers_honey.remove(bee)
                    self.starved_counts["workers_honey"] += 1
                elif bee in self.workers_cleaner:
                    self.workers_cleaner.remove(bee)
                    self.starved_counts["workers_cleaner"] += 1
                self.dead_bees.append(bee)

    def clean_dead_bees(self):
        cleaned = []
        for cleaner in self.workers_cleaner:
            for corpse in self.dead_bees:
                if corpse.get("weight", 3) < cleaner["weight"]:
                    cleaned.append(corpse)
                    break
        self.dead_bees = [b for b in self.dead_bees if b not in cleaned]

    def check_queen_death(self):
        return self.day > 50 or (self.honey_storage < 50 and random.random() < 0.2)

    def show_stats(self):
        total_starved = sum(self.starved_counts.values())
        cleaners_waiting = sum(
            1 for cleaner in self.workers_cleaner
            if not any(corpse.get("weight", 3) < cleaner["weight"] for corpse in self.dead_bees)
        )

        messagebox.showinfo("Статистика", f"""
День: {self.day}
Личинок: {len(self.larvae)}
Трутней: {len(self.drones)}
Рабочих (добыча): {len(self.workers_honey)}
Рабочих (уборка): {len(self.workers_cleaner)}

Мед в хранилище: {self.honey_storage}
Мертвых пчел: {len(self.dead_bees)}

Смертей от голода: {total_starved}
  - Трутни: {self.starved_counts['drones']}
  - Рабочие (добыча): {self.starved_counts['workers_honey']}
  - Рабочие (уборка): {self.starved_counts['workers_cleaner']}

Выметающих в ожидании: {cleaners_waiting}
""")


if __name__ == "__main__":
        root = tk.Tk()
        app = BeeSimulation(root)
        root.mainloop()
