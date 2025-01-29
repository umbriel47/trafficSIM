import pygame
import numpy as np
from typing import Tuple, Optional
from ..models.traffic_light import Direction
from ..models.vehicle import Vehicle

class Visualizer:
    """Visualizer for the traffic simulation."""
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (64, 64, 64)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    
    # UI Constants
    CELL_SIZE = 60
    PADDING = 20
    STATS_WIDTH = 200
    FONT_SIZE = 24
    SMALL_FONT_SIZE = 20
    BUTTON_HEIGHT = 40
    BUTTON_MARGIN = 10
    
    def __init__(self, rows: int, cols: int, p1: float, grid, simulation):
        """Initialize the visualizer."""
        pygame.init()
        self.rows = rows
        self.cols = cols
        self.p1 = p1
        self.grid = grid
        self.simulation = simulation
        
        # Calculate dimensions
        self.grid_width = cols * self.CELL_SIZE + 2 * self.PADDING
        self.grid_height = rows * self.CELL_SIZE + 2 * self.PADDING
        self.total_width = self.grid_width + self.STATS_WIDTH
        self.total_height = self.grid_height
        
        # Create screen and fonts
        self.screen = pygame.display.set_mode((self.total_width, self.total_height))
        pygame.display.set_caption("Traffic Simulation")
        self.font = pygame.font.Font(None, self.FONT_SIZE)
        self.small_font = pygame.font.Font(None, self.SMALL_FONT_SIZE)
        
        # Scrolling state
        self.scroll_y = 0
        self.max_scroll = 0
        self.scroll_bar_dragging = False
    
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
        return self._create_colormap()[index]
    
    def _draw_grid_section(self):
        """Draw the grid section with traffic density."""
        # Draw grid background
        grid_rect = pygame.Rect(self.PADDING, self.PADDING, 
                              self.grid_width - 2 * self.PADDING, self.grid_height - 2 * self.PADDING)
        pygame.draw.rect(self.screen, self.WHITE, grid_rect)
        
        # Draw grid lines
        for i in range(self.rows + 1):
            y = i * self.CELL_SIZE + self.PADDING
            pygame.draw.line(self.screen, self.BLACK,
                           (self.PADDING, y),
                           (self.grid_width - self.PADDING, y))
        
        for i in range(self.cols + 1):
            x = i * self.CELL_SIZE + self.PADDING
            pygame.draw.line(self.screen, self.BLACK,
                           (x, self.PADDING),
                           (x, self.grid_height - self.PADDING))
        
        # Draw intersections with traffic lights and queues
        for pos, queues in self.grid.intersection_queues.items():
            self._draw_intersection(pos, queues)
    
    def _create_heatmap_color(self, value: float) -> Tuple[int, int, int]:
        """Create a color gradient from green to red based on value (0-1)."""
        # Ensure value is between 0 and 1
        value = max(0, min(1, value))
        
        if value < 0.5:
            # Green (0,255,0) to Yellow (255,255,0)
            r = int(510 * value)
            g = 255
            b = 0
        else:
            # Yellow (255,255,0) to Red (255,0,0)
            r = 255
            g = int(510 * (1 - value))
            b = 0
        
        # Add some alpha for better visibility
        return (r, g, b)
    
    def _draw_intersection(self, pos: Tuple[int, int], queue_info: dict):
        """Draw an intersection with heatmap and traffic lights."""
        x = pos[1] * self.CELL_SIZE + self.PADDING
        y = pos[0] * self.CELL_SIZE + self.PADDING
        
        # Calculate total vehicles and waiting time for heatmap
        total_vehicles = 0
        total_waiting = 0
        for direction, vehicles in queue_info.items():
            total_vehicles += len(vehicles)
            total_waiting += sum(v.get_waiting_time() for v in vehicles)
        
        # Normalize values for heatmap
        max_vehicles = 8  # Reduced for more color variation
        max_waiting = 30  # Maximum expected waiting time
        
        # Calculate heatmap value based on both vehicle count and waiting time
        density_value = min(total_vehicles / max_vehicles, 1.0)
        waiting_value = min(total_waiting / (max_waiting * max_vehicles), 1.0)
        heatmap_value = max(density_value, waiting_value)  # Use the more severe indicator
        
        # Draw intersection background with heatmap color
        color = self._create_heatmap_color(heatmap_value)
        pygame.draw.rect(self.screen, color,
                        (x + 1, y + 1, self.CELL_SIZE - 2, self.CELL_SIZE - 2))
        
        # Draw traffic light indicators
        light = self.grid.get_traffic_light(pos)
        is_horizontal_green = light.is_green(Direction.HORIZONTAL)
        
        # Draw traffic light states
        light_size = (self.CELL_SIZE * 0.2, self.CELL_SIZE * 0.1)
        
        # Horizontal light
        pygame.draw.rect(self.screen,
                        self.GREEN if is_horizontal_green else self.RED,
                        (x + self.CELL_SIZE * 0.1, 
                         y + self.CELL_SIZE * 0.45,
                         light_size[0], light_size[1]))
        
        # Vertical light
        pygame.draw.rect(self.screen,
                        self.GREEN if not is_horizontal_green else self.RED,
                        (x + self.CELL_SIZE * 0.45,
                         y + self.CELL_SIZE * 0.1,
                         light_size[1], light_size[0]))
        
        # Draw vehicle count
        if total_vehicles > 0:
            count_text = self.small_font.render(str(total_vehicles), True, self.BLACK)
            text_rect = count_text.get_rect(center=(x + self.CELL_SIZE/2, y + self.CELL_SIZE/2))
            self.screen.blit(count_text, text_rect)
    
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
    
    def _draw_scheduler_section(self, y_offset: int) -> int:
        """Draw the scheduler section of the stats panel."""
        # Draw section title
        title = "Traffic Light Control"
        text = self.font.render(title, True, self.WHITE)
        self.screen.blit(text, (self.grid_width + 10, y_offset))
        y_offset += 30
        
        # Draw current scheduler info
        current = "Independent"  # Default scheduler
        text = self.small_font.render(f"Current: {current}", True, self.WHITE)
        self.screen.blit(text, (self.grid_width + 10, y_offset))
        y_offset += 20
        
        return y_offset + 10
    
    def _wrap_text(self, text: str, max_width: int) -> list:
        """Wrap text to fit within a given width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            # Test if current line exceeds max width
            test_line = ' '.join(current_line)
            if self.small_font.size(test_line)[0] > max_width:
                if len(current_line) > 1:
                    # Remove last word and add line
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Line contains single long word
                    lines.append(test_line)
                    current_line = []
        
        # Add remaining line
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _draw_stats_section(self, time_step: int, avg_speed: float, active_vehicles: int):
        """Draw the statistics section with a modern, minimalist design."""
        # Background
        stats_rect = pygame.Rect(self.grid_width, 0, 
                               self.STATS_WIDTH, self.total_height)
        pygame.draw.rect(self.screen, self.DARK_GRAY, stats_rect)
        
        y_offset = self.PADDING
        line_height = self.BUTTON_HEIGHT
        
        # Title
        title = self.font.render("TRAFFIC CONTROL SYSTEM", True, self.WHITE)
        title_rect = title.get_rect(center=(self.grid_width + self.STATS_WIDTH//2, y_offset))
        self.screen.blit(title, title_rect)
        y_offset += line_height * 1.5
        
        # Draw scheduler section
        y_offset = self._draw_scheduler_section(y_offset)
        y_offset += line_height/2
        
        # Draw sections
        sections = [
            ("CURRENT STATE", [
                f"Time Step: {time_step}",
                f"Active Vehicles: {active_vehicles}",
                f"Average Speed: {avg_speed:.2f}",
                f"Status: {'PAUSED' if self.simulation.paused else 'RUNNING'}"
            ]),
            ("CONTROLS", [
                "SPACE - Pause/Resume",
                "ESC - Exit",
                "Click intersection for details"
            ])
        ]
        
        for title, items in sections:
            # Section title with highlight
            pygame.draw.rect(self.screen, self.LIGHT_GRAY,
                           (self.grid_width + 10, y_offset, 
                            self.STATS_WIDTH - 20, line_height))
            text = self.font.render(title, True, self.WHITE)
            self.screen.blit(text, (self.grid_width + 20, y_offset))
            y_offset += line_height * 1.2
            
            # Section items
            for item in items:
                text = self.small_font.render(item, True, self.WHITE)
                self.screen.blit(text, (self.grid_width + 20, y_offset))
                y_offset += line_height * 0.8
            
            y_offset += line_height/2
    
    def _draw_intersection_detail(self, pos: Tuple[int, int], info: dict):
        """Draw detailed information about an intersection."""
        if not info:
            return
            
        # Draw info panel
        panel_width = 600
        panel_height = 400
        panel_x = (self.total_width - panel_width) // 2
        panel_y = (self.total_height - panel_height) // 2
        
        # Create a surface for the panel content
        content_surface = pygame.Surface((panel_width - 20, 1000))  # Extra height for scrolling
        content_surface.fill(self.DARK_GRAY)
        
        # Draw title on main panel
        title = f"Intersection ({pos[0]}, {pos[1]}) Details"
        text = self.font.render(title, True, self.WHITE)
        content_surface.blit(text, (20, 20))
        
        # Draw queue information with scrolling
        y = 70
        queues = info.get('queues', {})
        for direction, vehicles in queues.items():
            dir_name = f"{direction} Queue ({len(vehicles)} vehicles):"
            text = self.font.render(dir_name, True, self.WHITE)
            content_surface.blit(text, (20, y))
            
            y += 30
            for i, vehicle in enumerate(vehicles):
                # Get vehicle information
                waiting_time = vehicle.get_waiting_time()
                next_direction = vehicle.get_next_direction()
                turn_type = vehicle.get_turn_type() if hasattr(vehicle, 'get_turn_type') else 'unknown'
                
                vehicle_text = f"Vehicle {i+1}: {waiting_time}s wait, "
                vehicle_text += f"going {next_direction}, {turn_type} turn"
                text = self.small_font.render(vehicle_text, True, self.WHITE)
                
                # Create clickable area for vehicle
                vehicle_rect = pygame.Rect(40, y, panel_width - 80, 20)
                mouse_pos = pygame.mouse.get_pos()
                adjusted_pos = (mouse_pos[0] - panel_x - 10, mouse_pos[1] - panel_y - 10)
                
                if vehicle_rect.collidepoint(adjusted_pos):
                    pygame.draw.rect(content_surface, self.LIGHT_GRAY, vehicle_rect)
                    if pygame.mouse.get_pressed()[0]:  # Left click
                        return (direction, i)  # Return selected vehicle info
                
                content_surface.blit(text, (20, y))
                y += 20
            y += 10
        
        # Calculate max scroll
        self.max_scroll = max(0, y - panel_height + 40)
        
        # Draw visible portion of content
        visible_region = content_surface.subsurface(
            (0, self.scroll_y, panel_width - 20, min(panel_height - 40, y - self.scroll_y))
        )
        
        # Draw main panel
        pygame.draw.rect(self.screen, self.DARK_GRAY,
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
               selected_vehicle: Optional[Vehicle] = None) -> Optional[Tuple[Direction, int]]:
        """Update the visualization."""
        # Clear screen
        self.screen.fill(self.BLACK)
        
        # Draw grid section
        self._draw_grid_section()
        
        # Draw stats section
        self._draw_stats_section(time_step, avg_speed, active_vehicles)
        
        # Draw intersection detail if selected and simulation is paused
        if selected_intersection and self.simulation.paused:
            info = {
                'queues': self.grid.intersection_queues[selected_intersection],
                'light': self.grid.get_traffic_light(selected_intersection)
            }
            return self._draw_intersection_detail(selected_intersection, info)
        
        # Draw vehicle path if selected
        if selected_vehicle:
            self._draw_vehicle_path(selected_vehicle)
        
        # Update display
        pygame.display.flip()
        return None
