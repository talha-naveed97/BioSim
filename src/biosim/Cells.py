from .animals import Herbivore


class Cell:
    def __init__(self, loc):
        self.loc = loc
        self.herbivores = []
        self.carnivores = []
        self.food_status = self.f_max

    @classmethod
    def update_defaults(cls, params):
        cls.f_max = params["f_max"]

    def add_animal(self, animals):
        for x in animals:
            if x['species'] == 'Herbivore':
                obj = Herbivore(x['age'], x['weight'])
                self.herbivores.append(obj)
            else:
                print('Add carnivore')

    def cell_annual_lifecycle(self):
        new_born_herbivores = []
        new_born_carnivores = []
        for animal in self.herbivores:
            animal.calculate_fitness()
            feed_left = animal.feeds(self.food_status)
            self.food_status = feed_left
            baby = animal.procreation(len(self.herbivores))
            if baby is not None:
                new_born_herbivores.append(baby)
            animal.migration()
            animal.commence_aging()
            animal.commence_weight_loss()
            animal.death()
        self.herbivores = [animal for animal in self.herbivores if not animal.dead]

        for animal in self.carnivores:
            animal.calculate_fitness()
            baby = animal.procreation(len(self.carnivores))
            if baby is not None:
                new_born_carnivores.append(baby)
            animal.migration()
            animal.commence_aging()
            animal.commence_weight_loss()
            animal.death()
        self.carnivores = [animal for animal in self.carnivores if not animal.dead]

        self.herbivores.extend(new_born_herbivores)
        self.carnivores.extend(new_born_carnivores)

    def reset_cell(self):
        self.food_status = self.f_max


class Water(Cell):
    f_max = 0
    allows_animal = False

    def __init__(self, loc):
        super().__init__(loc)


class Lowland(Cell):
    f_max = 800
    allows_animal = True

    def __init__(self, loc):
        super().__init__(loc)


class Highland(Cell):
    f_max = 300
    allows_animal = True

    def __init__(self, loc):
        super().__init__(loc)


class Desert(Cell):
    f_max = 0
    allows_animal = True

    def __init__(self, loc):
        super().__init__(loc)

def set_params(land_type, params):
    if land_type == 'W':
        Water.update_defaults(params)
    elif land_type == 'H':
        Highland.update_defaults(params)
    elif land_type == 'L':
        Lowland.update_defaults(params)
    elif land_type == 'D':
        Desert.update_defaults(params)
