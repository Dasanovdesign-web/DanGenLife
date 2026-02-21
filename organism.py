import random

class Organism:
    def __init__(self, x, y, parent_genes=None):
        self.x = x
        self.y = y
        self.energy = 20
        
        if parent_genes is None:
            self.genes = {
                "speed": 0.5,
                "metabolism": 0.5,
                "efficiency": 1.0,
                "vision": 10.0  # Радиус зрения
            }
        else:
            self.genes = self.mutate_all(parent_genes)

    def mutate_all(self, p_genes):
        new_genes = {}
        mutation_strength = 0.1
        for name, value in p_genes.items():
            factor = 1 + random.uniform(-mutation_strength, mutation_strength)
            new_genes[name] = max(0.01, value * factor)
        return new_genes

    def move(self, width, height):
        if random.random() < self.genes["speed"]:
            self.x = (self.x + random.randint(-1, 1)) % width
            self.y = (self.y + random.randint(-1, 1)) % height
        self.energy -= self.genes["metabolism"]