import pygame
import numpy as np
from src.models.grid import Grid
from src.models.traffic_light import Direction

class Visualizer:
    def __init__(self, grid: Grid, rows: int, cols: int, p1: float):
        """Initialize visualizer with a grid.
        
        Args:
            grid: The traffic grid to visualize
            rows: Number of rows in the grid
            cols: Number of columns in the grid
            p1: Probability of vehicle generation
        """
        pygame.init()
        
        # Window settings
        self.WINDOW_WIDTH = 1200
        self.WINDOW_HEIGHT = 800
        self.GRID_SECTION_WIDTH = self.WINDOW_WIDTH // 2
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BACKGROUND = (240, 240, 240)
        
        # Create window
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Traffic Simulation")
        
        # Grid settings
        self.grid = grid
        self.rows = rows
        self.cols = cols
        self.p1 = p1
        self.cell_width = min(
            (self.GRID_SECTION_WIDTH - 100) // self.grid.cols,
            (self.WINDOW_HEIGHT - 100) // self.grid.rows
        )
        self.grid_offset_x = 50
        self.grid_offset_y = 50
        
        # Font
        self.font = pygame.font.Font(None, 36)
        
        # Stats
        self.stats_section_x = self.GRID_SECTION_WIDTH + 50
        
    def _draw_grid_section(self):
        """Draw the grid section with traffic density."""
        # Draw section divider
        pygame.draw.line(
            self.screen,
            self.GRAY,
            (self.GRID_SECTION_WIDTH, 0),
            (self.GRID_SECTION_WIDTH, self.WINDOW_HEIGHT),
            2
        )
        
        # Get traffic density
        density = self.grid.get_traffic_density()
        max_density = max(1, np.max(density))  # Avoid division by zero
        
        # Draw grid cells
        for i in range(self.grid.rows):
            for j in range(self.grid.cols):
                x = self.grid_offset_x + j * self.cell_width
                y = self.grid_offset_y + i * self.cell_width
                
                # Calculate cell color based on density
                density_value = density[i, j]
                color_value = int(255 * (1 - density_value / max_density))
                cell_color = (255, color_value, color_value)  # Red gradient
                
                # Draw cell
                pygame.draw.rect(
                    self.screen,
                    cell_color,
                    (x, y, self.cell_width, self.cell_width)
                )
                pygame.draw.rect(
                    self.screen,
                    self.GRAY,
                    (x, y, self.cell_width, self.cell_width),
                    1
                )
                
                # Draw traffic light
                light = self.grid.get_traffic_light((i, j))
                horizontal_color = self.GREEN if light.is_green(Direction.HORIZONTAL) else self.RED
                vertical_color = self.GREEN if light.is_green(Direction.VERTICAL) else self.RED
                
                # Draw horizontal light indicator
                pygame.draw.circle(
                    self.screen,
                    horizontal_color,
                    (x + self.cell_width - 10, y + self.cell_width // 2),
                    4
                )
                # Draw vertical light indicator
                pygame.draw.circle(
                    self.screen,
                    vertical_color,
                    (x + self.cell_width // 2, y + self.cell_width - 10),
                    4
                )
                
                # Draw density number
                if density_value > 0:
                    text = self.font.render(str(int(density_value)), True, self.BLACK)
                    text_rect = text.get_rect(center=(x + self.cell_width//2, y + self.cell_width//2))
                    self.screen.blit(text, text_rect)
    
    def _draw_stats_section(self, time_step: int, avg_speed: float):
        """Draw the statistics section."""
        y_offset = 50
        line_height = 40
        
        # Draw simulation settings
        text = self.font.render("Simulation Settings:", True, self.BLACK)
        self.screen.blit(text, (self.stats_section_x, y_offset))
        y_offset += line_height
        
        text = self.font.render(f"Grid Size: {self.rows}x{self.cols}", True, self.BLACK)
        self.screen.blit(text, (self.stats_section_x, y_offset))
        y_offset += line_height
        
        text = self.font.render(f"Vehicle Generation Rate: {self.p1:.2f}", True, self.BLACK)
        self.screen.blit(text, (self.stats_section_x, y_offset))
        y_offset += line_height * 1.5
        
        # Draw current statistics
        text = self.font.render("Current Statistics:", True, self.BLACK)
        self.screen.blit(text, (self.stats_section_x, y_offset))
        y_offset += line_height
        
        text = self.font.render(f"Time Step: {time_step}", True, self.BLACK)
        self.screen.blit(text, (self.stats_section_x, y_offset))
        y_offset += line_height
        
        # Calculate total vehicles across all direction queues
        total_vehicles = sum(
            len(direction_queue)
            for queues in self.grid.intersection_queues.values()
            for direction_queue in queues.values()
        )
        text = self.font.render(f"Total Vehicles: {total_vehicles}", True, self.BLACK)
        self.screen.blit(text, (self.stats_section_x, y_offset))
        y_offset += line_height
        
        text = self.font.render(f"Average Speed: {avg_speed:.2f}", True, self.BLACK)
        self.screen.blit(text, (self.stats_section_x, y_offset))
        y_offset += line_height * 1.5
        
        # Draw traffic light legend
        text = self.font.render("Traffic Lights:", True, self.BLACK)
        self.screen.blit(text, (self.stats_section_x, y_offset))
        y_offset += line_height
        
        # Horizontal light legend
        pygame.draw.circle(self.screen, self.GREEN, (self.stats_section_x + 20, y_offset + 5), 4)
        text = self.font.render("Horizontal Green", True, self.BLACK)
        self.screen.blit(text, (self.stats_section_x + 40, y_offset))
        y_offset += line_height
        
        # Vertical light legend
        pygame.draw.circle(self.screen, self.GREEN, (self.stats_section_x + 20, y_offset + 5), 4)
        text = self.font.render("Vertical Green", True, self.BLACK)
        self.screen.blit(text, (self.stats_section_x + 40, y_offset))
    
    def update(self, time_step: int, avg_speed: float):
        """Update the visualization."""
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit()
        
        # Clear screen
        self.screen.fill(self.BACKGROUND)
        
        # Draw sections
        self._draw_grid_section()
        self._draw_stats_section(time_step, avg_speed)
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        pygame.time.Clock().tick(10)  # 10 FPS
