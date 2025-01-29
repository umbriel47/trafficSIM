import numpy as np
from typing import Tuple
from src.models.grid import Grid
from src.models.vehicle import Vehicle
from src.controllers.simple import SimpleController
from src.visualization.visualizer import Visualizer
from src.models.traffic_light import Direction

class Simulation:
    def __init__(self, rows: int, cols: int, p1: float = 0.1):
        """Initialize simulation with grid dimensions and vehicle generation probability."""
        self.rows = rows
        self.cols = cols
        self.p1 = p1
        self.grid = Grid(rows, cols)
        self.time_step = 0
        self.visualizer = Visualizer(rows, cols, p1, self.grid)
        self.controller = SimpleController(self.grid)  # Pass grid to controller
        self.paused = False
        self.selected_intersection = None
        self.selected_vehicle = None
        self.active_vehicles = 0  # Track number of active vehicles
    
    def toggle_pause(self):
        """Toggle the simulation pause state."""
        self.paused = not self.paused
        if not self.paused:
            # Clear selections when resuming
            self.selected_intersection = None
            self.selected_vehicle = None
    
    def select_intersection(self, pos: Tuple[int, int]):
        """Select an intersection for detailed view."""
        if self.paused and pos[0] < self.rows and pos[1] < self.cols:
            self.selected_intersection = pos
            self.selected_vehicle = None  # Clear vehicle selection when selecting new intersection
    
    def select_vehicle(self, intersection: Tuple[int, int], queue_idx: int, vehicle_idx: int):
        """Select a vehicle from a specific queue at an intersection."""
        if not self.paused:
            return
            
        info = self.grid.get_intersection_info(intersection)
        if not info:
            return
            
        # Convert queue_idx to direction
        directions = list(info.keys())
        if queue_idx < len(directions):
            direction = directions[queue_idx]
            vehicles = info[direction]
            if vehicle_idx < len(vehicles):
                self.selected_vehicle = vehicles[vehicle_idx]['vehicle']
    
    def get_intersection_info(self, pos: Tuple[int, int]) -> dict:
        """Get detailed information about vehicles at an intersection."""
        if pos not in self.grid.intersection_queues:
            return None
        
        info = {}
        for direction, queue in self.grid.intersection_queues[pos].items():
            vehicles_info = []
            for vehicle in queue:
                vehicles_info.append({
                    'waiting_time': vehicle.get_waiting_time(),
                    'next_direction': vehicle.get_next_direction(),
                    'turn_type': vehicle.get_turn_type(),
                    'vehicle': vehicle  # Include vehicle object for selection
                })
            info[direction] = vehicles_info
        return info
    
    def generate_vehicles(self):
        """Generate new vehicles based on probability p1."""
        for i in range(self.grid.rows):
            for j in range(self.grid.cols):
                if np.random.random() < self.p1:
                    # Generate random destination different from start
                    while True:
                        dest_row = np.random.randint(0, self.grid.rows)
                        dest_col = np.random.randint(0, self.grid.cols)
                        if (dest_row, dest_col) != (i, j):
                            break
                    
                    # Create vehicle with random direction
                    vehicle = Vehicle(
                        start=(i, j),
                        destination=(dest_row, dest_col),
                        grid_size=(self.grid.rows, self.grid.cols)
                    )
                    
                    # Add vehicle to a random direction queue
                    directions = [self.grid.NORTH, self.grid.SOUTH, self.grid.EAST, self.grid.WEST]
                    direction = directions[np.random.randint(0, 4)]
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
        # Store moved vehicles to avoid moving them twice in the same step
        moved_vehicles = set()
        
        # Process each intersection
        for pos in self.grid.intersection_queues:
            # Get traffic light at this intersection
            light = self.grid.get_traffic_light(pos)
            
            # Track if we've moved a vehicle in the current green direction
            moved_in_green = False
            
            # First process right turns for all directions
            for direction in [self.grid.NORTH, self.grid.SOUTH, self.grid.EAST, self.grid.WEST]:
                queue = self.grid.get_direction_queue(pos, direction)
                vehicles_to_process = list(queue)  # Create a copy to avoid modification during iteration
                
                for vehicle in vehicles_to_process:
                    if vehicle in moved_vehicles or vehicle.has_reached_destination():
                        continue
                        
                    if vehicle.get_turn_type() == "right":
                        self.grid.remove_vehicle(pos, vehicle)
                        vehicle.move()
                        self.grid.add_vehicle(vehicle.current_pos, vehicle)
                        moved_vehicles.add(vehicle)
            
            # Then process straight and left turns for green direction
            is_horizontal_green = light.is_green(Direction.HORIZONTAL)
            green_directions = [self.grid.EAST, self.grid.WEST] if is_horizontal_green else [self.grid.NORTH, self.grid.SOUTH]
            
            for direction in green_directions:
                if moved_in_green:  # Only allow one vehicle per green direction
                    break
                    
                queue = self.grid.get_direction_queue(pos, direction)
                vehicles_to_process = list(queue)
                
                for vehicle in vehicles_to_process:
                    if vehicle in moved_vehicles or vehicle.has_reached_destination():
                        continue
                        
                    turn_type = vehicle.get_turn_type()
                    if turn_type in ["straight", "left"]:
                        self.grid.remove_vehicle(pos, vehicle)
                        vehicle.move()
                        self.grid.add_vehicle(vehicle.current_pos, vehicle)
                        moved_vehicles.add(vehicle)
                        moved_in_green = True
                        break
    
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
        if self.paused:
            return
            
        # 1. Update traffic lights through controller
        self.controller.update(self.time_step)
        
        # 2. Process vehicles at each intersection
        self.move_vehicles()
        
        # 3. Update waiting times for all vehicles
        self.update_vehicles_time()
        
        # 4. Generate new vehicles
        self.generate_vehicles()
        
        # 5. Remove vehicles that have reached their destination
        self.remove_vehicles()
        
        # Update active vehicles count
        self.active_vehicles = sum(
            len(direction_queue)
            for queues in self.grid.intersection_queues.values()
            for direction_queue in queues.values()
        )
        
        # Update visualization
        self.visualizer.update(
            self.time_step,
            self.get_average_speed(),
            self.active_vehicles,
            self.selected_intersection,
            self.selected_vehicle
        )
        
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
