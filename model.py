import mesa
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
import random as rnd
import matplotlib.pyplot as plt
import os
import Agents as CA

class Floor (Model):
    def __init__(self, floorplan, human_count):
        super().__init__()
        self.n_agents = human_count
        self.floorplan = []
        self.humans = []
        self.obstacles = []
        self.exits = []
        self.spawns = []
        # self.scheduler = DistanceScheduler(self)

 # Непрерывное пространство
        size = len(self.floorplan[0]), len(self.floorplan)
        self.space = ContinuousSpace(size[0], size[1], torus=False)
        self.grid = []

        for y in range(6 * size[1]):
            row = []
            for x in range(6 * size[0]):
                row.append(CA.Node((x, y)))
            self.grid.append(row)

# Помещаем все элементы в пространство
        for x in range(size[0]):
            for y in range(size[1]):
                value = str(self.floorplan[y][x])

                if value == 'W':
                    self.new_agent(CA.Wall, (x, y))
                    for i in range(6 * x, 6 * (x + 1)):
                        for j in range(6 * y, 6 * (y + 1)):
                            self.grid[j][i].done = True

                # elif value == 'O':
                #     self.new_agent(ca.Obstacles, (x, y))
                #     for i in range(6 * x, 6 * (x + 1)):
                #         for j in range(6 * y, 6 * (y + 1)):
                #             self.grid[j][i].done = True

                elif value == 'S':
                    self.spawns.append((x, y))

                elif value == 'E':
                    self.new_agent(CA.Exit, (x, y))
                    i = 6 * x + 1
                    j = 6 * y + 1
                    self.grid[j][i].exit = True
# Создание агентов в указанных координатах
        humans = rnd.sample(self.spawns, self.n_agents)
        for pos in humans:
            self.new_agent(CA.Human, pos)
        print("Floor initialised.")


# СОздание метода, который добавляет новые агенты в нужный список
    def new_agent(self, agent_type, pos):
        agent = agent_type(self, pos)
        self.space.place_agent(agent, pos)

        if agent_type.__name__ == "Human":
            self.humans.append(agent)
        elif agent_type.__name__ == "Exit":
            self.exits.append(agent)
        else:
            self.obstacles.append(agent)

# Мотод удаления агента + планировщик
    def remove_agent(self, agent):
        self.space.remove_agent(agent)
        if {type(agent).__name__} == "Human":
            self.scheduler.remove(agent)
            self.humans.remove(agent)

    def step(self):
        self.scheduler.step()

    def run_model(self):
        self.step()