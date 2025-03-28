import random

MAX_AGE = 50
LARVA_GROWTH_TIME = 5
HONEY_CONSUMPTION_RATE = 0.1
HONEY_PRODUCTION_RATE = 1.0
DRONE_EFFECTIVENESS = 3

class Bee:
    def __init__(self, bee_id, weight, age=0, max_age=MAX_AGE):
        self.id = bee_id
        self.weight = weight
        self.age = age
        self.max_age = max_age
        self.alive = True
        self.cause_of_death = None

    def consume_honey(self, storage):
        amount = self.weight * HONEY_CONSUMPTION_RATE
        if storage.honey >= amount:
            storage.honey -= amount
            return True
        self.alive = False
        self.cause_of_death = "hunger"
        return False

    def update_age(self):
        self.age += 1
        if self.age >= self.max_age:
            self.alive = False
            self.cause_of_death = "old_age"

class Queen(Bee):
    def __init__(self, bee_id, weight):
        super().__init__(bee_id, weight, max_age=200)  # Матка живет дольше
        self.productivity_base = 10

    def lay_eggs(self, storage):
        base_rate = min(int(storage.honey / 10), self.productivity_base)  # Ограничение продуктивности
        return [Larva(f"L{random.randint(1000,9999)}") for _ in range(base_rate)]

class Drone(Bee):
    def __init__(self, bee_id, weight):
        super().__init__(bee_id, weight, max_age=MAX_AGE)
        self.effectiveness = random.uniform(0, DRONE_EFFECTIVENESS)

class Worker(Bee):
    def __init__(self, bee_id, weight, role):
        super().__init__(bee_id, weight, max_age=MAX_AGE)
        self.role = role
        self.idle = False

    def do_work(self, storage, hive):
        self.idle = False
        if self.role == "collector":
            storage.honey += HONEY_PRODUCTION_RATE
        elif self.role == "cleaner":
            for dead in hive.dead_bees[:]:  # Используем копию для итерации
                if self.weight > dead.weight:
                    hive.dead_bees.remove(dead)
                    return
            self.idle = True

class Larva:
    def __init__(self, larva_id):
        self.id = larva_id
        self.age = 0
        self.weight = 0.5
        self.alive = True
        self.cause_of_death = None

    def grow(self, storage):
        if storage.honey >= 0.4:
            storage.honey -= 0.4
            self.weight += 0.4
            self.age += 1
            return True
        self.alive = False
        self.cause_of_death = "hunger"
        return False

    def transform(self):
        if random.random() < 0.7:
            return Worker(f"W{random.randint(1000,9999)}", self.weight, random.choice(["collector", "cleaner"]))
        else:
            return Drone(f"D{random.randint(1000,9999)}", self.weight)

class Storage:
    def __init__(self):
        self.honey = 100.0

class Hive:
    def __init__(self):
        self.storage = Storage()
        self.queen = Queen("Q1", 1.5)
        self.larvae = []
        self.drones = []
        self.workers = []
        self.dead_bees = []
        self.tick = 0

    def next_step(self):
        self.tick += 1

        # Проверка состояния матки
        if not self.queen.consume_honey(self.storage):
            self.dead_bees.append(self.queen)
        if self.queen.alive:
            self.queen.update_age()
            if self.queen.alive:
                new_larvae = self.queen.lay_eggs(self.storage)
                self.larvae.extend(new_larvae)
            else:
                self.dead_bees.append(self.queen)

        # Обработка личинок
        new_bees = []
        for larva in self.larvae[:]:
            if larva.grow(self.storage) and larva.age >= LARVA_GROWTH_TIME:
                new_bees.append(larva.transform())
                self.larvae.remove(larva)
            elif not larva.alive:
                self.larvae.remove(larva)
                self.dead_bees.append(larva)

        # Добавление новых пчел
        for bee in new_bees:
            if isinstance(bee, Drone):
                self.drones.append(bee)
            else:
                self.workers.append(bee)

        # Обработка рабочих пчел
        for worker in self.workers[:]:
            if not worker.consume_honey(self.storage):
                self.workers.remove(worker)
                self.dead_bees.append(worker)
                continue
            worker.update_age()
            if not worker.alive:
                self.workers.remove(worker)
                self.dead_bees.append(worker)
            else:
                worker.do_work(self.storage, self)

        # Обработка трутней
        for drone in self.drones[:]:
            if not drone.consume_honey(self.storage):
                self.drones.remove(drone)
                self.dead_bees.append(drone)
                continue
            drone.update_age()
            if not drone.alive:
                self.drones.remove(drone)
                self.dead_bees.append(drone)

    def get_stats(self):
        starved = sum(1 for b in self.dead_bees if b.cause_of_death == "hunger")
        return (f"Tick: {self.tick}\n"
                f"Queen alive: {self.queen.alive}\n"
                f"Larvae: {len(self.larvae)}\n"
                f"Drones: {len(self.drones)}\n"
                f"Workers: {len(self.workers)}\n"
                f"Honey: {self.storage.honey:.2f}\n"
                f"Dead bees: {len(self.dead_bees)}\n"
                f"Starved: {starved}")

    def queen_alive(self):
        return self.queen.alive

def main():
    hive = Hive()
    for _ in range(60):  # Симуляция 20 шагов
        if hive.queen_alive() == False:
            break
        hive.next_step()
        print(hive.get_stats())
        print("-" * 20)

if __name__ == "__main__":
    main()
