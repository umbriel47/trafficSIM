import pygame
import numpy as np
from typing import Tuple, Optional
from ..models.traffic_light import Direction
from ..models.vehicle import Vehicle

class Visualizer:
    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (200, 200, 200)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    DARK_BLUE = (0, 0, 128)
    
    # UI Constants
    CELL_SIZE = 60
    STATS_WIDTH = 400
    PADDING = 20
    FONT_SIZE = 24
    SMALL_FONT_SIZE = 18
    
    def __init__(self, rows: int, cols: int, p1: float, grid):
        """Initialize the visualizer."""
        pygame.init()
        self.rows = rows
        self.cols = cols
        self.p1 = p1
        self.grid = grid
        
        # Calculate dimensions
        self.grid_width = cols * self.CELL_SIZE
        self.grid_height = rows * self.CELL_SIZE
        self.total_width = self.grid_width + self.STATS_WIDTH + self.PADDING * 2
        self.total_height = max(self.grid_height, 800) + self.PADDING * 2
        
        # Initialize display
        self.screen = pygame.display.set_mode((self.total_width, self.total_height))
        pygame.display.set_caption("Traffic Simulation")
        
        # Initialize fonts
        self.font = pygame.font.Font(None, self.FONT_SIZE)
        self.small_font = pygame.font.Font(None, self.SMALL_FONT_SIZE)
        
        # Stats section position
        self.stats_section_x = self.grid_width + self.PADDING * 2
        
        # Scroll state for intersection detail
        self.scroll_y = 0
        self.max_scroll = 0
        self.scroll_bar_dragging = False
        
        # Create colormap
        self.colormap = self._create_colormap()
    
    def _create_colormap(self):
        """Create a colormap for the heatmap visualization."""
        colors = [
            (0, 255, 0),    # Green for low waiting time
            (255, 255, 0),  # Yellow for medium waiting time
            (255, 0, 0)     # Red for high waiting time
        ]
        n_colors = 256
        colormap = []
        for i in range(n_colors):
            if i < n_colors // 2:
                # Interpolate between green and yellow
                t = i / (n_colors // 2)
                r = int(colors[0][0] * (1-t) + colors[1][0] * t)
                g = int(colors[0][1] * (1-t) + colors[1][1] * t)
                b = int(colors[0][2] * (1-t) + colors[1][2] * t)
            else:
                # Interpolate between yellow and red
                t = (i - n_colors // 2) / (n_colors // 2)
                r = int(colors[1][0] * (1-t) + colors[2][0] * t)
                g = int(colors[1][1] * (1-t) + colors[1][2] * t)
                b = int(colors[1][2] * (1-t) + colors[2][2] * t)
            colormap.append((r, g, b))
        return colormap
    
    def _get_heatmap_color(self, waiting_time: int) -> Tuple[int, int, int]:
        """Get color for heatmap based on waiting time."""
        max_time = 50  # Maximum waiting time for color scaling
        index = min(int(waiting_time / max_time * 255), 255)
        return self.colormap[index]
    
    def _draw_grid_section(self):
        """Draw the grid section with traffic density."""
        # Draw grid background
        self.screen.fill(self.WHITE, (0, 0, self.grid_width + self.PADDING, self.total_height))
        
        # Get vehicle density
        density = self.grid.get_total_vehicles()
        max_density = max(1, np.max(density))  # Avoid division by zero
        
        # Draw cells
        for i in range(self.rows):
            for j in range(self.cols):
                x = j * self.CELL_SIZE
                y = i * self.CELL_SIZE
                
                # Draw cell border
                pygame.draw.rect(self.screen, self.GRAY, 
                               (x, y, self.CELL_SIZE, self.CELL_SIZE), 1)
                
                # Get vehicle count
                vehicle_count = density[i, j]
                
                if vehicle_count > 0:
                    # Draw density indicator with color scale
                    color_intensity = int(255 * (vehicle_count / max_density))
                    cell_color = (0, 0, min(color_intensity + 50, 255))  # Blue gradient
                    pygame.draw.rect(self.screen, cell_color,
                                   (x+1, y+1, self.CELL_SIZE-2, self.CELL_SIZE-2))
                    
                    # Draw vehicle count
                    text = self.small_font.render(str(int(vehicle_count)), True, self.WHITE)
                    text_rect = text.get_rect(center=(x + self.CELL_SIZE//2, y + self.CELL_SIZE//2))
                    self.screen.blit(text, text_rect)
                
                # Draw traffic light
                light = self.grid.get_traffic_light((i, j))
                self._draw_traffic_light(x, y, light)
    
    def _draw_traffic_light(self, x: int, y: int, light):
        """Draw traffic light indicators for both directions."""
        # Draw background circles
        pygame.draw.circle(self.screen, self.BLACK, (x + 10, y + 10), 6)  # NS background
        pygame.draw.circle(self.screen, self.BLACK, (x + self.CELL_SIZE - 10, y + 10), 6)  # EW background
        
        # Draw NS light (left circle)
        ns_color = self.GREEN if not light.is_green(Direction.HORIZONTAL) else self.RED
        pygame.draw.circle(self.screen, ns_color, (x + 10, y + 10), 5)
        
        # Draw EW light (right circle)
        ew_color = self.GREEN if light.is_green(Direction.HORIZONTAL) else self.RED
        pygame.draw.circle(self.screen, ew_color, (x + self.CELL_SIZE - 10, y + 10), 5)
        
        # Draw direction indicators
        text_ns = self.small_font.render("NS", True, self.BLACK)
        text_ew = self.small_font.render("EW", True, self.BLACK)
        self.screen.blit(text_ns, (x + 5, y + 15))
        self.screen.blit(text_ew, (x + self.CELL_SIZE - 15, y + 15))
    
    def _draw_stats_section(self, time_step: int, avg_speed: float, active_vehicles: int):
        """Draw the statistics section with a modern, tech-inspired design."""
        # Background
        stats_rect = pygame.Rect(self.stats_section_x, 0, 
                               self.STATS_WIDTH, self.total_height)
        pygame.draw.rect(self.screen, self.DARK_BLUE, stats_rect)
        
        y_offset = self.PADDING
        line_height = 40
        
        # Title
        title = self.font.render("TRAFFIC CONTROL SYSTEM", True, self.WHITE)
        title_rect = title.get_rect(center=(self.stats_section_x + self.STATS_WIDTH//2, y_offset))
        self.screen.blit(title, title_rect)
        y_offset += line_height * 1.5
        
        # Sections with modern design
        sections = [
            ("SIMULATION SETTINGS", [
                f"Grid Size: {self.rows}x{self.cols}",
                f"Vehicle Generation Rate: {self.p1:.2f}"
            ]),
            ("REAL-TIME METRICS", [
                f"Time Step: {time_step}",
                f"Active Vehicles: {active_vehicles}",
                f"Average Speed: {avg_speed:.2f} cells/step"
            ]),
            ("TRAFFIC DENSITY", [
                "● Low (1-5 vehicles)",
                "● Medium (6-10 vehicles)",
                "● High (>10 vehicles)"
            ])
        ]
        
        for section_title, items in sections:
            # Section header
            pygame.draw.rect(self.screen, self.BLACK,
                           (self.stats_section_x + 10, y_offset - 5,
                            self.STATS_WIDTH - 20, line_height))
            text = self.font.render(section_title, True, self.WHITE)
            self.screen.blit(text, (self.stats_section_x + 20, y_offset))
            y_offset += line_height
            
            # Section items
            for item in items:
                text = self.small_font.render(item, True, self.WHITE)
                self.screen.blit(text, (self.stats_section_x + 30, y_offset))
                y_offset += line_height
            
            y_offset += line_height/2
        
        # Draw density scale bar
        self._draw_density_scale(y_offset)
    
    def _draw_density_scale(self, y_offset: int):
        """Draw the density scale bar."""
        legend_width = self.STATS_WIDTH - 40
        legend_height = 20
        x = self.stats_section_x + 20
        
        # Draw gradient
        for i in range(legend_width):
            intensity = int(255 * (i / legend_width))
            color = (0, 0, min(intensity + 50, 255))  # Blue gradient
            pygame.draw.line(self.screen, color, 
                           (x + i, y_offset),
                           (x + i, y_offset + legend_height))
        
        # Draw labels
        labels = ["0", "5", "10", "15+"]
        positions = [0, 0.33, 0.67, 1]
        for label, pos in zip(labels, positions):
            text = self.small_font.render(label, True, self.WHITE)
            text_rect = text.get_rect(center=(x + pos * legend_width, y_offset + legend_height + 15))
            self.screen.blit(text, text_rect)
    
    def _draw_intersection_detail(self, pos: Tuple[int, int], info: dict):
        """Draw detailed information about an intersection."""
        if not info:
            return
            
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.total_width, self.total_height))
        overlay.fill(self.BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Draw info panel
        panel_width = 600
        panel_height = 400
        panel_x = (self.total_width - panel_width) // 2
        panel_y = (self.total_height - panel_height) // 2
        
        # Create a surface for the panel content
        content_surface = pygame.Surface((panel_width - 20, 1000))  # Extra height for scrolling
        content_surface.fill(self.DARK_BLUE)
        
        # Draw title on main panel
        title = f"Intersection ({pos[0]}, {pos[1]}) Details"
        text = self.font.render(title, True, self.WHITE)
        content_surface.blit(text, (20, 20))
        
        # Draw queue information with scrolling
        y = 70
        for direction, vehicles in info.items():
            dir_name = f"{direction} Queue ({len(vehicles)} vehicles):"
            text = self.font.render(dir_name, True, self.WHITE)
            content_surface.blit(text, (20, y))
            
            y += 30
            for i, v_info in enumerate(vehicles):
                vehicle_text = f"Vehicle {i+1}: {v_info['waiting_time']}s wait, "
                vehicle_text += f"going {v_info['next_direction']}, {v_info['turn_type']} turn"
                text = self.small_font.render(vehicle_text, True, self.WHITE)
                
                # Create clickable area for vehicle
                vehicle_rect = pygame.Rect(40, y, panel_width - 80, 20)
                if vehicle_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(content_surface, self.BLUE, vehicle_rect)
                    if pygame.mouse.get_pressed()[0]:  # Left click
                        return (direction, i)  # Return selected vehicle info
                
                content_surface.blit(text, (20, y))
                y += 20
            y += 10
        
        # Calculate max scroll
        self.max_scroll = max(0, y - panel_height + 40)
        
        # Draw visible portion of content
        visible_region = content_surface.subsurface(
            (0, self.scroll_y, panel_width - 20, panel_height - 40)
        )
        
        # Draw main panel
        pygame.draw.rect(self.screen, self.DARK_BLUE,
                        (panel_x, panel_y, panel_width, panel_height))
        self.screen.blit(visible_region, (panel_x + 10, panel_y + 10))
        
        # Draw scroll bar if needed
        if self.max_scroll > 0:
            scroll_bar_height = max(40, panel_height * panel_height / (y + 40))
            scroll_bar_pos = panel_height * self.scroll_y / (y + 40)
            
            # Draw scroll bar background
            pygame.draw.rect(self.screen, self.GRAY,
                           (panel_x + panel_width - 20, panel_y,
                            10, panel_height))
            
            # Draw scroll bar
            pygame.draw.rect(self.screen, self.WHITE,
                           (panel_x + panel_width - 20,
                            panel_y + scroll_bar_pos,
                            10, scroll_bar_height))
            
            # Handle scroll bar dragging
            mouse_pos = pygame.mouse.get_pos()
            scroll_bar_rect = pygame.Rect(panel_x + panel_width - 20,
                                        panel_y, 10, panel_height)
            
            if pygame.mouse.get_pressed()[0]:  # Left click
                if scroll_bar_rect.collidepoint(mouse_pos):
                    self.scroll_bar_dragging = True
            else:
                self.scroll_bar_dragging = False
            
            if self.scroll_bar_dragging:
                relative_y = (mouse_pos[1] - panel_y) / panel_height
                self.scroll_y = min(self.max_scroll,
                                  max(0, int(relative_y * (y + 40))))
        
        return None  # No vehicle selected
    
    def handle_mouse_wheel(self, y):
        """Handle mouse wheel scrolling."""
        if self.max_scroll > 0:
            self.scroll_y = min(self.max_scroll,
                              max(0, self.scroll_y - y * 20))
    
    def _draw_vehicle_path(self, vehicle: Vehicle):
        """Draw the path of a selected vehicle with heatmap coloring."""
        if not vehicle:
            return
            
        path = vehicle.get_path_with_delays()
        if len(path) < 2:
            return
            
        for i in range(len(path) - 1):
            start_pos = path[i][0]
            end_pos = path[i+1][0]
            waiting_time = path[i][1]
            
            start_x = start_pos[1] * self.CELL_SIZE + self.CELL_SIZE // 2
            start_y = start_pos[0] * self.CELL_SIZE + self.CELL_SIZE // 2
            end_x = end_pos[1] * self.CELL_SIZE + self.CELL_SIZE // 2
            end_y = end_pos[0] * self.CELL_SIZE + self.CELL_SIZE // 2
            
            color = self._get_heatmap_color(waiting_time)
            pygame.draw.line(self.screen, color, (start_x, start_y), (end_x, end_y), 3)
    
    def update(self, time_step: int, avg_speed: float, active_vehicles: int,
              selected_intersection: Optional[Tuple[int, int]] = None,
              selected_vehicle: Optional[Vehicle] = None):
        """Update the visualization."""
        # Clear screen
        self.screen.fill(self.WHITE)
        
        # Draw main sections
        self._draw_grid_section()
        self._draw_stats_section(time_step, avg_speed, active_vehicles)
        
        # Draw selected vehicle path
        if selected_vehicle:
            self._draw_vehicle_path(selected_vehicle)
        
        # Draw intersection detail if selected
        selected_vehicle_info = None
        if selected_intersection:
            info = self.grid.get_intersection_info(selected_intersection)
            selected_vehicle_info = self._draw_intersection_detail(selected_intersection, info)
        
        # Update display
        pygame.display.flip()
        
        return selected_vehicle_info
