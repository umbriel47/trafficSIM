import random
import time
import pygame
import numpy as np
from traffic_model import Town, Vehicle, Direction, Action, TrafficLightStrategy

class Visualizer:
    def __init__(self, window_size=(1600, 900)):  
        self.window_size = window_size
        self.left_panel = (1200, 900)    
        self.right_panel = (400, 900)    
        self.grid_margin = 40            
        self.cell_colors = {
            'background': (255, 255, 255),
            'grid': (200, 200, 200),
            'vehicle': (255, 0, 0, 180),
            'text': (0, 0, 0),
            'timer': (50, 50, 200)
        }
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)
        self.timer_font = pygame.font.SysFont('Arial', 36)
    
    def init_display(self):
        """Initialize pygame display"""
        pygame.init()
        screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Traffic Simulation")
        return screen
        
    def draw_grid(self, screen, town_size):
        """Draw the town grid"""
        # Calculate cell size based on available space
        grid_size = min(self.left_panel[0], self.left_panel[1]) - 2 * self.grid_margin
        cell_size = grid_size // town_size  # town_size is already an integer
        
        # Draw grid lines
        for i in range(town_size + 1):
            x = self.grid_margin + i * cell_size
            y = self.grid_margin + i * cell_size
            # Vertical lines
            pygame.draw.line(screen, self.cell_colors['grid'], 
                           (x, self.grid_margin), 
                           (x, self.grid_margin + town_size * cell_size), 2)
            # Horizontal lines
            pygame.draw.line(screen, self.cell_colors['grid'], 
                           (self.grid_margin, y),
                           (self.grid_margin + town_size * cell_size, y), 2)
                           
        return cell_size
        
    def get_screen_pos(self, grid_pos, cell_size):
        """Convert grid position to screen coordinates"""
        row, col = grid_pos
        x = self.grid_margin + col * cell_size + cell_size // 2
        y = self.grid_margin + row * cell_size + cell_size // 2
        return (x, y)
        
    def draw_vehicle(self, screen, vehicle, cell_size):
        """Draw the vehicle without trajectory"""
        if vehicle:
            screen_pos = self.get_screen_pos(vehicle.current_position, cell_size)
            # Draw vehicle
            radius = max(cell_size // 5, 2)
            vehicle_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(vehicle_surface, self.cell_colors['vehicle'], 
                             (radius, radius), radius)
            screen.blit(vehicle_surface, (screen_pos[0]-radius, screen_pos[1]-radius))
            
    def draw_density(self, screen, town, cell_size):
        """Draw density overlay on the grid"""
        # Get density matrix
        density_matrix = town.get_node_density()
        max_density = density_matrix.max()
        
        # Draw density overlay
        if max_density > 0:
            for row in range(town.rows):
                for col in range(town.cols):
                    density = density_matrix[row, col]
                    if density > 0:
                        x = self.grid_margin + col * cell_size
                        y = self.grid_margin + row * cell_size
                        surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                        # Normalize density and set alpha
                        alpha = int((density / max_density) * 128)  # Max alpha 128 for better visibility
                        pygame.draw.rect(surface, (255, 0, 0, alpha), 
                                      (0, 0, cell_size, cell_size))
                        screen.blit(surface, (x, y))
    
    def draw_traffic_lights(self, screen, town, cell_size):
        """Draw traffic lights at each intersection"""
        light_size = max(cell_size // 6, 4)
        for row in range(town.rows):
            for col in range(town.cols):
                intersection = town.grid[row][col]
                light = intersection['traffic_light']
                screen_pos = self.get_screen_pos((row, col), cell_size)
                
                # Draw NS light (top)
                ns_color = (0, 255, 0) if light.is_ns_green else (255, 0, 0)
                pygame.draw.circle(screen, ns_color, 
                                (screen_pos[0], screen_pos[1] - light_size*2), 
                                light_size)
                
                # Draw EW light (right)
                ew_color = (255, 0, 0) if light.is_ns_green else (0, 255, 0)
                pygame.draw.circle(screen, ew_color,
                                (screen_pos[0] + light_size*2, screen_pos[1]),
                                light_size)
    
    def draw_info_panel(self, screen, sim, time_text):
        """Draw simulation information on the right panel"""
        x = self.left_panel[0] + 20
        y = 50
        line_height = 40
        
        # Draw vertical separator line
        pygame.draw.line(screen, self.cell_colors['grid'],
                        (self.left_panel[0], 0),
                        (self.left_panel[0], self.window_size[1]), 2)
        
        # Calculate metrics
        avg_speed = sim.get_metrics()
        running_time = max(0, sim.time_step - sim.start_time)
        
        # Draw information
        info_texts = [
            f"Steps: {sim.time_step}",
            f"Town Size: {sim.town.rows}x{sim.town.cols}",
            "",
            f"Active Vehicles: {len(sim.vehicles)}",
            f"Running Time: {running_time}",
            "",
            "Performance Metrics:",
            f"Avg Speed: {avg_speed:.2f} moves/step",
            "",
            f"Next Step in: {time_text}"
        ]
        
        for text in info_texts:
            text_surface = self.font.render(text, True, self.cell_colors['text'])
            screen.blit(text_surface, (x, y))
            y += line_height

class TrafficSimulation:
    def __init__(self, rows=20, cols=20, max_steps=1000, light_strategy=TrafficLightStrategy.INDEPENDENT, num_vehicles=100):
        """Initialize simulation with town grid"""
        self.town = Town(rows, cols, light_strategy)
        self.max_steps = max_steps
        self.time_step = 0
        self.visualizer = Visualizer()
        self.start_time = 0
        
        # Vehicle tracking
        self.vehicles = []
        self.vehicle_stats = {}  # Track stats for each vehicle
        
        # Create initial vehicles
        for i in range(num_vehicles):
            vehicle = Vehicle(i, random.choice(list(Action)))
            pos = (random.randint(0, rows-1), random.randint(0, cols-1))
            direction = random.choice(list(Direction))
            
            self.town.add_vehicle(vehicle, pos, direction)
            vehicle.update_position(pos, direction)
            self.vehicles.append(vehicle)
            
            # Initialize vehicle stats
            self.vehicle_stats[vehicle.vehicle_id] = {
                'moves': 0,
                'start_time': None
            }
            
            if i % 20 == 0:
                print(f"Added {i+1} vehicles...")
        print(f"All {len(self.vehicles)} vehicles initialized")
    
    def get_metrics(self):
        """Calculate average speed across all vehicles"""
        if not self.vehicles:
            return 0.0
        
        total_speed = 0
        active_vehicles = 0
        
        for vehicle in self.vehicles:
            stats = self.vehicle_stats[vehicle.vehicle_id]
            if stats['start_time'] is not None:
                # Calculate running time for this vehicle
                vehicle_time = self.time_step - stats['start_time']
                if vehicle_time > 0:
                    # Calculate speed for this vehicle
                    vehicle_speed = stats['moves'] / vehicle_time
                    total_speed += vehicle_speed
                    active_vehicles += 1
        
        # Return average speed across all active vehicles
        return total_speed / max(1, active_vehicles)
    
    def step(self):
        """Perform one simulation step"""
        self.time_step += 1
        
        # Update all traffic lights
        self.town.update_traffic_lights()
        
        # Move vehicles
        vehicles_to_remove = []
        
        for vehicle in self.vehicles:
            old_pos = vehicle.current_position
            stats = self.vehicle_stats[vehicle.vehicle_id]
            
            # Try to move vehicle
            moved = self.town.move_vehicle(vehicle)
            if moved:
                # Initialize start time if this is the vehicle's first move
                if stats['start_time'] is None:
                    stats['start_time'] = self.time_step - 1
                # Check if position actually changed
                if old_pos != vehicle.current_position:
                    stats['moves'] += 1
            if not moved:
                vehicles_to_remove.append(vehicle)
        
        # Remove vehicles that have left the town
        for vehicle in vehicles_to_remove:
            self.vehicles.remove(vehicle)
        
        # Continue simulation if vehicles remain
        return len(self.vehicles) > 0
    
    def run_simulation(self):
        """Run the simulation with visualization"""
        print("\nStarting simulation...")
        print(f"Initial vehicle count: {len(self.vehicles)}")
        
        # Initialize display
        screen = self.visualizer.init_display()
        clock = pygame.time.Clock()
        
        running = True
        paused = False
        step_timer = 0  # Timer for step delay
        step_delay = 200  # 200 milliseconds = 0.2 seconds
        
        while running and self.time_step < self.max_steps:
            current_time = pygame.time.get_ticks()
            time_to_next_step = step_delay - (current_time - step_timer)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused  # Toggle pause state
                        if paused:
                            print("Simulation paused. Press SPACE to continue.")
                        else:
                            print("Simulation resumed.")
                            step_timer = current_time  # Reset timer when unpausing
            
            # Clear screen
            screen.fill((255, 255, 255))
            
            # Draw grid and get cell size
            cell_size = self.visualizer.draw_grid(screen, self.town.rows)
            
            # Draw traffic lights
            self.visualizer.draw_traffic_lights(screen, self.town, cell_size)
            
            # Draw density overlay
            self.visualizer.draw_density(screen, self.town, cell_size)
            
            # Draw vehicles
            for vehicle in self.vehicles:
                self.visualizer.draw_vehicle(screen, vehicle, cell_size)
            
            # Update info panel text based on pause state
            time_text = "PAUSED" if paused else f"{time_to_next_step/1000:.1f}s"
            self.visualizer.draw_info_panel(screen, self, time_text)
            
            pygame.display.flip()
            
            # Only update simulation if not paused
            if not paused and current_time - step_timer >= step_delay:
                # Perform simulation step
                if not self.step():
                    print("\nAll vehicles have exited the town")
                    break
                step_timer = current_time  # Reset timer
            
            clock.tick(60)  # Limit to 60 FPS for smooth display
        
        if self.time_step >= self.max_steps:
            print(f"\nReached maximum steps ({self.max_steps})")
            print(f"Remaining vehicles: {len(self.vehicles)}")
        
        # Show final state briefly
        pygame.time.wait(2000)
        pygame.quit()
        print("\nSimulation ended")
        print(f"Total steps: {self.time_step}")

def main():
    """Main function to run the simulation"""
    # Create and run simulation with independent traffic light control
    sim = TrafficSimulation(rows=20, cols=20, max_steps=1000, 
                          light_strategy=TrafficLightStrategy.BASIC,
                          num_vehicles=200)  # Now specify number of vehicles
    sim.run_simulation()

if __name__ == "__main__":
    main()
