import numpy as np
from typing import Tuple, List, Dict
from collections import deque
from .traffic_light import TrafficLight, Direction
from .vehicle import Vehicle

class Grid:
    # Direction constants
    NORTH = (0, -1)  # Moving up (decreasing row)
    SOUTH = (0, 1)   # Moving down (increasing row)
    EAST = (1, 0)    # Moving right (increasing col)
    WEST = (-1, 0)   # Moving left (decreasing col)

    def __init__(self, rows: int, cols: int):
        """Initialize the grid with given dimensions.
        
        Args:
            rows (int): Number of rows in the grid
            cols (int): Number of columns in the grid
        """
        self.rows = rows
        self.cols = cols
        self.traffic_lights = {}  # Dict to store traffic lights at each intersection
        
        # Dictionary to store vehicle queues for each direction at each intersection
        self.intersection_queues = {}
        
        # Initialize intersections and traffic lights
        for i in range(rows):
            for j in range(cols):
                self.traffic_lights[(i, j)] = TrafficLight()
                # Initialize queues for each direction
                self.intersection_queues[(i, j)] = {
                    self.NORTH: deque(),  # Queue for vehicles coming from north
                    self.SOUTH: deque(),  # Queue for vehicles coming from south
                    self.EAST: deque(),   # Queue for vehicles coming from east
                    self.WEST: deque()    # Queue for vehicles coming from west
                }
    
    def get_next_position(self, current: Tuple[int, int], direction: Tuple[int, int]) -> Tuple[int, int]:
        """Get next position considering periodic boundary conditions."""
        next_row = (current[0] + direction[0]) % self.rows
        next_col = (current[1] + direction[1]) % self.cols
        return (next_row, next_col)
    
    def get_direction_from_positions(self, current: Tuple[int, int], next_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Get the direction vector from current position to next position."""
        # Calculate shortest path considering periodic boundaries
        dx = next_pos[1] - current[1]
        dy = next_pos[0] - current[0]
        
        # Adjust for periodic boundaries
        if dx > self.cols//2:
            dx -= self.cols
        elif dx < -self.cols//2:
            dx += self.cols
            
        if dy > self.rows//2:
            dy -= self.rows
        elif dy < -self.rows//2:
            dy += self.rows
        
        # Determine primary direction of movement
        if abs(dx) > abs(dy):
            return (1, 0) if dx > 0 else (-1, 0)
        else:
            return (0, 1) if dy > 0 else (0, -1)
    
    def add_vehicle(self, position: Tuple[int, int], vehicle: Vehicle):
        """Add a vehicle to the appropriate queue at the intersection."""
        if not vehicle.has_reached_destination():
            next_pos = vehicle.get_next_position()
            direction = self.get_direction_from_positions(position, next_pos)
            self.intersection_queues[position][direction].append(vehicle)
    
    def remove_vehicle(self, position: Tuple[int, int], vehicle: Vehicle):
        """Remove a vehicle from its queue at the intersection."""
        if not vehicle.has_reached_destination():
            next_pos = vehicle.get_next_position()
            direction = self.get_direction_from_positions(position, next_pos)
            queue = self.intersection_queues[position][direction]
            if vehicle in queue:
                queue.remove(vehicle)
    
    def get_traffic_density(self) -> np.ndarray:
        """Return the traffic density matrix."""
        density = np.zeros((self.rows, self.cols))
        for pos, queues in self.intersection_queues.items():
            density[pos[0], pos[1]] = sum(len(q) for q in queues.values())
        return density
    
    def get_traffic_light(self, position: Tuple[int, int]) -> TrafficLight:
        """Get the traffic light at the specified intersection."""
        return self.traffic_lights[position]
    
    def get_vehicles_at_intersection(self, position: Tuple[int, int]) -> List[Vehicle]:
        """Get all vehicles at an intersection."""
        vehicles = []
        for queue in self.intersection_queues[position].values():
            vehicles.extend(list(queue))
        return vehicles
    
    def get_direction_queue(self, position: Tuple[int, int], direction: Tuple[int, int]) -> deque:
        """Get the queue for a specific direction at an intersection."""
        return self.intersection_queues[position][direction]
    
    def get_intersection_info(self, pos: Tuple[int, int]) -> dict:
        """Get detailed information about vehicles at an intersection.
        
        Args:
            pos: Tuple of (row, col) coordinates
            
        Returns:
            dict: Information about vehicles in each direction queue
        """
        if pos not in self.intersection_queues:
            return None
        
        info = {}
        for direction, queue in self.intersection_queues[pos].items():
            vehicles_info = []
            for vehicle in queue:
                vehicles_info.append({
                    'waiting_time': vehicle.get_waiting_time(),
                    'next_direction': vehicle.get_next_direction(),
                    'turn_type': vehicle.get_turn_type(),
                    'vehicle': vehicle
                })
            info[direction] = vehicles_info
        return info
    
    def get_total_vehicles(self) -> np.ndarray:
        """Get the total number of vehicles at each intersection.
        
        Returns:
            np.ndarray: Matrix of vehicle counts
        """
        density = np.zeros((self.rows, self.cols))
        for pos, queues in self.intersection_queues.items():
            density[pos[0], pos[1]] = sum(len(q) for q in queues.values())
        return density
