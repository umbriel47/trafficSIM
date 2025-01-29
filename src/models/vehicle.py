from typing import Tuple, List
import networkx as nx
import numpy as np

class Vehicle:
    def __init__(self, start: Tuple[int, int], destination: Tuple[int, int], grid_size: Tuple[int, int]):
        """Initialize a vehicle with start and destination positions.
        
        Args:
            start: Starting position (row, col)
            destination: Destination position (row, col)
            grid_size: Size of the grid (rows, cols)
        """
        self.current_pos = start
        self.destination = destination
        self.grid_size = grid_size
        self.path = self._calculate_path()
        self.current_path_index = 0
        self.steps_taken = 0
        self.distance_traveled = 0
        self.waiting_times = {pos: 0 for pos in self.path}  # Track waiting time at each intersection
        self.path_history = []  # Track actual path taken with waiting times
        self.last_move_time = 0  # Track when the vehicle last moved
    
    def _calculate_path(self) -> List[Tuple[int, int]]:
        """Calculate the shortest path from start to destination."""
        # Create a graph representing the grid
        G = nx.grid_2d_graph(self.grid_size[0], self.grid_size[1], periodic=True)
        
        # Find shortest path using NetworkX
        path = nx.shortest_path(G, self.current_pos, self.destination)
        return path
    
    def get_next_position(self) -> Tuple[int, int]:
        """Get the next position in the path."""
        if self.current_path_index + 1 < len(self.path):
            return self.path[self.current_path_index + 1]
        return self.current_pos
    
    def move(self):
        """Move to the next position in the path."""
        if self.current_path_index + 1 < len(self.path):
            self.current_path_index += 1
            self.current_pos = self.path[self.current_path_index]
            self.distance_traveled += 1
            self.last_move_time = self.steps_taken
    
    def update_time(self):
        """Update the time counter and waiting times."""
        self.steps_taken += 1
        self.waiting_times[self.current_pos] += 1
        if len(self.path_history) == 0 or self.path_history[-1][0] != self.current_pos:
            self.path_history.append((self.current_pos, 0))
        self.path_history[-1] = (self.current_pos, self.waiting_times[self.current_pos])
    
    def get_average_speed(self) -> float:
        """Calculate average speed (distance/time)."""
        if self.steps_taken == 0:
            return 0.0
        return self.distance_traveled / self.steps_taken
    
    def has_reached_destination(self) -> bool:
        """Check if vehicle has reached its destination."""
        return self.current_pos == self.destination
    
    def get_turn_type(self) -> str:
        """Determine the type of turn at the current intersection."""
        if self.current_path_index + 1 >= len(self.path):
            return "straight"
        
        # Get current and next two positions
        current = self.current_pos
        next_pos = self.path[self.current_path_index + 1]
        
        # Calculate direction vectors considering periodic boundary conditions
        dx = (next_pos[1] - current[1] + self.grid_size[1]//2) % self.grid_size[1] - self.grid_size[1]//2
        dy = (next_pos[0] - current[0] + self.grid_size[0]//2) % self.grid_size[0] - self.grid_size[0]//2
        
        # If there's a next-next position, use it to determine turn type
        if self.current_path_index + 2 < len(self.path):
            next_next = self.path[self.current_path_index + 2]
            dx_next = (next_next[1] - next_pos[1] + self.grid_size[1]//2) % self.grid_size[1] - self.grid_size[1]//2
            dy_next = (next_next[0] - next_pos[0] + self.grid_size[0]//2) % self.grid_size[0] - self.grid_size[0]//2
            
            # Determine turn type based on direction change
            if dx == 0 and dx_next != 0:  # Moving vertically then horizontally
                return "right" if (dy > 0 and dx_next > 0) or (dy < 0 and dx_next < 0) else "left"
            elif dy == 0 and dy_next != 0:  # Moving horizontally then vertically
                return "right" if (dx > 0 and dy_next < 0) or (dx < 0 and dy_next > 0) else "left"
        
        return "straight"

    def get_next_direction(self) -> str:
        """Get the next direction of movement as a string."""
        if self.current_path_index + 1 >= len(self.path):
            return "Destination"
        
        current = self.current_pos
        next_pos = self.path[self.current_path_index + 1]
        
        dx = (next_pos[1] - current[1] + self.grid_size[1]//2) % self.grid_size[1] - self.grid_size[1]//2
        dy = (next_pos[0] - current[0] + self.grid_size[0]//2) % self.grid_size[0] - self.grid_size[0]//2
        
        if dx > 0:
            return "East"
        elif dx < 0:
            return "West"
        elif dy > 0:
            return "South"
        else:
            return "North"
    
    def get_waiting_time(self) -> int:
        """Get the current waiting time at the current intersection."""
        return self.waiting_times[self.current_pos]
    
    def get_path_with_delays(self) -> List[Tuple[Tuple[int, int], int]]:
        """Get the path history with waiting times for each position."""
        return self.path_history
