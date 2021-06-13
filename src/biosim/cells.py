from .animals import Herbivore, Carnivore


class Cell:
    def __init__(self, loc):
        self.loc = loc
        self.herbivores = []
        self.carnivores = []
        self.food_status = self.f_max

    @classmethod
    def update_defaults(cls, params):
        if len(params.keys()) > 1:
            raise ValueError('Cell accepts only one key i.e f_max')
        valid_key = {'f_max': None}
        key_diff = params.keys() - valid_key.keys()
        if len(key_diff) != 0:
            raise ValueError('Key value is invalid: ', key_diff)
        value = params['f_max']
        if type(value) is not int and type(value) is not float:
            raise ValueError('f_max must be numerical')
        if value < 0:
            raise ValueError('f_max cannot be less than zero')
        cls.f_max = params["f_max"]

    def add_animal(self, animals):
        for x in animals:
            if x['species'] == 'Herbivore':
                obj = Herbivore(x['age'], x['weight'])
                self.herbivores.append(obj)
            else:
                obj = Carnivore(x['age'], x['weight'])
                self.carnivores.append(obj)

    def animals_feed(self):
        for animal in self.herbivores:
            self.food_status = animal.feeds(self.food_status)
        # Sort animals in cell by fitness
        self.herbivores.sort(key=lambda x: x.fitness, reverse=False)
        self.carnivores.sort(key=lambda x: x.fitness, reverse=True)
        for animal in self.carnivores:
            continue_eating_cycle = animal.feeds(self.herbivores)
            self.herbivores = [animal for animal in self.herbivores if not animal.dead]
            self.herbivores.sort(key=lambda x: x.fitness, reverse=False)
            if not continue_eating_cycle:
                break

    def animals_procreate(self, number_of_herbivores, number_of_carnivores):
        index = 0
        while index < len(self.herbivores):
            animal = self.herbivores[index]
            baby = animal.procreation(number_of_herbivores)
            if baby is not None:
                self.herbivores.append(baby)
            index += 1
        index = 0
        while index < len(self.carnivores):
            animal = self.carnivores[index]
            baby = animal.procreation(number_of_carnivores)
            if baby is not None:
                self.carnivores.append(baby)
            index += 1

    def animals_migrate(self):
        for animal in self.herbivores + self.carnivores:
            animal.migration()

    def animals_age(self):
        for animal in self.herbivores + self.carnivores:
            animal.commence_aging()

    def animals_death(self):
        for animal in self.herbivores + self.carnivores:
            animal.death()

        self.herbivores = [herbivore for herbivore in self.herbivores if not herbivore.dead]
        self.carnivores = [carnivore for carnivore in self.carnivores if not carnivore.dead]

    def reset_cell(self):
        self.food_status = self.f_max

    def cell_annual_lifecycle(self):
        # Feeding
        self.animals_feed()
        # Procreation
        self.animals_procreate(len(self.herbivores), len(self.carnivores))
        # Migration Flag,
        self.animals_migrate()
        # Aging and weight loss
        self.animals_age()
        # Death
        self.animals_death()

        return [a.fitness for a in self.herbivores], \
               [a.fitness for a in self.carnivores], \
               [a.age for a in self.herbivores], \
               [a.age for a in self.carnivores], \
               [a.weight for a in self.herbivores], \
               [a.weight for a in self.carnivores]

    def get_migration_possibilities(self):
        return [(self.loc[0] - 1, self.loc[1]), (self.loc[0] + 1, self.loc[1]),
                (self.loc[0], self.loc[1] - 1), (self.loc[0], self.loc[1] + 1)]


class Water(Cell):
    f_max = 0
    allows_animal = False
    rgb = (0.0, 0.0, 1.0)


class Lowland(Cell):
    f_max = 800
    allows_animal = True
    rgb = (0.0, 0.6, 0.0)


class Highland(Cell):
    f_max = 300
    allows_animal = True
    rgb = (0.5, 1.0, 0.5)


class Desert(Cell):
    f_max = 0
    allows_animal = True
    rgb = (1.0, 1.0, 0.5)


def set_cell_params(land_type, params):
    if land_type == 'H':
        Highland.update_defaults(params)
    elif land_type == 'L':
        Lowland.update_defaults(params)
    elif land_type == 'D':
        Desert.update_defaults(params)
    elif land_type == 'W':
        raise ValueError('Water cannot have food')
    else:
        raise ValueError('Cannot Identify Land Type')
