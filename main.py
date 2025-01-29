import pygame
from src.simulation import Simulation

def main():
    # Initialize simulation parameters
    rows = 15
    cols = 15
    p1 = 0.1  # Vehicle generation probability
    
    # Create simulation
    sim = Simulation(rows, cols, p1)
    
    # Main loop
    running = True
    clock = pygame.time.Clock()
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sim.toggle_pause()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Convert mouse position to grid coordinates
                    x, y = pygame.mouse.get_pos()
                    col = x // sim.visualizer.CELL_SIZE
                    row = y // sim.visualizer.CELL_SIZE
                    if col < cols and row < rows:
                        sim.select_intersection((row, col))
            elif event.type == pygame.MOUSEWHEEL:
                sim.visualizer.handle_mouse_wheel(event.y)
        
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
        clock.tick(10)
    
    pygame.quit()

if __name__ == "__main__":
    main()
