# About:
# This is a simple maze based game where the player has to beat/race a CPU agent to the white exit circle and get through all 25 levels to win! 
# The player's icon is green while the agent's icon is red, the exit icon is white. The game is over if the agent beats you to the exit and you win if you get through all levels without losing the race.
# Each maze level is procedurally generated in real time using a back tracking algorithm, and the mazes size is increased by 1 for each continuing level. The agent uses a breadth first search to compute the path to the exit.
# The agent than plays back each step with a small delay (200-300ms) per cell in order to follow the maze to the exit cell.

# Controls:
# W or up arrow - move up
# A or left arrow - move left
# S or down arrow - move down
# D or right arrow - move right

# space - skip current level
# return - restart game (only works when in end screen)

import pygame
import random
import os
import sys
from queue import Queue

os.chdir(os.path.dirname(__file__)) 

WINDOW_SIZE = 600
LEVELS_TO_WIN = 25 # If you want to make the game easier you can set the max level to a lower number :D
OFFSET = 40
FPS = 60

# --Game color values-- 
# Marker colors (in RGB)
PLAYER_COLOR = (42, 130, 48) # Green color
AGENT_COLOR = (255, 0, 0) # Red color
EXIT_CELL_COLOR = (255, 255, 255) # White color
# Screen background color (in RGB)
SCREEN_BACKGROUND_COLOR = (0, 0, 0) # Black color
# Cell wall color (in RGB)
CELL_WALLS_COLOR = (255, 255, 255) # White color
# Text color (in RGB)
TEXT_COLOR = (255, 255, 255) # White color

# Movement direction codes
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
WAITING = -1

# Represents a single cell within the world grid 
class Cell:
    def __init__(self, row, col, size, offset):
        self.row = row
        self.col = col
        self.x_pos = col * size + offset[0]
        self.y_pos = row * size + offset[1]

        self.visited = False  # Used for procedural maze creation, implemented using backtracking

        # What walls should be rendered within the cell's square
        self.north = True
        self.south = True
        self.east = True
        self.west = True

class MazeGame:
    def __init__(self):
        pygame.init()
        pygame.font.init() 

        self.custom_font = pygame.font.Font(r"font//8bitOperatorPlus.ttf", 25)
        self.custom_font2 = pygame.font.Font(r"font//8bitOperatorPlus.ttf", 20)
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Maze Game")

        self.clock = pygame.time.Clock()

        # Game state variables
        self.cols = 3
        self.rows = 3
        self.n_cells = self.cols * self.rows
        self.delay = 300  # Agent move delay in ms, this is randomized between 200-300ms for each playback step 
        self.level = 0
        self.elapsed_time = 0
        self.start_time = pygame.time.get_ticks()
        self.delay_time = self.start_time
        self.quit = False
        self.game_over = False

        # Player and agent positions
        self.current_cell = 0
        self.agent_cell = 0
        self.exit_cell = 0
        self.player_next_move = WAITING
        self.agent_path  = []

        # Maze structure
        self.maze_cells = []
        self.offset = (0, 0)
        self.cell_size = 50
        self.load_level()

    # Dynamically calculate cell size to fit the maze within window 
    def calculate_cell_size_and_offsets(self):
        self.cell_size = min((WINDOW_SIZE - OFFSET * 2) // self.cols, (WINDOW_SIZE - OFFSET * 2) // self.rows)

        # Update offsets to center the maze
        maze_width = self.cols * self.cell_size
        maze_height = self.rows * self.cell_size
        self.offset = ((WINDOW_SIZE - maze_width) // 2, (WINDOW_SIZE - maze_height) // 2)

    def generate_maze(self):
        self.calculate_cell_size_and_offsets()
        self.maze_cells = []
        for row in range(self.rows):
            for col in range(self.cols):
                self.maze_cells.append(Cell(row, col, self.cell_size, self.offset))

        self.back_tracker() # Apply backtracking algorithm to generate the maze

    # Maze generation using backtracking algorithm
    def back_tracker(self):
        stack = []
        current_cell = 0
        self.maze_cells[current_cell].visited = True
        visited_cells = 1

        while visited_cells < self.n_cells:
            neighbors = self.get_unvisited_neighbors(current_cell)
            if neighbors:
                next_cell, direction = random.choice(neighbors)
                self.remove_adj_walls(current_cell, next_cell, direction)
                stack.append(current_cell)
                current_cell = next_cell
                self.maze_cells[current_cell].visited = True # Mark cell as visited, needed to ensure proper maze loop
                visited_cells += 1
            elif stack:
                current_cell = stack.pop()

    # Finds unvisited neighbors of a given cell
    def get_unvisited_neighbors(self, cell):
        neighbors = []
        row, col = divmod(cell, self.cols)

        if row > 0 and not self.maze_cells[cell - self.cols].visited:
            neighbors.append((cell - self.cols, UP))
        if row < self.rows - 1 and not self.maze_cells[cell + self.cols].visited:
            neighbors.append((cell + self.cols, DOWN))
        if col > 0 and not self.maze_cells[cell - 1].visited:
            neighbors.append((cell - 1, LEFT))
        if col < self.cols - 1 and not self.maze_cells[cell + 1].visited:
            neighbors.append((cell + 1, RIGHT))

        return neighbors

    # Remove walls between two adjacent cells
    def remove_adj_walls(self, cell, neighbor, direction):
        if direction == UP:
            self.maze_cells[cell].north = False
            self.maze_cells[neighbor].south = False
        elif direction == DOWN:
            self.maze_cells[cell].south = False
            self.maze_cells[neighbor].north = False
        elif direction == LEFT:
            self.maze_cells[cell].west = False
            self.maze_cells[neighbor].east = False
        elif direction == RIGHT:
            self.maze_cells[cell].east = False
            self.maze_cells[neighbor].west = False

    def load_level(self):
        self.level += 1
        self.cols += 1
        self.rows += 1
        self.n_cells = self.cols * self.rows
        self.generate_maze() # Begin procedurally generating a new maze for the current level
        print(f"Generating level: {self.level}")

        self.current_cell = 0
        self.exit_cell = random.choice(range(self.n_cells))
        self.agent_cell = 0
        self.agent_path = self.compute_path(self.agent_cell, self.exit_cell)

        self.start_time = pygame.time.get_ticks()
        self.delay_time = self.start_time

    # Use breadth first search to compute the shortest path between two cells
    def compute_path(self, start_cell, target_cell):
        queue = Queue()
        queue.put(start_cell)
        visited = [False] * self.n_cells
        visited[start_cell] = True
        parent = [-1] * self.n_cells

        while not queue.empty():
            current = queue.get()
            if current == target_cell:
                path = []
                while current != -1:
                    path.insert(0, current)
                    current = parent[current]
                return path # Returns a list of steps needed to reach the exit cell, starting at cell 0

            for neighbor, direction in self.get_neighbors(current):
                if not visited[neighbor]:
                    queue.put(neighbor)
                    visited[neighbor] = True
                    parent[neighbor] = current
    
    # Returns accessible neighbors of a cell
    def get_neighbors(self, cell):
        neighbors = []
        row, col = divmod(cell, self.cols)
        walls = self.maze_cells[cell]

        if not walls.north and row > 0:
            neighbors.append((cell - self.cols, UP))
        if not walls.south and row < self.rows - 1:
            neighbors.append((cell + self.cols, DOWN))
        if not walls.west and col > 0:
            neighbors.append((cell - 1, LEFT))
        if not walls.east and col < self.cols - 1:
            neighbors.append((cell + 1, RIGHT))

        return neighbors

    # Handle player movement based on the current movement code's direction
    def handle_player_movement(self):
        if self.player_next_move == UP and not self.maze_cells[self.current_cell].north:
            self.current_cell -= self.cols
        elif self.player_next_move == DOWN and not self.maze_cells[self.current_cell].south:
            self.current_cell += self.cols
        elif self.player_next_move == LEFT and not self.maze_cells[self.current_cell].west:
            self.current_cell -= 1
        elif self.player_next_move == RIGHT and not self.maze_cells[self.current_cell].east:
            self.current_cell += 1

        self.player_next_move = WAITING # Reset movement code, this prevents continuous movement when not holding down a key 

    def handle_agent_movement(self):
        self.delay = random.randrange(200, 300) # Randomize the agent movement playback between 200-300ms

        if pygame.time.get_ticks() - self.delay_time >= self.delay and self.agent_path:
            self.agent_cell = self.agent_path.pop(0)
            self.delay_time = pygame.time.get_ticks()

    def draw_maze(self):
        self.screen.fill(SCREEN_BACKGROUND_COLOR)
        for cell in self.maze_cells:
            x, y = cell.x_pos, cell.y_pos
            if cell.north:
                pygame.draw.line(self.screen, CELL_WALLS_COLOR, (x, y), (x + self.cell_size, y), 2)
            if cell.south:
                pygame.draw.line(self.screen, CELL_WALLS_COLOR, (x, y + self.cell_size), (x + self.cell_size, y + self.cell_size), 2)
            if cell.west:
                pygame.draw.line(self.screen, CELL_WALLS_COLOR, (x, y), (x, y + self.cell_size), 2)
            if cell.east:
                pygame.draw.line(self.screen, CELL_WALLS_COLOR, (x + self.cell_size, y), (x + self.cell_size, y + self.cell_size), 2)

        self.draw_marker(self.current_cell, PLAYER_COLOR)
        self.draw_marker(self.agent_cell, AGENT_COLOR)
        self.draw_marker(self.exit_cell, EXIT_CELL_COLOR) 

    def draw_marker(self, cell, color):
        x, y = self.maze_cells[cell].x_pos, self.maze_cells[cell].y_pos
        pygame.draw.circle(self.screen, color, (x + self.cell_size // 2, y + self.cell_size // 2), self.cell_size // 4) # Draw in the middle of the given cell

    # Draw the end screen, handle game reset
    def handle_game_over(self, display_text):
        self.game_over = True
        self.screen.fill(SCREEN_BACKGROUND_COLOR)

        text_surface = self.custom_font.render(display_text, True, TEXT_COLOR)
        sub_text_surface = self.custom_font2.render("[Press 'ENTER' to restart]", True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
        text_rect2 = sub_text_surface.get_rect(center=(WINDOW_SIZE // 2, (WINDOW_SIZE // 2) + 45))

        self.screen.blit(text_surface, text_rect)
        self.screen.blit(sub_text_surface, text_rect2)
        pygame.display.flip()

        while self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.reset_game()
                    self.game_over = False
     
    # Reset the game state to level 1
    def reset_game(self):
        self.cols = 3
        self.rows = 3
        self.level = 0
        self.n_cells = self.cols * self.rows
        self.current_cell = 0
        self.agent_cell = 0
        self.exit_cell = 0
        self.player_next_move = WAITING
        self.agent_path = []
        self.load_level()

    def game_loop(self):
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_w, pygame.K_UP):
                        self.player_next_move = UP
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        self.player_next_move = DOWN
                    elif event.key in (pygame.K_a, pygame.K_LEFT):
                        self.player_next_move = LEFT
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        self.player_next_move = RIGHT
                    elif event.key == pygame.K_SPACE:  # Allow player to Skip the current level using 'space', mostly left this here for quick testing
                        self.current_cell = self.exit_cell
                    elif event.key == pygame.K_ESCAPE:
                        self.quit = True

            if self.current_cell == self.exit_cell:
                if self.level < LEVELS_TO_WIN:
                    self.load_level()
                else:
                    self.handle_game_over("YOU WIN!")

            elif self.agent_cell == self.exit_cell:
                self.handle_game_over("GAME OVER!")

            self.handle_player_movement()
            self.handle_agent_movement()
            self.draw_maze()
            pygame.display.flip()
            self.clock.tick(FPS)

MazeGame().game_loop()
