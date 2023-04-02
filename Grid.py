from mesa.space import _Grid

class trial_grid(_Grid):
	"""
	Added a method to the Mesa Grid class
	"""
	def __init__(self, width, height, torus):
		super().__init__(width, height, torus)


	def get_free_cells(self, pos, moore=False):
		'''
		returns list of free cells in adjacent tiles
		'''
		neighborhood = self.get_neighborhood(pos, moore)
		return[cell for cell in neighborhood if self.is_cell_empty(cell)]
