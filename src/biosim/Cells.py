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

        for animal in self.carnivores:
            animal.calculate_fitness()
            baby = animal.procreation(len(self.carnivores))
            if baby is not None:
                new_born_carnivores.append(baby)
            animal.migration()
            animal.commence_aging()
            animal.commence_weight_loss()
            animal.death()


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
