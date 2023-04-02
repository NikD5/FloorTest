def main(self):
    grid = AStar.create_grid(self.cols, self.rows)
    grid = AStar.fill_grids(grid, self.cols, self.rows, obstacle_ratio=self.obstacle_ratio,
                            obstacle_list=self.obstacle_list)
    grid = AStar.get_neighbors(grid, self.cols, self.rows)
    open_set = []
    closed_set = []
    current_node = None
    final_path = []
    open_set.append(grid[self.start[0]][self.start[1]])
    self.end = grid[self.end[0]][self.end[1]]
    while len(open_set) > 0:
        open_set, closed_set, current_node, final_path = AStar.start_path(open_set, closed_set, current_node, self.end)
        if len(final_path) > 0:
            break
    return final_path

