import random
from typing import List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class Cell:
    x: int
    y: int
    walls: dict = field(default_factory=lambda: {
        'N': True,
        'E': True,
        'S': True,
        'W': True
    })
    visited: bool = False

    def has_wall(self, direction: str) -> bool:
        return self.walls[direction]

    def remove_wall(self, direction: str) -> None:
        self.walls[direction] = False

    def add_wall(self, direction: str) -> None:
        self.walls[direction] = True


class Maze:
    def __init__(
                    self, width: int, height: int,
                    entry: Tuple[int, int], exit: Tuple[int, int]):
        """
        Initialize maze.

        Args:
            width: Number of cells horizontally
            height: Number of cells vertically
            entry: Entry position (x, y)
            exit: Exit position (x, y)
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.cells: List[List[Cell]] = [
            [Cell(x, y) for x in range(width)]
            for y in range(height)
        ]
        self.solution: List[str] = []

    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        """Get cell at position (x, y)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        return None

    def get_neighbors(self, x: int, y: int) -> List[Tuple[str, Cell]]:
        """Get unvisited neighbors of cell at (x, y)."""
        directions = {
            'N': (0, -1),
            'E': (1, 0),
            'S': (0, 1),
            'W': (-1, 0)
        }
        neighbors = []
        for dir_from, (dx, dy) in directions.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append((nx, ny, dir_from))
        return neighbors


class MazeGenerator:
    def __init__(self, width: int, height: int, perfect: bool = True,
                 seed: Optional[int] = None):
        self.width = width
        self.height = height
        self.perfect = perfect
        if seed is not None:
            random.seed(seed)

    def generate(self, entry: Tuple[int, int], exit: Tuple[int, int]) -> Maze:
        """Generate maze using recursive backtracking."""
        ex, ey = entry
        xx, xy = exit

        if not (0 <= ex < self.width and 0 <= ey < self.height):
            raise ValueError(f"Entry point out of bounds: {entry}")
        if not (0 <= xx < self.width and 0 <= xy < self.height):
            raise ValueError(f"Exit point out of bounds: {exit}")
        if entry == exit:
            raise ValueError("Entry and exit points cannot be the same.")
        maze = Maze(self.width, self.height, entry, exit)
        self. recursive_backtracker(maze, ex, ey)
        self.add_42_pattern(maze)
        return maze

    def recursive_backtracker(self,
                              maze: Maze,
                              start_x: int,
                              start_y: int) -> None:
        stack = [(start_x, start_y)]
        current_cell = maze.get_cell(start_x, start_y)
        if current_cell:
            current_cell.visited = True
        print(stack[-1])
        while stack:
            x, y = stack[-1]
            neighbors = maze.get_neighbors(x, y)
            unvisiteed_neighbors = [
                (nx, ny, dir_from) for (nx, ny, dir_from) in neighbors
                if not maze.get_cell(nx, ny).visited
            ]
            if unvisiteed_neighbors:
                nx, ny, dir = random.choice(unvisiteed_neighbors)
                current = maze.get_cell(x, y)
                neighbor = maze.get_cell(nx, ny)
                if current and neighbor:
                    current.remove_wall(dir)
                    opposite = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
                    neighbor.remove_wall(opposite[dir])
                    neighbor.visited = True
                    stack.append((nx, ny))
            else:
                stack.pop()

    def add_42_pattern(self, maze: Maze) -> None:
        if self.width < 10 or self.height < 10:
            print("Maze too small for 42 pattern.")
            return
        pattern = [
                [0, 1, 1, 1, 0],
                [0, 0, 0, 1, 0],
                [0, 1, 1, 1, 0],
                [0, 1, 0, 0, 0],
                [0, 1, 0, 0, 0],
                [0, 1, 1, 1, 1],
                [0, 0, 0, 0, 1],
        ]
        offset_x = self.width - 5
        offset_y = self.height - 7
        for py, row in enumerate(pattern):
            for px, val in enumerate(row):
                if val == 1:
                    cell = maze.get_cell(offset_x + px, offset_y + py)
                    if cell:
                        cell.walls = {
                                        'N': False,
                                        'E': False,
                                        'S': False,
                                        'W': False}


def test_maze_generation():
    generator = MazeGenerator(width=14, height=16, perfect=True, seed=42)
    maze = generator.generate(entry=(0, 0), exit=(2, 8))

    # print(maze.cells)
    # assert maze.get_cell(0, 0).visited
    # assert maze.get_cell(9, 9).visited
    print("Maze generation test passed.")
    # draw maze in terminal

    maze_str = ""
    for y in range(maze.height):
        # Top walls
        for x in range(maze.width):
            cell = maze.get_cell(x, y)
            maze_str += "+" + ("---" if cell.has_wall('N') else "   ")
        maze_str += "+\n"
        # Side walls and spaces
        for x in range(maze.width):
            cell = maze.get_cell(x, y)
            maze_str += ("|" if cell.has_wall('W') else " ") + "   "
        maze_str += ("|\n" if maze.get_cell(maze.width - 1, y).has_wall('E') else " \n")
    # Bottom walls
    for x in range(maze.width):
        cell = maze.get_cell(x, maze.height - 1)
        maze_str += "+" + ("---" if cell.has_wall('S') else "   ")
    maze_str += "+\n"
    print(maze_str)


if __name__ == "__main__":
    test_maze_generation()
