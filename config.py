# DanGenLife Ecosystem - Configuration

# Параметры мира (Сетка)
GRID_WIDTH = 100
GRID_HEIGHT = 100
INITIAL_PLANKTON_DENSITY = 0.4  # Чуть больше еды на старте

# Энергетический баланс
PLANKTON_ENERGY = 10      # Увеличил (было 5), чтобы травоядные жили дольше
ENERGY_LOSS_PER_STEP = 0.2 # Снизил базовую трату (было 1), чтобы хищники не умирали мгновенно
REPRODUCTION_COST = 30     # Стоимость размножения

# Параметры Хищников
PREDATOR_REPRODUCTION_THRESHOLD = 100 # Порог для размножения красных
APEX_REPRODUCTION_THRESHOLD = 150     # Апексам нужно больше энергии для потомка

# Генетика и Мутации 
MUTATION_RATE = 0.2       
MUTATION_STRENGTH = 0.2  

# Диапазоны генов
GENE_LIMITS = {
    'speed': (0.1, 1.5),      # Поднял верхний порог для эволюции
    'metabolism': (0.1, 2.0), # Снизил нижний порог
    'vision': (1, 15)         # Увеличил радиус (было 5), чтобы Апексы видели дальше 
}