import random
import time
import pygame
import numpy as np
from traffic_model import Town, Vehicle, Direction, Action

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
            'trajectory': (0, 0, 255, 32),  
            'text': (0, 0, 0)
        }
        self.trajectories = []
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)
        
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
        """Draw the vehicle and its trajectory"""
        if vehicle:
            # Add position to trajectory
            screen_pos = self.get_screen_pos(vehicle.current_position, cell_size)
            if len(self.trajectories) <= vehicle.vehicle_id:
                self.trajectories.append([screen_pos])
            else:
                self.trajectories[vehicle.vehicle_id].append(screen_pos)
                # Keep only recent positions to avoid clutter
                if len(self.trajectories[vehicle.vehicle_id]) > 10:  
                    self.trajectories[vehicle.vehicle_id].pop(0)
            
            # Draw trajectory (only for every 4th vehicle to reduce visual clutter)
            if vehicle.vehicle_id % 4 == 0 and len(self.trajectories[vehicle.vehicle_id]) > 1:
                pygame.draw.lines(screen, self.cell_colors['trajectory'], False, 
                                self.trajectories[vehicle.vehicle_id], 1)  
            
            # Draw vehicle (smaller size for better visibility)
            radius = max(cell_size // 5, 2)  
            # Create a surface for the semi-transparent vehicle
            vehicle_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(vehicle_surface, self.cell_colors['vehicle'], (radius, radius), radius)
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
    
    def draw_info_panel(self, screen, sim):
        """Draw simulation information on the right panel"""
        # Start position for right panel
        x = self.left_panel[0] + 20
        y = 50
        line_height = 40
        
        # Draw vertical separator line
        pygame.draw.line(screen, self.cell_colors['grid'],
                        (self.left_panel[0], 0),
                        (self.left_panel[0], self.window_size[1]), 2)
        
        # Calculate metrics
        avg_speed = sim.get_metrics()
        
        # Draw information
        info_texts = [
            f"Steps: {sim.time_step}",
            f"Town Size: {sim.town.rows}x{sim.town.cols}",
            f"Running Vehicles: {len(sim.vehicles)}",
            "",
            "Performance Metrics:",
            f"Avg Speed: {avg_speed:.2f} nodes/step"
        ]
        
        for text in info_texts:
            text_surface = self.font.render(text, True, self.cell_colors['text'])
            screen.blit(text_surface, (x, y))
            y += line_height

class TrafficSimulation:
    def __init__(self, rows=20, cols=20, max_steps=1000):
        """Initialize simulation with town grid"""
        self.town = Town(rows, cols)
        self.max_steps = max_steps
        self.time_step = 0
        self.visualizer = Visualizer()
        
        # Create initial vehicles
        self.vehicles = []
        for i in range(800):  # Initialize 800 vehicles
            vehicle = Vehicle(i, random.choice(list(Action)))
            # Place vehicle at any random position in town
            pos = (random.randint(0, rows-1), random.randint(0, cols-1))
            # Random initial direction
            direction = random.choice(list(Direction))
            
            # Add attributes for speed calculation
            vehicle.nodes_passed = 1  # Start with 1 for initial position
            vehicle.running_time = 1  # Start with 1 for initial step
            
            self.town.add_vehicle(vehicle, pos, direction)
            vehicle.update_position(pos, direction)
            self.vehicles.append(vehicle)
            if i % 100 == 0:  # Print status every 100 vehicles
                print(f"Added {i+1} vehicles...")
        print(f"All {len(self.vehicles)} vehicles initialized")
    
    def get_metrics(self):
        """Calculate current simulation metrics"""
        if not self.vehicles:
            return 0.0
            
        # Calculate average speed across all vehicles
        total_speed = 0
        for vehicle in self.vehicles:
            # Speed = nodes passed / running time
            vehicle_speed = vehicle.nodes_passed / vehicle.running_time
            total_speed += vehicle_speed
            
        avg_speed = total_speed / len(self.vehicles)
        return avg_speed
    
    def step(self):
        """Perform one simulation step"""
        self.time_step += 1
        
        # Move each vehicle
        vehicles_to_remove = []
        for vehicle in self.vehicles:
            # Update running time for each vehicle
            vehicle.running_time += 1
            
            # Try to move vehicle
            if self.town.move_vehicle(vehicle):
                # Successfully moved, increment nodes passed
                vehicle.nodes_passed += 1
            else:
                vehicles_to_remove.append(vehicle)
        
        # Remove vehicles that have left the town
        for vehicle in vehicles_to_remove:
            self.vehicles.remove(vehicle)
        
        # Continue simulation if there are still vehicles
        return len(self.vehicles) > 0

    def run_simulation(self):
        """Run the simulation with visualization"""
        print("\nStarting simulation...")
        print(f"Initial vehicle count: {len(self.vehicles)}")
        
        # Initialize display
        screen = self.visualizer.init_display()
        clock = pygame.time.Clock()
        
        running = True
        while running and self.time_step < self.max_steps:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Clear screen
            screen.fill((255, 255, 255))
            
            # Draw grid and get cell size
            cell_size = self.visualizer.draw_grid(screen, self.town.rows)
            
            # Draw density overlay
            self.visualizer.draw_density(screen, self.town, cell_size)
            
            # Draw vehicles
            for vehicle in self.vehicles:
                self.visualizer.draw_vehicle(screen, vehicle, cell_size)
            
            # Draw information panel
            self.visualizer.draw_info_panel(screen, self)
            pygame.display.flip()
            clock.tick(5)  # Increased to 5 FPS for smoother animation
            
            # Perform simulation step
            if not self.step():
                print("\nAll vehicles have exited the town")
                break
        
        if self.time_step >= self.max_steps:
            print(f"\nReached maximum steps ({self.max_steps})")
            print(f"Remaining vehicles: {len(self.vehicles)}")
        
        # Show final state briefly
        pygame.time.wait(2000)
        pygame.quit()
        print("\nSimulation ended")
        print(f"Total steps: {self.time_step}")

def main():
    """Main function to run the traffic simulation"""
    # Create and run simulation
    sim = TrafficSimulation(rows=20, cols=20, max_steps=1000)
    sim.run_simulation()

if __name__ == "__main__":
    main()
