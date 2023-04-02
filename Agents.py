# import numpy as np
# from mesa import Agent
# # Узел для поиска пути по алгоритму
# #  self.pos : позиция в сетке
# #  self.done : проверка узла
# #  self.exit : проверка на выход
# #  self.path : кротчайший путь к узлу
#
# class Node:
#     def __init__(self, position):
#         self.pos = position
#         self.done = False
#         self.exit = False
#         self.path = []
#
# def __str__(self):
#     x, y = self.pos
#     return f"{x / 6, y / 6}"
#
# # Родительский класс для всех агентов
#
# class Objects (Agent):
#     def __init__(self, model, pos):
#         super().__init__(model.next_id(), model)
#         self.pos = pos
#         self.model = model
#
#     def get_position(self):
#         return self.pos
#
# # class Obstacles(Objects):
# #     def __init__(self, model, pos):
# #         super().__init__(model, pos)
#
# class Wall(Objects):
#     def __init__(self, model, pos):
#         super().__init__(model, pos)
#
# class Exit(Objects):
#     def __init__(self, model, pos):
#         super().__init__(model, pos)
#
# # Люди в модели
#
# # self.new_pos : цель для перемещения
# # self.node : ближайший узел
# # self.path : кротчайший путь
# # self.dist : длина кротчайшего пути
#
# class Human(Objects):
#     def __init__(self, model, pos):
#         super().__init__(model, pos)
#         getattr(model, f'scheduler').add(self)
#         self.new_pos = 0
#         self.node = 6 * self.pos[0], 6 * self.pos[1]
#         self.path = dijkstra(self.model.grid, self.node)
#         self.dist = len(self.path)
#
# # Движение агентов в пространстве
#     def move(self):
#         self.model.space.move_agent(self, self.new_pos)
#
# # Выполнение всех методов для первого шага
#     def step(self):
#         try:
#             self.dijkstra()
#             self.get_node()
#             self.force()
#             self.move()
#         except Exception as e:
#             print(e)
#
# # Удаление агента
#     def saved(self):
#         self.model.remove_agent(self)


import matplotlib.pyplot as plt
from matplotlib import image
import numpy as np
import json
import re

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector


class AgentEnvironmentMap:
    def __init__(self, bw_image_path, dist_per_pix=1.0):
        self.img = image.imread(bw_image_path)
        self.shape = (self.img.shape[0], self.img.shape[1])
        self.dist_per_pix = dist_per_pix
        self.max_x = self.shape[1] * dist_per_pix - 1
        self.max_y = self.shape[0] * dist_per_pix - 1
        self.wall_mask = np.zeros(self.shape, dtype=bool)
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                self.wall_mask[i, j] = self.img[i, j, 0] < 0.1

    def is_wall(self, x, y):
        i = int(y / self.dist_per_pix)
        j = int(x / self.dist_per_pix)
        return self.wall_mask[i, j]

    def to_ascii1(self):
        return '\n'.join([''.join(['#' if m else '.' for m in ln]) for ln in self.wall_mask])


class PhysicalAgent(Agent):
    def __init__(self, unique_id, model):
        self.is_moving = True
        super().__init__(unique_id, model)

    def reset_waypoints(self, waypoints=None):
        if waypoints:
            self.waypoints = waypoints
        self.model.space.move_agent(self, self.waypoints[0])
        self.next_waypoint_index = 1
        self.is_moving = True

    def get_points_to_show(self):
        return {'agent': self.pos, 'final_target': self.waypoints[-1],
                'next_target': self.waypoints[self.next_waypoint_index]}

    def step(self):
        TARGET_SENSITIVITY = 3
        search_target = True
        while search_target:
            dx = self.waypoints[self.next_waypoint_index][0] - self.pos[0]
            dy = self.waypoints[self.next_waypoint_index][1] - self.pos[1]
            d = np.sqrt(dx * dx + dy * dy)
            if d < TARGET_SENSITIVITY:
                if self.next_waypoint_index < len(self.waypoints) - 1:
                    self.next_waypoint_index += 1
                else:
                    self.is_moving = False
                    return
            else:
                search_target = False
        new_x = self.pos[0] + 5 * dx / d
        new_y = self.pos[1] + 5 * dy / d
        if not self.model.env_map.is_wall(new_x, new_y):
            print(f'#{self.unique_id} is moving to ({new_x}, {new_y}) fowards waypoint #{self.next_waypoint_index}')
            self.model.space.move_agent(self, (new_x, new_y))

class IndoorModel(Model):
    def __init__(self, agents_json_path='agents.json', env_map_path='map_2floor_bw.png'):
        hard_dx = 235
        hard_dy = 76
        self.path = env_map_path
        self.env_map = AgentEnvironmentMap(env_map_path)
        self.space = ContinuousSpace(self.env_map.max_x, self.env_map.max_y, False)
        self.schedule = RandomActivation(self)
        with open(agents_json_path) as f:
            agent_json = json.load(f)
        for i, aj in enumerate(agent_json):
            with open(aj['waypoints_path']) as f:
                lns = f.readlines()
                waypoints = []
                for ln in lns:
                    parts = re.findall('\d+', ln)
                    waypoints.append((int(parts[0].strip()) - hard_dx, int(parts[1].strip()) - hard_dy))
            a = PhysicalAgent(i, self)
            self.schedule.add(a)
            self.space.place_agent(a, waypoints[0])
            a.reset_waypoints(waypoints)
        # self.data_collector = DataCollector({'target_x': lambda m: m.target[0], 'target_y': lambda m: m.target[1], 'moving_agents_num': 'moving_agents_num'},
        #     {'is_moving': 'is_moving', 'x': lambda a: a.pos[0], 'y': lambda a: a.pos[1]})
        self.data_collector = DataCollector({'moving_agents_num': 'moving_agents_num'},
                                            {'is_moving': 'is_moving', 'x': lambda a: a.pos[0],
                                             'y': lambda a: a.pos[1]})
        self.moving_agents_num = 0
        self.running = True
        self.data_collector.collect(self)

    def step(self):
        self.schedule.step()
        self.data_collector.collect(self)
        self.moving_agents_num = sum([a.is_moving for a in self.schedule.agents])
        self.running = self.moving_agents_num > 0

    def plot_explicitly(self):
        plt.imshow(self.env_map.img)
        for a in self.schedule.agents:
            plt.plot(a.pos[0], a.pos[1], 'bo')
        # plt.plot(self.target[0], self.target[1], 'r+')