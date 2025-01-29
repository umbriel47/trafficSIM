from typing import Tuple, List, Dict
import numpy as np
from .models.grid import Grid
from .models.vehicle import Vehicle

class Simulation:
    def __init__(self, grid_size: Tuple[int, int], num_vehicles: int):
        """Initialize the traffic simulation.
        
        Args:
            grid_size: Size of the grid (rows, cols)
            num_vehicles: Number of vehicles to simulate
        """
        self.grid_size = grid_size
        self.num_vehicles = num_vehicles
        self.time_step = 0
        self.paused = False
        
        # Initialize grid
        self.grid = [[Grid((i, j)) for j in range(grid_size[1])] 
                    for i in range(grid_size[0])]
        
        # Initialize vehicles
        self.vehicles = self._create_vehicles()
        
        # Place vehicles in their initial positions
        self._place_vehicles()
    
    def _create_vehicles(self) -> List[Vehicle]:
        """Create vehicles with random start and destination positions."""
        vehicles = []
        rows, cols = self.grid_size
        
        for _ in range(self.num_vehicles):
            # Generate random start and destination positions
            start = (np.random.randint(rows), np.random.randint(cols))
            while True:
                dest = (np.random.randint(rows), np.random.randint(cols))
                if dest != start:  # Ensure destination is different from start
                    break
            
            vehicle = Vehicle(start, dest, self.grid_size)
            vehicles.append(vehicle)
        
        return vehicles
    
    def _place_vehicles(self):
        """Place vehicles in their initial positions."""
        for vehicle in self.vehicles:
            pos = vehicle.current_pos
            next_pos = vehicle.get_next_position()
            if next_pos:
                direction = self._get_direction(pos, next_pos)
                self.grid[pos[0]][pos[1]].add_vehicle(vehicle, direction)
    
    def _get_direction(self, current: Tuple[int, int], next_pos: Tuple[int, int]) -> str:
        """Determine the direction from current position to next position."""
        rows, cols = self.grid_size
        row_diff = (next_pos[0] - current[0] + rows//2) % rows - rows//2
        col_diff = (next_pos[1] - current[1] + cols//2) % cols - cols//2
        
        if row_diff > 0:
            return 'S'
        elif row_diff < 0:
            return 'N'
        elif col_diff > 0:
            return 'E'
        else:
            return 'W'
    
    def step(self):
        """Advance the simulation by one time step."""
        if self.paused:
            return
            
        self.time_step += 1
        
        # Update all traffic lights
        for row in self.grid:
            for intersection in row:
                intersection.update()
        
        # Move vehicles
        for vehicle in self.vehicles:
            if not vehicle.has_reached_destination():
                current_pos = vehicle.current_pos
                next_pos = vehicle.get_next_position()
                
                if next_pos:
                    current_intersection = self.grid[current_pos[0]][current_pos[1]]
                    next_intersection = self.grid[next_pos[0]][next_pos[1]]
                    
                    # Check if vehicle can move based on traffic light
                    direction = vehicle.get_next_direction()
                    can_move = self._can_move(current_intersection, direction)
                    
                    if can_move:
                        # Remove from current intersection
                        current_intersection.remove_vehicle(direction)
                        
                        # Move vehicle
                        vehicle.move()
                        
                        # Add to next intersection's queue
                        next_direction = self._get_direction(next_pos, vehicle.get_next_position())
                        next_intersection.add_vehicle(vehicle, next_direction)
                    else:
                        # Update waiting time
                        vehicle.update_waiting_time(current_pos)
    
    def _can_move(self, intersection: Grid, direction: str) -> bool:
        """Check if a vehicle can move in the given direction."""
        if direction in ['N', 'S']:
            return intersection.traffic_light.is_ns_green()
        elif direction in ['E', 'W']:
            return intersection.traffic_light.is_ew_green()
        return False
    
    def get_state(self) -> Dict:
        """Get the current state of the simulation."""
        return {
            'time_step': self.time_step,
            'grid_size': self.grid_size,
            'num_vehicles': self.num_vehicles,
            'grid_state': [[intersection.get_state() for intersection in row]
                          for row in self.grid],
            'vehicle_states': [
                {
                    'position': vehicle.current_pos,
                    'destination': vehicle.destination,
                    'progress': vehicle.current_path_index / max(1, len(vehicle.path)),
                    'average_speed': vehicle.get_average_speed()
                }
                for vehicle in self.vehicles
            ]
        }
    
    def toggle_pause(self):
        """Toggle the pause state of the simulation."""
        self.paused = not self.paused
