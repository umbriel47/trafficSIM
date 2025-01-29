import pygame
import sys
from src.models.vehicle import Vehicle
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = (600, 600)
GRID_SIZE = (10, 10)
CELL_SIZE = WINDOW_SIZE[0] // GRID_SIZE[0]

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Create window
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Vehicle Path Visualization")

def draw_grid():
    """Draw the grid lines"""
    for i in range(GRID_SIZE[0] + 1):
        pygame.draw.line(screen, BLACK, 
                        (0, i * CELL_SIZE), 
                        (WINDOW_SIZE[0], i * CELL_SIZE))
        pygame.draw.line(screen, BLACK, 
                        (i * CELL_SIZE, 0), 
                        (i * CELL_SIZE, WINDOW_SIZE[1]))

def draw_cell_coordinates():
    """Draw coordinates in each cell"""
    font = pygame.font.Font(None, 24)
    for i in range(GRID_SIZE[0]):
        for j in range(GRID_SIZE[1]):
            text = font.render(f"({i},{j})", True, GRAY)
            text_rect = text.get_rect(center=(j * CELL_SIZE + CELL_SIZE//2,
                                            i * CELL_SIZE + CELL_SIZE//2))
            screen.blit(text, text_rect)

def draw_path(path):
    """Draw the vehicle's path"""
    # Draw path lines
    for i in range(len(path) - 1):
        start_pos = (path[i][1] * CELL_SIZE + CELL_SIZE//2,
                    path[i][0] * CELL_SIZE + CELL_SIZE//2)
        end_pos = (path[i+1][1] * CELL_SIZE + CELL_SIZE//2,
                  path[i+1][0] * CELL_SIZE + CELL_SIZE//2)
        
        # Handle periodic boundary visualization
        dx = path[i+1][1] - path[i][1]
        dy = path[i+1][0] - path[i][0]
        
        # If the difference is more than half the grid size, it's a boundary crossing
        if abs(dx) > GRID_SIZE[1]//2:
            # Draw line to edge
            if dx > 0:  # Crossing left boundary
                pygame.draw.line(screen, BLUE, start_pos, 
                               (0, start_pos[1]))
                pygame.draw.line(screen, BLUE, 
                               (WINDOW_SIZE[0], end_pos[1]), end_pos)
            else:  # Crossing right boundary
                pygame.draw.line(screen, BLUE, start_pos, 
                               (WINDOW_SIZE[0], start_pos[1]))
                pygame.draw.line(screen, BLUE, 
                               (0, end_pos[1]), end_pos)
        elif abs(dy) > GRID_SIZE[0]//2:
            # Draw line to edge
            if dy > 0:  # Crossing top boundary
                pygame.draw.line(screen, BLUE, start_pos, 
                               (start_pos[0], 0))
                pygame.draw.line(screen, BLUE, 
                               (end_pos[0], WINDOW_SIZE[1]), end_pos)
            else:  # Crossing bottom boundary
                pygame.draw.line(screen, BLUE, start_pos, 
                               (start_pos[0], WINDOW_SIZE[1]))
                pygame.draw.line(screen, BLUE, 
                               (end_pos[0], 0), end_pos)
        else:
            # Normal line
            pygame.draw.line(screen, BLUE, start_pos, end_pos)
    
    # Draw points for each step
    for i, pos in enumerate(path):
        color = RED if i == 0 else GREEN if i == len(path)-1 else BLUE
        pygame.draw.circle(screen, color,
                         (pos[1] * CELL_SIZE + CELL_SIZE//2,
                          pos[0] * CELL_SIZE + CELL_SIZE//2), 8)
        
        # Draw step numbers
        font = pygame.font.Font(None, 24)
        text = font.render(str(i), True, BLACK)
        text_rect = text.get_rect(center=(pos[1] * CELL_SIZE + CELL_SIZE//2,
                                        pos[0] * CELL_SIZE + CELL_SIZE//2))
        screen.blit(text, text_rect)

def main():
    # Create vehicle and get path
    start = (3, 3)
    end = (9, 9)
    vehicle = Vehicle(start, end, GRID_SIZE)
    path = vehicle.path
    
    # Print path information
    print(f"Path from {start} to {end}:")
    for i, pos in enumerate(path):
        print(f"Step {i}: {pos}")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Draw
        screen.fill(WHITE)
        draw_grid()
        draw_cell_coordinates()
        draw_path(path)
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
