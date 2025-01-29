import pygame
import sys
from src.simulation import Simulation
from src.visualization import Visualizer

def main():
    # Initialize simulation parameters
    grid_size = (10, 10)  # 10x10 grid
    num_vehicles = 1
    
    # Create simulation instance
    sim = Simulation(grid_size=grid_size, num_vehicles=num_vehicles)
    
    # Create visualizer
    viz = Visualizer(sim)
    
    # Main simulation loop
    running = True
    clock = pygame.time.Clock()
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Pause/Resume simulation
                    sim.toggle_pause()
        
        # Update simulation state
        sim.step()
        
        # Update visualization
        viz.draw()
        
        # Control frame rate
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
