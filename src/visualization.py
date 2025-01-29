import pygame
import numpy as np
from typing import Tuple
from .simulation import Simulation

class Visualizer:
    def __init__(self, simulation: Simulation, window_size: Tuple[int, int] = (1200, 600)):
        """Initialize the visualization.
        
        Args:
            simulation: The traffic simulation instance
            window_size: Size of the visualization window
        """
        pygame.init()
        self.simulation = simulation
        self.window_size = window_size
        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Traffic Simulation")
        
        # Split window into two parts
        self.grid_surface = pygame.Surface((window_size[0]//2, window_size[1]))
        self.path_surface = pygame.Surface((window_size[0]//2, window_size[1]))
        
        # Calculate grid cell size for both surfaces
        self.cell_width = (window_size[0]//2) // simulation.grid_size[1]
        self.cell_height = window_size[1] // simulation.grid_size[0]
        
        # Colors
        self.COLORS = {
            'background': (200, 200, 200),  # Light gray
            'road': (100, 100, 100),        # Dark gray
            'vehicle': (0, 0, 255),         # Blue
            'traffic_light_red': (255, 0, 0),
            'traffic_light_green': (0, 255, 0),
            'grid_line': (50, 50, 50),      # Darker gray
            'path': (255, 165, 0),          # Orange
            'vehicle_trail': (0, 191, 255),  # Deep sky blue
            'path_highlight': (255, 69, 0)   # Red-Orange for highlighting
        }
        
        # Store vehicle trail
        self.vehicle_positions = []
        # Animation control
        self.path_animation_index = 0
        self.animation_speed = 5  # Number of frames to wait before showing next segment
        self.animation_counter = 0
    
    def draw(self):
        """Draw the current state of the simulation."""
        self.screen.fill(self.COLORS['background'])
        
        # Draw grid surface (left side)
        self._draw_grid_view()
        
        # Draw path surface (right side)
        self._draw_path_view()
        
        # Blit both surfaces to the main screen
        self.screen.blit(self.grid_surface, (0, 0))
        self.screen.blit(self.path_surface, (self.window_size[0]//2, 0))
        
        # Update display
        pygame.display.flip()
    
    def _draw_grid_view(self):
        """Draw the grid view on the left surface."""
        self.grid_surface.fill(self.COLORS['background'])
        
        # Draw roads
        self._draw_roads()
        
        # Draw traffic lights
        self._draw_traffic_lights()
        
        # Draw vehicle and its trail
        self._draw_vehicle_and_trail()
        
        # Draw grid lines
        self._draw_grid_lines()
    
    def _draw_roads(self):
        """Draw the road network."""
        # Draw horizontal roads
        for i in range(self.simulation.grid_size[0]):
            y = i * self.cell_height
            pygame.draw.rect(self.grid_surface, self.COLORS['road'],
                           (0, y - self.cell_height//4,
                            self.window_size[0]//2, self.cell_height//2))
        
        # Draw vertical roads
        for j in range(self.simulation.grid_size[1]):
            x = j * self.cell_width
            pygame.draw.rect(self.grid_surface, self.COLORS['road'],
                           (x - self.cell_width//4, 0,
                            self.cell_width//2, self.window_size[1]))
    
    def _draw_traffic_lights(self):
        """Draw traffic lights as rectangles."""
        for i in range(self.simulation.grid_size[0]):
            for j in range(self.simulation.grid_size[1]):
                intersection = self.simulation.grid[i][j]
                x = j * self.cell_width
                y = i * self.cell_height
                
                # Draw NS traffic light (vertical rectangle)
                light_color = (self.COLORS['traffic_light_green'] 
                             if intersection.traffic_light.is_ns_green()
                             else self.COLORS['traffic_light_red'])
                pygame.draw.rect(self.grid_surface, light_color,
                               (x + self.cell_width//2 - 2,
                                y + self.cell_height//4,
                                4, self.cell_height//2))
                
                # Draw EW traffic light (horizontal rectangle)
                light_color = (self.COLORS['traffic_light_red']
                             if intersection.traffic_light.is_ns_green()
                             else self.COLORS['traffic_light_green'])
                pygame.draw.rect(self.grid_surface, light_color,
                               (x + self.cell_width//4,
                                y + self.cell_height//2 - 2,
                                self.cell_width//2, 4))
    
    def _draw_vehicle_and_trail(self):
        """Draw the vehicle and its movement trail."""
        if self.simulation.vehicles:
            vehicle = self.simulation.vehicles[0]  # Get the first vehicle
            current_pos = vehicle.current_pos
            
            # Update vehicle positions list
            if not self.vehicle_positions or self.vehicle_positions[-1] != current_pos:
                self.vehicle_positions.append(current_pos)
            
            # Draw trail
            if len(self.vehicle_positions) > 1:
                for i in range(len(self.vehicle_positions) - 1):
                    start_pos = self.vehicle_positions[i]
                    end_pos = self.vehicle_positions[i + 1]
                    
                    start_pixel = (start_pos[1] * self.cell_width + self.cell_width//2,
                                 start_pos[0] * self.cell_height + self.cell_height//2)
                    end_pixel = (end_pos[1] * self.cell_width + self.cell_width//2,
                               end_pos[0] * self.cell_height + self.cell_height//2)
                    
                    pygame.draw.line(self.grid_surface, self.COLORS['vehicle_trail'],
                                   start_pixel, end_pixel, 2)
            
            # Draw current vehicle position
            x = current_pos[1] * self.cell_width + self.cell_width//2
            y = current_pos[0] * self.cell_height + self.cell_height//2
            pygame.draw.circle(self.grid_surface, self.COLORS['vehicle'],
                             (x, y), min(self.cell_width, self.cell_height)//4)
    
    def _draw_grid_lines(self):
        """Draw grid lines."""
        for i in range(self.simulation.grid_size[0] + 1):
            y = i * self.cell_height
            pygame.draw.line(self.grid_surface, self.COLORS['grid_line'],
                           (0, y), (self.window_size[0]//2, y))
        
        for j in range(self.simulation.grid_size[1] + 1):
            x = j * self.cell_width
            pygame.draw.line(self.grid_surface, self.COLORS['grid_line'],
                           (x, 0), (x, self.window_size[1]))
    
    def _draw_path_view(self):
        """Draw the planned path view on the right surface."""
        self.path_surface.fill(self.COLORS['background'])
        
        if self.simulation.vehicles:
            vehicle = self.simulation.vehicles[0]
            path = vehicle.path
            
            # Draw grid on path view
            self._draw_path_grid()
            
            # Draw planned path with animation
            if len(path) > 1:
                # Increment animation counter
                self.animation_counter += 1
                if self.animation_counter >= self.animation_speed:
                    self.animation_counter = 0
                    if self.path_animation_index < len(path) - 1:
                        self.path_animation_index += 1
                
                # Draw path segments up to current animation index
                for i in range(min(self.path_animation_index, len(path) - 1)):
                    start_pos = path[i]
                    end_pos = path[i + 1]
                    
                    start_pixel = (start_pos[1] * self.cell_width + self.cell_width//2,
                                 start_pos[0] * self.cell_height + self.cell_height//2)
                    end_pixel = (end_pos[1] * self.cell_width + self.cell_width//2,
                               end_pos[0] * self.cell_height + self.cell_height//2)
                    
                    # Draw completed segments in regular color
                    pygame.draw.line(self.path_surface, self.COLORS['path'],
                                   start_pixel, end_pixel, 2)
                
                # Draw current segment in highlight color
                if self.path_animation_index < len(path) - 1:
                    start_pos = path[self.path_animation_index]
                    end_pos = path[self.path_animation_index + 1]
                    
                    start_pixel = (start_pos[1] * self.cell_width + self.cell_width//2,
                                 start_pos[0] * self.cell_height + self.cell_height//2)
                    end_pixel = (end_pos[1] * self.cell_width + self.cell_width//2,
                               end_pos[0] * self.cell_height + self.cell_height//2)
                    
                    pygame.draw.line(self.path_surface, self.COLORS['path_highlight'],
                                   start_pixel, end_pixel, 3)
            
            # Draw start and end points
            if path:
                # Start point
                start_pos = path[0]
                x = start_pos[1] * self.cell_width + self.cell_width//2
                y = start_pos[0] * self.cell_height + self.cell_height//2
                pygame.draw.circle(self.path_surface, (255, 0, 0),
                                 (x, y), min(self.cell_width, self.cell_height)//4)
                
                # End point
                end_pos = path[-1]
                x = end_pos[1] * self.cell_width + self.cell_width//2
                y = end_pos[0] * self.cell_height + self.cell_height//2
                pygame.draw.circle(self.path_surface, (0, 255, 0),
                                 (x, y), min(self.cell_width, self.cell_height)//4)
    
    def _draw_path_grid(self):
        """Draw grid lines for the path view."""
        # Draw roads
        for i in range(self.simulation.grid_size[0]):
            y = i * self.cell_height
            pygame.draw.rect(self.path_surface, self.COLORS['road'],
                           (0, y - self.cell_height//4,
                            self.window_size[0]//2, self.cell_height//2))
        
        for j in range(self.simulation.grid_size[1]):
            x = j * self.cell_width
            pygame.draw.rect(self.path_surface, self.COLORS['road'],
                           (x - self.cell_width//4, 0,
                            self.cell_width//2, self.window_size[1]))
        
        # Draw grid lines
        for i in range(self.simulation.grid_size[0] + 1):
            y = i * self.cell_height
            pygame.draw.line(self.path_surface, self.COLORS['grid_line'],
                           (0, y), (self.window_size[0]//2, y))
        
        for j in range(self.simulation.grid_size[1] + 1):
            x = j * self.cell_width
            pygame.draw.line(self.path_surface, self.COLORS['grid_line'],
                           (x, 0), (x, self.window_size[1]))
