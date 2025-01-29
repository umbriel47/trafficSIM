import pygame
from src.simulation import Simulation

def main():
    # Initialize simulation parameters
    rows = 10
    cols = 10
    p1 = 0.3  # Vehicle generation probability
    
    # Create simulation
    sim = Simulation(rows, cols, p1)
    
    # Main loop
    running = True
    clock = pygame.time.Clock()
    
    while running:
        # Handle events through simulation
        running = sim.handle_events()
        
        # Update simulation
        sim.step()
        
        # Update visualization and get selected vehicle info
        selected_vehicle_info = sim.visualizer.update(
            sim.time_step,
            sim.get_average_speed(),
            sim.active_vehicles,
            sim.selected_intersection,
            sim.selected_vehicle
        )
        
        # Handle vehicle selection
        if selected_vehicle_info and sim.selected_intersection:
            direction, vehicle_idx = selected_vehicle_info
            queue_idx = list(sim.grid.get_intersection_info(
                sim.selected_intersection).keys()).index(direction)
            sim.select_vehicle(sim.selected_intersection, queue_idx, vehicle_idx)
        
        # Control frame rate
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
