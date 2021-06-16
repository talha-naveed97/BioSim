# -*- coding: utf-8 -*-

"""
This module implements the Animals class to simulate the animals found on Rossumøya island.
The two subclasses, Herbivore and Carnivore represent the two types of animals and define
their respective characteristics and functions such as the way each type of animal feeds.
"""

import math
import random


class Animals:
    """
    The Animals class.

    Attributes
    __________
    age
        *int*: Age of the animal.

        |

    weight
        *float*: Weight of the animal.

        |

    dead
        *bool*: *True* if the animal dies, *False* otherwise.

        |

    fitness
        *float*: Fitness of the animal.

        |

    can_migrate
        *bool*: *True* if animal is likely to migrate to another cell, *False* otherwise.

        |

    has_migrated
        *bool*: *True* if animal has migrated to another cell, *False* otherwise.
        Cannot be *True* if **can_migrate** is *False*.

        |

    """

    def __init__(self, age, weight):
        self.age = age
        self.weight = weight
        self.calculate_fitness()
        self.can_migrate = False
        self.has_migrated = False
        self.dead = False

    @classmethod
    def update_defaults(cls, params):
        """
        Update default characteristics of animals.

        Parameters
        ----------
        params : dict
            Dictionary of *guideline_params* for each type of animal.

            .. seealso::
                - animals.Herbivore()
                - animals.Carnivore()

        .. code-block:: python

            params = {'zeta': 1.2}
            Herbivore.update_defaults(params)


            |

        """

        key_diff = params.keys() - cls.guideline_params.keys()
        if len(key_diff) != 0:
            raise ValueError('The following keys are invalid: ', key_diff)
        if 'DeltaPhiMax' in params.keys() and params['DeltaPhiMax'] <= 0:
            raise ValueError('DeltaPhiMax must be > zero')
        for key, value in params.items():
            if type(value) is not int and type(value) is not float:
                raise ValueError('All parameter values must be numerical')
            if value < 0:
                raise ValueError('All parameter values must be >= zero')
        cls.guideline_params.update(params)

    def calculate_fitness(self):
        """
        Calculate fitness (between 0 and 1) of an animal using the equation:
            .. math::
                \\Phi =
                \\begin{cases}
                    0 & \\text{if } w \\le 0

                    q^{+}(a,a_{\\frac{1}{2}},\\phi_{age}) \\times
                    q^{-}(w,w_{\\frac{1}{2}},\\phi_{weight}) &
                    \\text{else}
                \\end{cases}

        where
            .. math::
                q^{\\pm}(a,a_{\\frac{1}{2}},\\phi) =  \\frac{1}{1 + e^{\\pm\\phi(x-x_\\frac{1}{2})}}


        .. code-block:: python

            herbivore = Herbivore(age=10, weight =20)
            herbivore.calculate_fitness()
            print(herbivore.fitness)


        |

        """
        try:
            if self.weight <= 0:
                self.fitness = 0
            else:
                q_age = 1 / (1 + math.exp(self.guideline_params["phi_age"] *
                                          (self.age - self.guideline_params["a_half"])))
                q_weight = 1 / (1 + math.exp(-self.guideline_params["phi_weight"] *
                                             (self.weight - self.guideline_params["w_half"])))
                self.fitness = q_age * q_weight
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while executing calculate_fitness(): {}'.format(err))

    def procreation(self, cell_animal_count):
        """
        Compute the probability for an animal giving birth:
            .. math::
                \\text{min}(1, \\gamma \\times \\Phi \\times (N-1))

        and returns **baby**: a newborn animal in the similar class or None if no procreation.

        Parameters
        ----------
        cell_animal_count : int
            Number of animals of a species in a cell. Probability of giving birth is only
            calculated if there are at least two animals of the same species present in a cell.


        .. code-block:: python

            herbivore = Herbivore(age=10, weight =20)
            baby = herbivore.procreation()
            if baby is not None:
                print("baby added")
                baby_age = baby.age

        |


        """
        try:
            birth_prob = 0
            if cell_animal_count > 1 and self.weight >= self.guideline_params["zeta"] * \
                    (self.guideline_params["w_birth"] + self.guideline_params["sigma_birth"]):
                birth_prob = min(1, self.guideline_params["gamma"] *
                                 self.fitness * (cell_animal_count - 1))
            if birth_prob > random.random():
                baby_age = 0
                baby_weight = random.gauss(self.guideline_params["w_birth"],
                                           self.guideline_params["sigma_birth"])
                mother_weight_loss = self.guideline_params["xi"] * baby_weight
                if self.weight >= mother_weight_loss:
                    baby = self.__class__(baby_age, baby_weight)
                    self.weight -= mother_weight_loss
                    self.calculate_fitness()
                    return baby
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while executing procreation(): {}'.format(err))

        return None

    def migration(self):
        """
        Compute migration probability for the animal:
            .. math::
                \\mu \\Phi

        and set **can_migrate** as *True* if probability is higher than a random threshold.

        .. code-block:: python

            herbivore = Herbivore(age=10, weight =20)
            herbivore.migration()
            if herbivore.can_migrate:
                print("Animal can migrate")
            else
                print("Animal can not migrate")


        |

        """
        try:
            migration_prob = self.guideline_params["mu"] * self.fitness
            if migration_prob > random.random():
                self.can_migrate = True
            else:
                self.can_migrate = False
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while executing migration(): {}'.format(err))

    def commence_aging(self):
        """
        Increase animal age by 1 year and recompute animal weight and fitness.

        .. code-block:: python

            herbivore = Herbivore(age=10, weight =20)
            herbivore.commence_aging()
            print("Animal Age", herbivore.age)
            print("Animal Weight", herbivore.weight)


        |

        """
        try:
            self.age += 1
            self.weight -= self.weight * self.guideline_params["eta"]
            self.has_migrated = False
            self.calculate_fitness()
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while executing commence_aging(): {}'.format(err))

    def death(self):
        """
        Compute probability of the animal dying and set ``dead`` as *True*
        if probability is higher than a random threshold. The probability is
        computed as:

            .. math::
                p_{death} =
                \\begin{cases}
                    1 & \\text{if } w_{animal} = 0

                    \\omega(1 - \\Phi) & \\text{otherwise.}
                \\end{cases}

        .. code-block:: python

            herbivore = Herbivore(age=10, weight =20)
            herbivore.death()
            if herbivore.dead:
                print("Animal will die")
            else
                print("Animal will not die")


        |

        """
        try:
            if self.weight <= 0:
                self.dead = True
            else:
                death_prob = self.guideline_params["omega"] * (1 - self.fitness)
                if death_prob > random.random():
                    self.dead = True
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while executing death(): {}'.format(err))


class Herbivore(Animals):
    """
    The 'Herbivore' animal type, subclass of *Animals* class: feeds on fodder in
    lowland and highland. Herbivores eat in random order the amount *F* from the
    fodder available in the cell. Subsequently, its weight increases by:

    .. math::
        \\Delta w_{herb} = \\beta F


    .. list-table:: Default characteristics *guideline_params* of Herbivores
            :widths: 25 25
            :header-rows: 1

            * - Parameter name
              - Value

            * - ``w_birth``
              - 8.0
            * - ``sigma_birth``
              - 1.5
            * - ``beta``
              - 0.9
            * - ``eta``
              - 0.05
            * - ``a_half``
              - 40.0
            * - ``phi_age``
              - 0.6
            * - ``w_half``
              - 10.0
            * - ``phi_weight``
              - 0.1
            * - ``mu``
              - 0.25
            * - ``gamma``
              - 0.2
            * - ``zeta``
              - 3.5
            * - ``xi``
              - 1.2
            * - ``omega``
              - 0.4
            * - ``F``
              - 10.0
            * - ``DeltaPhiMax``
              - None

    |

    """

    def __init__(self, age, weight):
        super().__init__(age, weight)

    guideline_params = {'w_birth': 8.0,
                        'sigma_birth': 1.5,
                        'beta': 0.9,
                        'eta': 0.05,
                        'a_half': 40.0,
                        'phi_age': 0.6,
                        'w_half': 10.0,
                        'phi_weight': 0.1,
                        'mu': 0.25,
                        'gamma': 0.2,
                        'zeta': 3.5,
                        'xi': 1.2,
                        'omega': 0.4,
                        'F': 10.0,
                        'DeltaPhiMax': None
                        }

    def feeds(self, cell_food_amount):
        """
        Feeding function for herbivores.

        Returns **feed_left**: the amount of food left in the cell after herbivore has eaten.

        Parameters
        ----------
        cell_food_amount : float
            The amount of food available in the cell.


        .. code-block:: python

            herbivore = Herbivore(age=10, weight =20)
            herbivore.feeds()
            print("Animal after weight", herbivore.weight)


        |

        """
        try:
            f = self.guideline_params["F"]
            if f > cell_food_amount:
                f = cell_food_amount
            self.weight += f * self.guideline_params["beta"]
            self.calculate_fitness()
            feed_left = cell_food_amount - f
            return feed_left
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while executing Herbivore.feeds(): {}'.format(err))


class Carnivore(Animals):
    """
    The 'Carnivore' animal type, subclass of *Animals* class: preys on herbivores but
    do not prey on each other. A carnivore continues to kills herbivores until it has
    eaten a specific amount or until it has tried to kill each herbivore present in
    the cell. The probability *p* of carnivores killing a herbivore is given by:

        .. math::
                p =
                \\begin{cases}
                    0 & \\text{if } \\Phi_{carn} \\le \\Phi_{herb}

                    \\frac{\\Phi_{carn} - \\Phi_{herb}}{\\Delta \\Phi_{max}} &
                    \\text{if } 0 \\le \\Phi_{carn} - \\Phi_{herb} \\le \\Phi_{max}

                    1 & \\text{otherwise.}

                \\end{cases}


        .. list-table:: Default characteristics of Carnivores
            :widths: 25 25
            :header-rows: 1

            * - Parameter name
              - Value

            * - ``w_birth``
              - 6.0
            * - ``sigma_birth``
              - 1.0
            * - ``beta``
              - 0.75
            * - ``eta``
              - 0.125
            * - ``a_half``
              - 40.0
            * - ``phi_age``
              - 0.3
            * - ``w_half``
              - 4.0
            * - ``phi_weight``
              - 0.4
            * - ``mu``
              - 0.4
            * - ``gamma``
              - 0.8
            * - ``zeta``
              - 3.5
            * - ``xi``
              - 1.1
            * - ``omega``
              - 0.8
            * - ``F``
              - 50.0
            * - ``DeltaPhiMax``
              - 10.0

    |

    """

    def __init__(self, age, weight):
        super().__init__(age, weight)

    guideline_params = {'w_birth': 6.0,
                        'sigma_birth': 1.0,
                        'beta': 0.75,
                        'eta': 0.125,
                        'a_half': 40.0,
                        'phi_age': 0.3,
                        'w_half': 4.0,
                        'phi_weight': 0.4,
                        'mu': 0.4,
                        'gamma': 0.8,
                        'zeta': 3.5,
                        'xi': 1.1,
                        'omega': 0.8,
                        'F': 50.0,
                        'DeltaPhiMax': 10.0
                        }

    def feeds(self, herbivores):
        """
        Function for carnivores preying on herbivores.

        Parameters
        ----------
        herbivores : list
            The list of herbivores present in the cell. The attribute **dead** is set *True*
            for each herbivores that is killed by the carnivore.


        .. code-block:: python

            carnivore = Carnivore(age=10, weight =20)
            herbivores = [Herbivore(1, 10) for _ in range(2)]
            carnivore.feeds(herbivores)
            print("Animal after weight", carnivore.weight)


        |

        """
        try:
            amount_eaten = 0
            for herbivore in herbivores:
                fitness_difference = self.fitness - herbivore.fitness
                if self.fitness <= herbivore.fitness:
                    eating_probability = 0
                elif 0 < fitness_difference < self.guideline_params["DeltaPhiMax"]:
                    eating_probability = fitness_difference / self.guideline_params["DeltaPhiMax"]
                else:
                    eating_probability = 1

                if eating_probability > random.random():
                    herbivore.dead = True
                    self.weight += self.guideline_params["beta"] * herbivore.weight
                    amount_eaten += herbivore.weight
                    self.calculate_fitness()
                    if amount_eaten >= self.guideline_params["F"]:
                        break
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while executing Carnivore.feeds(): {}'.format(err))

        return None


def set_animal_params(species, params):
    """

    Parameters
    ----------
    species : str
        Class of animal, *'Herbivore'* or *'Carnovire'*

    params : dict
        Dictionary of *guideline_params* for each type of animal.

        .. seealso::
            - Animals.update_defaults()


    .. code-block:: python

        set_animal_params('Herbivore', params = {'age': 10, 'weight': 20})


    |

    """
    if species == 'Herbivore':
        Herbivore.update_defaults(params)
    elif species == 'Carnivore':
        Carnivore.update_defaults(params)
    else:
        raise ValueError('Cannot identify species')
