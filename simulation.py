import random
import time
import pygame
import numpy as np
from traffic_model import Town, Vehicle, Direction, Action

class Visualizer:
    def __init__(self, window_size=(1200, 800)):
        self.window_size = window_size
        self.left_panel = (800, 800)    # Size for town visualization
        self.right_panel = (400, 800)   # Size for information display
        self.grid_margin = 50           # Margin around the grid
        self.cell_colors = {
            'background': (255, 255, 255),
            'grid': (200, 200, 200),
            'vehicle': (255, 0, 0),
            'trajectory': (0, 0, 255),
            'text': (0, 0, 0)
        }
        self.trajectory = []  # Store vehicle positions
        # Initialize font
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
        
    def draw_vehicle(self, screen, position, cell_size):
        """Draw the vehicle and its trajectory"""
        if position:
            # Add position to trajectory
            screen_pos = self.get_screen_pos(position, cell_size)
            self.trajectory.append(screen_pos)
            
            # Draw trajectory
            if len(self.trajectory) > 1:
                pygame.draw.lines(screen, self.cell_colors['trajectory'], False, 
                                self.trajectory, 2)
            
            # Draw vehicle
            radius = cell_size // 3
            pygame.draw.circle(screen, self.cell_colors['vehicle'], screen_pos, radius)
            
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
        
        # Draw information
        info_texts = [
            f"Steps: {sim.time_step}",
            f"Town Size: {sim.town.rows}x{sim.town.cols}",
            f"Running Vehicles: {sim.town.get_total_vehicles()}"
        ]
        
        for text in info_texts:
            text_surface = self.font.render(text, True, self.cell_colors['text'])
            screen.blit(text_surface, (x, y))
            y += line_height

class TrafficSimulation:
    def __init__(self, rows=10, cols=10, max_steps=100):
        self.town = Town(rows, cols)
        self.vehicle = None
        self.time_step = 0
        self.max_steps = max_steps
        self.initialize_vehicle()
        self.visualizer = Visualizer()
        
    def initialize_vehicle(self):
        """Create a vehicle with random position and direction"""
        self.vehicle = Vehicle(1, random.choice(list(Action)))
        
        # Random position
        row = random.randint(0, self.town.rows - 1)
        col = random.randint(0, self.town.cols - 1)
        direction = random.choice(list(Direction))
        
        # Add to town
        self.town.add_vehicle(self.vehicle, (row, col), direction)
        print(f"\nVehicle created:")
        print(f"  Position: {(row, col)}")
        print(f"  Direction: {direction.value}")
        print(f"  Initial action: {self.vehicle.action.value}")
        
    def step(self):
        """Perform one simulation step"""
        if not self.vehicle:
            return False
            
        # Store old position and action for printing
        old_pos = self.vehicle.current_position
        old_action = self.vehicle.action
        
        # Move vehicle
        if not self.town.move_vehicle(self.vehicle):
            print(f"\nStep {self.time_step}:")
            print(f"  Vehicle exited town from position {old_pos}")
            self.vehicle = None
            return False
        
        # Print movement information
        print(f"\nStep {self.time_step}:")
        print(f"  Position: {old_pos} -> {self.vehicle.current_position}")
        print(f"  Action completed: {old_action.value}")
        print(f"  Next action: {self.vehicle.action.value}")
        
        self.time_step += 1
        return True
        
    def run_simulation(self):
        """Run the simulation with visualization"""
        print("\nStarting simulation...")
        
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
            
            # Draw vehicle and perform step
            if self.vehicle:
                self.visualizer.draw_vehicle(screen, self.vehicle.current_position, cell_size)
                
                # Update display before step
                self.visualizer.draw_info_panel(screen, self)
                pygame.display.flip()
                clock.tick(1)  # 1 FPS for easy viewing
                
                # Perform simulation step
                if not self.step():
                    break
            
            # Draw information panel
            self.visualizer.draw_info_panel(screen, self)
            
            # Update display after step
            pygame.display.flip()
        
        if self.time_step >= self.max_steps:
            print(f"\nReached maximum steps ({self.max_steps})")
        
        # Show final state briefly
        pygame.time.wait(2000)
        pygame.quit()
        print("\nSimulation ended")
        print(f"Total steps: {self.time_step}")

def main():
    """Main function to run the traffic simulation"""
    # Create and run simulation
    sim = TrafficSimulation(rows=10, cols=10, max_steps=100)
    sim.run_simulation()

if __name__ == "__main__":
    main()
