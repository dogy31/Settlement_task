from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit
from PyQt6.QtCore import QTimer
import sys
from hive_logic import Hive

class HiveSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Симулятор Пчелиной Семьи")
        self.setGeometry(100, 100, 600, 500)
        self.hive = Hive()

        self.layout = QVBoxLayout()
        self.stats = QTextEdit()
        self.stats.setReadOnly(True)

        self.start_btn = QPushButton("Старт")
        self.start_btn.clicked.connect(self.start_simulation)
        self.stop_btn = QPushButton("Стоп")
        self.stop_btn.clicked.connect(self.stop_simulation)

        self.layout.addWidget(self.start_btn)
        self.layout.addWidget(self.stop_btn)
        self.layout.addWidget(self.stats)
        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)

    def start_simulation(self):
        self.timer.start(500)

    def stop_simulation(self):
        self.timer.stop()

    def update_simulation(self):
        self.hive.next_step()
        self.display_stats()

    def display_stats(self):
        stats = self.hive
        idle_cleaners = sum(1 for w in stats.workers if w.role == "cleaner" and w.idle)
        hunger_deaths = sum(1 for b in stats.dead_bees if b.age <= MAX_AGE)

        text = f"""
--- Статистика Улья ---
Шаг симуляции: {stats.tick}
Мед в хранилище: {stats.storage.honey:.2f}
Личинок: {len(stats.larvae)}
Трутней: {len(stats.drones)}
Рабочих пчел: {len(stats.workers)}
Мертвых пчел: {len(stats.dead_bees)}
Умерли от голода: {hunger_deaths}
Простаивающих чистильщиков: {idle_cleaners}
"""
        self.stats.setText(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HiveSimulator()
    window.show()
    sys.exit(app.exec())
