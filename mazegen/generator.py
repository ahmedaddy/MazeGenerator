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
        """Get neighbors of cell at (x, y)."""
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
                 loop_factor: float = 0.1, seed: Optional[int] = None):
        """
        Args:
            width: Number of cells horizontally
            height: Number of cells vertically
            perfect: If True, maze has exactly one path between any two cells.
                If False, extra walls are removed to create multiple routes.
            loop_factor: Fraction of internal walls to remove (0.0 to 1.0).
                         Only used when perfect=False.
                         0.05 = subtle alternatives, 0.3 = very open maze.
            seed: Random seed for reproducibility
        """
        self.width = width
        self.height = height
        self.perfect = perfect
        self.loop_factor = max(0.0, min(1.0, loop_factor))
        self.rng = random.Random(seed)

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
        self.add_42_pattern(maze)
        self.recursive_backtracker(maze, ex, ey)
        if not self.perfect:
            self.add_loops(maze)
        self.add_border_walls(maze)
        return maze

    OPPOSITE = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
    DIRECTION_OFFSETS = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}

    def recursive_backtracker(self,
                              maze: Maze,
                              start_x: int,
                              start_y: int) -> None:
        stack = [(start_x, start_y)]
        current_cell = maze.get_cell(start_x, start_y)
        if current_cell:
            current_cell.visited = True
        while stack:
            x, y = stack[-1]
            neighbors = maze.get_neighbors(x, y)
            unvisiteed_neighbors = [
                (nx, ny, dir_from) for (nx, ny, dir_from) in neighbors
                if not maze.get_cell(nx, ny).visited
            ]
            if unvisiteed_neighbors:
                nx, ny, dir = self.rng.choice(unvisiteed_neighbors)
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

    def add_loops(self, maze: Maze) -> None:
        """
        Remove random internal walls to create loops (multiple routes).

        Collects all internal walls that still exist after the base maze
        generation, then randomly removes a fraction of them determined
        by self.loop_factor. Each removal creates one extra loop/cycle,
        giving the solver alternative paths.
        """
        pattern_walls = set()
        for y in range(maze.height):
            for x in range(maze.width):
                cell = maze.get_cell(x, y)
                if (cell and cell.visited and
                        all(cell.has_wall(d) for d in ['N', 'E', 'S', 'W'])):
                    pattern_walls.add((x, y))
        internal_walls = []
        for y in range(maze.height):
            for x in range(maze.width):
                cell = maze.get_cell(x, y)
                if not cell:
                    continue
                # Only check E and S to avoid counting each wall twice
                if x + 1 < maze.width and cell.has_wall('E'):
                    if ((x, y) not in pattern_walls and
                            (x + 1, y) not in pattern_walls):
                        internal_walls.append((x, y, 'E'))
                if y + 1 < maze.height and cell.has_wall('S'):
                    if ((x, y) not in pattern_walls and
                            (x, y + 1) not in pattern_walls):
                        internal_walls.append((x, y, 'S'))

        num_to_remove = int(len(internal_walls) * self.loop_factor)
        walls_to_remove = self.rng.sample(internal_walls,
                                          min(num_to_remove,
                                              len(internal_walls)))

        for x, y, direction in walls_to_remove:
            cell = maze.get_cell(x, y)
            dx, dy = self.DIRECTION_OFFSETS[direction]
            neighbor = maze.get_cell(x + dx, y + dy)
            if cell and neighbor:
                cell.remove_wall(direction)
                neighbor.remove_wall(self.OPPOSITE[direction])

    def add_42_pattern(self, maze: Maze) -> None:
        """Embed a '42' pattern using fully closed cells."""
        pattern_4 = [
            [1, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 0, 1],
            [0, 0, 1],
        ]
        pattern_2 = [
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1],
            [1, 0, 0],
            [1, 1, 1],
        ]
        pattern_w = len(pattern_4[0]) + 1 + len(pattern_2[0])  # 3+1+3 = 7
        pattern_h = len(pattern_4)  # 5
        if self.width < pattern_w + 2 or self.height < pattern_h + 2:
            print("Maze too small for 42 pattern.")
            return
        offset_x = (self.width - pattern_w) // 2
        offset_y = (self.height - pattern_h) // 2
        entry_x, entry_y = maze.entry
        exit_x, exit_y = maze.exit
        for py, row in enumerate(pattern_4):
            for px, val in enumerate(row):
                if val == 1:
                    cx, cy = offset_x + px, offset_y + py
                    if (cx, cy) == (entry_x, entry_y):
                        continue
                    if (cx, cy) == (exit_x, exit_y):
                        continue
                    self.close_cell(maze, cx, cy)
        for py, row in enumerate(pattern_2):
            for px, val in enumerate(row):
                if val == 1:
                    cx = offset_x + len(pattern_4[0]) + 1 + px
                    cy = offset_y + py
                    if (cx, cy) == (entry_x, entry_y):
                        continue
                    if (cx, cy) == (exit_x, exit_y):
                        continue
                    self.close_cell(maze, cx, cy)

    def close_cell(self, maze: Maze, x: int, y: int) -> None:
        """Close all 4 walls of a cell and update neighbor walls."""
        cell = maze.get_cell(x, y)
        if not cell:
            return
        cell.visited = True

    def add_border_walls(self, maze: Maze) -> None:
        """Ensure all outer edges of the maze have walls."""
        for x in range(maze.width):
            maze.get_cell(x, 0).add_wall('N')
            maze.get_cell(x, maze.height - 1).add_wall('S')
        for y in range(maze.height):
            maze.get_cell(0, y).add_wall('W')
            maze.get_cell(maze.width - 1, y).add_wall('E')

    def save_to_file(self, maze: Maze, filename: str) -> None:
        """
        Save maze to file in hexadecimal format.

        Args:
            maze: Maze to save
            filename: Output filename

        File format:
            - One hex digit per cell (walls encoding)
            - One row per line
            - Empty line
            - Entry coordinates
            - Exit coordinates
            - Solution path (N, E, S, W moves)

            N = 2³ = 8
            E = 2² = 4
            S = 2¹ = 2
            W = 2⁰ = 1
        """
        with open(filename, 'w') as f:
            for y in range(maze.height):
                row = ''
                for x in range(maze.width):
                    cell = maze.get_cell(x, y)
                    if cell:
                        row += f'{(cell.walls["N"] * 8 +
                                   cell.walls["E"] * 4 +
                                   cell.walls["S"] * 2 +
                                   cell.walls["W"] * 1):X}'
                f.write(row + '\n')
            f.write('\n')
            f.write(f'{maze.entry[0]} {maze.entry[1]}\n')
            f.write(f'{maze.exit[0]} {maze.exit[1]}\n')
            f.write(''.join(maze.solution) + '\n')


def test_maze_generation():
    # Non-perfect maze: loop_factor=0.1 means ~10% of internal walls removed
    generator = MazeGenerator(width=20, height=20, perfect=False,
                              loop_factor=0.1, seed=None)
    maze = generator.generate(entry=(0, 1), exit=(9, 11))
    generator.save_to_file(maze, "maze.txt")

    maze_str = ""
    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze.get_cell(x, y)
            maze_str += "+" + ("---" if cell.has_wall('N') else "   ")
        maze_str += "+\n"
        for x in range(maze.width):
            cell = maze.get_cell(x, y)
            maze_str += ("|" if cell.has_wall('W') else " ") + "   "
        maze_str += ("|\n" if maze.get_cell(maze.width - 1, y).has_wall('E') else " \n")
    for x in range(maze.width):
        cell = maze.get_cell(x, maze.height - 1)
        maze_str += "+" + ("---" if cell.has_wall('S') else "   ")
    maze_str += "+\n"
    print(maze_str)


if __name__ == "__main__":
    test_maze_generation()
