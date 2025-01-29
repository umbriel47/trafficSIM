import numpy as np
from typing import Tuple
from src.models.grid import Grid
from src.models.vehicle import Vehicle
from src.controllers.simple import SimpleController
from src.visualization.visualizer import Visualizer
from src.models.traffic_light import Direction

class Simulation:
    def __init__(self, rows: int, cols: int, p1: float = 0.1):
        """Initialize simulation.
        
        Args:
            rows: Number of rows in the grid
            cols: Number of columns in the grid
            p1: Probability of vehicle generation at each intersection
        """
        self.grid = Grid(rows, cols)
        self.controller = SimpleController(self.grid)
        self.visualizer = Visualizer(self.grid, rows=rows, cols=cols, p1=p1)
        self.p1 = p1
        self.time_step = 0
    
    def generate_vehicles(self):
        """Generate new vehicles based on probability p1."""
        for i in range(self.grid.rows):
            for j in range(self.grid.cols):
                if np.random.random() < self.p1:
                    # Generate random destination
                    dest_row = np.random.randint(0, self.grid.rows)
                    dest_col = np.random.randint(0, self.grid.cols)
                    
                    # Skip if destination is same as start
                    if (dest_row, dest_col) == (i, j):
                        continue
                    
                    # Create and add vehicle
                    vehicle = Vehicle(
                        start=(i, j),
                        destination=(dest_row, dest_col),
                        grid_size=(self.grid.rows, self.grid.cols)
                    )
                    self.grid.add_vehicle((i, j), vehicle)
    
    def remove_vehicles(self):
        """Remove vehicles that have reached their destination."""
        for pos in self.grid.intersection_queues:
            for direction in [self.grid.NORTH, self.grid.SOUTH, self.grid.EAST, self.grid.WEST]:
                queue = self.grid.get_direction_queue(pos, direction)
                vehicles_to_remove = [v for v in queue if v.has_reached_destination()]
                for vehicle in vehicles_to_remove:
                    self.grid.remove_vehicle(pos, vehicle)
    
    def move_vehicles(self):
        """Move vehicles according to traffic rules."""
        # Process each intersection
        for pos in self.grid.intersection_queues:
            # Get traffic light at this intersection
            light = self.grid.get_traffic_light(pos)
            
            # Track if we've moved a vehicle in the current green direction
            moved_in_green = False
            
            # Process each direction queue
            for direction in [self.grid.NORTH, self.grid.SOUTH, self.grid.EAST, self.grid.WEST]:
                queue = self.grid.get_direction_queue(pos, direction)
                
                # Process each vehicle in the queue
                vehicles_to_process = list(queue)  # Create a copy to avoid modification during iteration
                for vehicle in vehicles_to_process:
                    if vehicle.has_reached_destination():
                        self.grid.remove_vehicle(pos, vehicle)
                        continue
                    
                    next_pos = vehicle.get_next_position()
                    turn_type = vehicle.get_turn_type()
                    
                    # Determine if the vehicle's direction aligns with the green light
                    is_horizontal_direction = direction in [self.grid.EAST, self.grid.WEST]
                    is_green_direction = (is_horizontal_direction and light.is_green(Direction.HORIZONTAL)) or \
                                      (not is_horizontal_direction and light.is_green(Direction.VERTICAL))
                    
                    # Check if vehicle can move based on traffic rules
                    can_move = False
                    
                    if turn_type == "right":
                        # Right turns are always allowed
                        can_move = True
                    elif is_green_direction:
                        if turn_type in ["straight", "left"]:
                            # Only allow one vehicle per green direction per time step
                            if not moved_in_green:
                                can_move = True
                                moved_in_green = True
                    
                    if can_move:
                        self.grid.remove_vehicle(pos, vehicle)
                        vehicle.move()
                        self.grid.add_vehicle(vehicle.current_pos, vehicle)
    
    def update_vehicles_time(self):
        """Update time counter for all vehicles."""
        for pos in self.grid.intersection_queues:
            for direction_queue in self.grid.intersection_queues[pos].values():
                for vehicle in direction_queue:
                    vehicle.update_time()

    def get_average_speed(self) -> float:
        """Calculate average speed across all vehicles."""
        total_speed = 0.0
        total_vehicles = 0
        
        for pos in self.grid.intersection_queues:
            for direction_queue in self.grid.intersection_queues[pos].values():
                for vehicle in direction_queue:
                    total_speed += vehicle.get_average_speed()
                    total_vehicles += 1
        
        if total_vehicles == 0:
            return 0.0
        return total_speed / total_vehicles
    
    def step(self):
        """Perform one simulation step."""
        self.generate_vehicles()
        self.move_vehicles()
        self.remove_vehicles()
        self.update_vehicles_time()
        self.controller.update(self.time_step)
        self.visualizer.update(self.time_step, self.get_average_speed())
        self.time_step += 1

def main():
    # Create and run simulation
    sim = Simulation(rows=5, cols=5)
    try:
        while True:
            sim.step()
    except KeyboardInterrupt:
        print("\nSimulation ended by user")

if __name__ == "__main__":
    main()
