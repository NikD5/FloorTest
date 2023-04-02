# from os import listdir, path
#
# from mesa.visualization.modules import CanvasGrid, ChartModule
# from mesa.visualization.ModularVisualization import ModularServer
# from mesa.visualization.UserParam import UserSettableParameter
#
# from model import Floor
# from Agents import Exit, Wall, Objects, Human
#
# # Creates a visual portrayal of our model in the browser interface
# def Hospital(agent):
#     if agent is None:
#         return
#
#     portrayal = {}
#     (x, y) = agent.get_position()
#     portrayal["x"] = x
#     portrayal["y"] = y
#
#     if type(agent) is Human:
#         portrayal["scale"] = 1
#         portrayal["Layer"] = 5
#
#         # Normal agent
#         # portrayal["Shape"] = "resources/human.png"
#
#     elif type(agent) is Exit:
#         # portrayal["Shape"] = "resources/fire_exit.png"
#         portrayal["scale"] = 1
#         portrayal["Layer"] = 1
#
#     elif type(agent) is Wall:
#         # portrayal["Shape"] = "resources/wall.png"
#         portrayal["scale"] = 1
#         portrayal["Layer"] = 1
#
#     elif type(agent) is Objects:
#         # portrayal["Shape"] = "resources/furniture.png"
#         portrayal["scale"] = 1
#         portrayal["Layer"] = 1
#
#     return portrayal
#
# # Size of grid is hardcoded, if floorplan changes change grid size manually
# canvas_element = CanvasGrid(Hospital, 23, 17, 500, 500)
#
# # Specify the parameters changeable by the user, in the web interface
# model_params = {
#     "human_count": UserSettableParameter("slider", "Number Of Human Agents", 10, 1, 80),
#     "human_panic": UserSettableParameter("slider", "Panic", 0, 0, 7),
#     "human_speed": UserSettableParameter("slider", "Maximum speed", 3, 1, 5),
# }


import os
import base64
from mesa.visualization.ModularVisualization import ModularServer, VisualizationElement
from mesa.visualization.modules import TextElement
from mesa.visualization.UserParam import UserSettableParameter
from Agents import IndoorModel

class IndoorVisualCanvas(VisualizationElement):
    local_includes = ["simple_continuous_canvas.js"]

    def __init__(self, portrayal_method, canvas_height=500, canvas_width=500, bg_path=None):
        self.portrayal_method = portrayal_method
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        new_element = f"new Simple_Continuous_Module({self.canvas_width}, {self.canvas_height}, '{bg_path}')"
        self.js_code = "elements.push(" + new_element + ");"

    def transform_xy(self, model, pos):
        x, y = pos
        x = (x - model.space.x_min) / (model.space.x_max - model.space.x_min)
        y = (y - model.space.y_min) / (model.space.y_max - model.space.y_min)
        return x, y

    def render(self, model):
        space_state = []
        for obj in model.schedule.agents:
            # agent
            portrayal = self.portrayal_method(obj)
            portrayal["x"], portrayal["y"] = self.transform_xy(model, obj.pos)
            space_state.append(portrayal)
            # targets
            tg = obj.get_points_to_show()
            tm_portrayal = {'Shape': 'circle', 'r': 2, 'Filled': 'true', 'Color': 'magenta'}
            tm_portrayal["x"], tm_portrayal["y"] = self.transform_xy(model, tg['next_target'])
            space_state.append(tm_portrayal)
            tf_portrayal = {'Shape': 'circle', 'r': 2, 'Filled': 'true', 'Color': 'red'}
            tf_portrayal["x"], tf_portrayal["y"] = self.transform_xy(model, tg['final_target'])
            space_state.append(tf_portrayal)
        return space_state

class RunningAgentsNum(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        return f'Running agents: {model.moving_agents_num}'

def agent_portayal(a):
    cl = '#00FF00' if a.is_moving else '#0000FF'
    return {'Shape': 'circle', 'r': 4, 'Filled': 'true', 'Color': cl}

bg_path = 'map_2floor_bw.png'
with open(bg_path, "rb") as img_file:
    b64_string = base64.b64encode(img_file.read())

running_counter_element = RunningAgentsNum()
canvas_element = IndoorVisualCanvas(agent_portayal, 250, 600, 'data:image/png;base64, ' + b64_string.decode('utf-8'))

model_params = {
    # 'N': UserSettableParameter('slider', 'N', 5, 1, 20),
    'agents_json_path': 'agents.json',
    'env_map_path': bg_path
}

server = ModularServer(IndoorModel, [canvas_element, running_counter_element], 'Indoor model', model_params)
