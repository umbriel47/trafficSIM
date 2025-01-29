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
        
    def _calculate_path(self) -> List[Tuple[int, int]]:
        """Calculate the shortest path from start to destination considering periodic boundaries."""
        rows, cols = self.grid_size
        G = nx.DiGraph()
        
        # Get start and destination positions
        start_row, start_col = self.current_pos
        dest_row, dest_col = self.destination
        
        # Calculate all possible distances considering periodic boundaries
        row_dists = [
            (dest_row - start_row),  # Normal
            (dest_row - start_row + rows),  # Through top boundary
            (dest_row - start_row - rows)   # Through bottom boundary
        ]
        col_dists = [
            (dest_col - start_col),  # Normal
            (dest_col - start_col + cols),  # Through right boundary
            (dest_col - start_col - cols)   # Through left boundary
        ]
        
        # Find the shortest combination of row and column distances
        min_total_dist = float('inf')
        best_row_dist = None
        best_col_dist = None
        
        for rd in row_dists:
            for cd in col_dists:
                total_dist = abs(rd) + abs(cd)
                if total_dist < min_total_dist:
                    min_total_dist = total_dist
                    best_row_dist = rd
                    best_col_dist = cd
        
        # Add edges based on the optimal direction
        for i in range(rows):
            for j in range(cols):
                # Add all possible edges for each node
                # Vertical edges (both up and down)
                G.add_edge((i, j), ((i + 1) % rows, j), weight=1)  # Down
                G.add_edge((i, j), ((i - 1) % rows, j), weight=1)  # Up
                
                # Horizontal edges (both left and right)
                G.add_edge((i, j), (i, (j + 1) % cols), weight=1)  # Right
                G.add_edge((i, j), (i, (j - 1) % cols), weight=1)  # Left
                
                # Add higher weights for edges in non-optimal directions
                if best_row_dist > 0:  # Need to go down
                    G.edges[((i, j), ((i - 1) % rows, j))]['weight'] = 2
                elif best_row_dist < 0:  # Need to go up
                    G.edges[((i, j), ((i + 1) % rows, j))]['weight'] = 2
                
                if best_col_dist > 0:  # Need to go right
                    G.edges[((i, j), (i, (j - 1) % cols))]['weight'] = 2
                elif best_col_dist < 0:  # Need to go left
                    G.edges[((i, j), (i, (j + 1) % cols))]['weight'] = 2
        
        # Calculate shortest path
        try:
            path = nx.shortest_path(G, self.current_pos, self.destination, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return [self.current_pos]
    
    def get_next_direction(self) -> str:
        """Get the next direction of movement as a string."""
        if self.current_path_index + 1 >= len(self.path):
            return None
            
        current = self.path[self.current_path_index]
        next_pos = self.path[self.current_path_index + 1]
        
        # Calculate differences considering periodic boundaries
        rows, cols = self.grid_size
        row_diff = (next_pos[0] - current[0] + rows//2) % rows - rows//2
        col_diff = (next_pos[1] - current[1] + cols//2) % cols - cols//2
        
        if row_diff > 0:
            return 'S'  # Moving South
        elif row_diff < 0:
            return 'N'  # Moving North
        elif col_diff > 0:
            return 'E'  # Moving East
        elif col_diff < 0:
            return 'W'  # Moving West
        return None
    
    def get_turn_type(self) -> str:
        """Determine the type of turn at the current intersection."""
        if len(self.path) < 3 or self.current_path_index >= len(self.path) - 2:
            return 'straight'
            
        prev_pos = self.path[self.current_path_index]
        curr_pos = self.path[self.current_path_index + 1]
        next_pos = self.path[self.current_path_index + 2]
        
        # Calculate movement vectors
        rows, cols = self.grid_size
        v1_row = (curr_pos[0] - prev_pos[0] + rows//2) % rows - rows//2
        v1_col = (curr_pos[1] - prev_pos[1] + cols//2) % cols - cols//2
        v2_row = (next_pos[0] - curr_pos[0] + rows//2) % rows - rows//2
        v2_col = (next_pos[1] - curr_pos[1] + cols//2) % cols - cols//2
        
        # Cross product to determine turn direction
        cross_product = v1_row * v2_col - v1_col * v2_row
        
        if cross_product == 0:
            return 'straight'
        elif cross_product > 0:
            return 'right'
        else:
            return 'left'
    
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
    
    def update_waiting_time(self, position: Tuple[int, int]):
        """Update the waiting time at a specific position."""
        if position not in self.waiting_times:
            self.waiting_times[position] = 0
        self.waiting_times[position] += 1
    
    def has_reached_destination(self) -> bool:
        """Check if vehicle has reached its destination."""
        return self.current_pos == self.destination
    
    def get_average_speed(self) -> float:
        """Calculate average speed (distance/time)."""
        total_time = sum(self.waiting_times.values()) + self.distance_traveled
        return self.distance_traveled / max(1, total_time)  # Avoid division by zero
