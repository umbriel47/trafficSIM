import pygame
import sys
from src.simulation import Simulation
from src.visualization import Visualizer

def main():
    # Initialize simulation parameters
    grid_size = (10, 10)  # 10x10 grid
    num_vehicles = 1      # Single vehicle simulation
    
    # Create simulation instance with a single vehicle
    sim = Simulation(grid_size=grid_size, num_vehicles=num_vehicles)
    
    # Set specific start and destination for the vehicle
    # Note: These coordinates are (row, col) format
    start = (1, 1)
    destination = (8, 8)
    
    # Reset the vehicle's position and path
    if sim.vehicles:
        vehicle = sim.vehicles[0]
        vehicle.current_pos = start
        vehicle.destination = destination
        vehicle.current_path_index = 0
        vehicle.path = vehicle._calculate_path()
        
        # Place vehicle in the grid
        sim._place_vehicles()
    
    # Create visualizer with wider window for split view
    viz = Visualizer(sim, window_size=(1200, 600))
    
    # Main simulation loop
    running = True
    clock = pygame.time.Clock()
    paused = False
    
    print(f"Vehicle Path Information:")
    print(f"Start: {start}")
    print(f"Destination: {destination}")
    print(f"Planned path: {sim.vehicles[0].path if sim.vehicles else 'No vehicle'}")
    print("\nControls:")
    print("SPACE - Pause/Resume simulation")
    print("R - Reset vehicle to start position")
    print("ESC - Exit simulation")
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Toggle pause
                    paused = not paused
                elif event.key == pygame.K_r:
                    # Reset vehicle and animation
                    if sim.vehicles:
                        vehicle = sim.vehicles[0]
                        vehicle.current_pos = start
                        vehicle.current_path_index = 0
                        viz.vehicle_positions = []  # Clear the trail
                        viz.path_animation_index = 0  # Reset path animation
                        viz.animation_counter = 0
                        sim._place_vehicles()
        
        # Update simulation if not paused
        if not paused:
            sim.step()
            
            # Check if vehicle reached destination
            if sim.vehicles and sim.vehicles[0].has_reached_destination():
                paused = True  # Pause when destination is reached
        
        # Update visualization
        viz.draw()
        
        # Display simulation status
        if sim.vehicles:
            vehicle = sim.vehicles[0]
            status = "PAUSED" if paused else "RUNNING"
            if vehicle.has_reached_destination():
                status = "DESTINATION REACHED"
            pygame.display.set_caption(f"Traffic Simulation - {status}")
        
        # Control frame rate
        clock.tick(5)  # Slower speed for better visualization
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
