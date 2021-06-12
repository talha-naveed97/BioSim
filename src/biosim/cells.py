from .animals import Herbivore, Carnivore


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
                obj = Carnivore(x['age'], x['weight'])
                self.carnivores.append(obj)

    def calculate_cell_fitness(self):
        for animal in self.herbivores + self.carnivores:
            animal.calculate_fitness()

    def cell_annual_lifecycle(self):
        new_born_herbivores = []
        new_born_carnivores = []
        fitness_herbivores = []
        fitness_carnivores = []
        # Calculate fitness of Animals in Cell
        self.calculate_cell_fitness()
        # Sort animals in cell by fitness

        # Feeding
        for animal in self.herbivores:
            feed_left = animal.feeds(self.food_status)
            self.food_status = feed_left

        self.herbivores.sort(key=lambda x: x.fitness, reverse=False)
        self.carnivores.sort(key=lambda x: x.fitness, reverse=True)

        for animal in self.carnivores:
            dummy = len(self.herbivores)
            continue_eating_cycle = animal.feeds(self.herbivores)
            self.herbivores = [animal for animal in self.herbivores if not animal.dead]
            if dummy < len(self.herbivores):
                raise ValueError(dummy,self.herbivores)
            if not continue_eating_cycle:
                break
        # Procreation
        self.procreates(len(self.herbivores),len(self.carnivores))
        # for animal in self.herbivores:
        #     baby = animal.procreation(len(self.herbivores))
        #     if baby is not None:
        #         new_born_herbivores.append(baby)
        # for animal in self.carnivores:
        #     baby = animal.procreation(len(self.carnivores))
        #     if baby is not None:
        #         new_born_carnivores.append(baby)

        # # Add New Borns
        # self.herbivores.extend(new_born_herbivores)
        # self.carnivores.extend(new_born_carnivores)
        # for baby in new_born_herbivores:
        #     baby = animal.procreation(len(self.herbivores))
        #     if baby is not None:
        #         new_born_herbivores.append(baby)

        # Migration, Aging, Weight Loss, Death
        for animal in self.herbivores + self.carnivores:
            animal.migration()
            animal.commence_aging()
            animal.commence_weight_loss()
            animal.death()
        # Remove dead animals from List
        self.herbivores = [animal for animal in self.herbivores if not animal.dead]
        self.carnivores = [animal for animal in self.carnivores if not animal.dead]


        return [a.fitness for a in self.herbivores],\
               [a.fitness for a in self.carnivores],\
               [a.age for a in self.herbivores],\
               [a.age for a in self.carnivores],\
                [a.weight for a in self.herbivores],\
                [a.weight for a in self.carnivores],\

    def get_migration_possibilities(self):
        return [(self.loc[0] - 1, self.loc[1]), (self.loc[0] + 1, self.loc[1]),
                (self.loc[0], self.loc[1] - 1), (self.loc[0], self.loc[1] + 1)]

    def procreates(self,number_of_herbs,number_of_carns):
        index = 0
        while index < len(self.herbivores):
            animal = self.herbivores[index]
            baby = animal.procreation(number_of_herbs)
            if baby is not None:
                self.herbivores.append(baby)
            index += 1
        index = 0
        while index < len(self.carnivores):
            animal = self.carnivores[index]
            baby = animal.procreation(number_of_carns)
            if baby is not None:
                self.carnivores.append(baby)
            index += 1




    def reset_cell(self):
        self.food_status = self.f_max



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
    if land_type == 'W':
        Water.update_defaults(params)
    elif land_type == 'H':
        Highland.update_defaults(params)
    elif land_type == 'L':
        Lowland.update_defaults(params)
    elif land_type == 'D':
        Desert.update_defaults(params)
