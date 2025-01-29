from enum import Enum
from typing import List, Dict, Tuple, Optional
from collections import deque
import pygame
import numpy as np
import random

class Direction(Enum):
    """Enum for vehicle directions"""
    NORTH = 'N'
    SOUTH = 'S'
    EAST = 'E'
    WEST = 'W'

class Action(Enum):
    """Enum for vehicle actions"""
    STRAIGHT = 'straight'
    LEFT = 'left'
    RIGHT = 'right'

class Vehicle:
    """
    A class representing vehicles in the traffic simulation.
    Each vehicle has a unique ID and can perform different actions (straight, left, right).
    """
    def __init__(self, vehicle_id: int, action: Action):
        self.vehicle_id = vehicle_id
        self.action = action
        self.current_position = None  # (row, col) tuple
        self.incoming_direction = None
        self.trajectory = []  # List of positions the vehicle has visited
        
    def get_next_position(self) -> Tuple[Tuple[int, int], Direction]:
        """Calculate next position and incoming direction based on current action"""
        row, col = self.current_position
        
        # First determine exit direction based on incoming direction and action
        exit_direction = None
        if self.action == Action.STRAIGHT:
            if self.incoming_direction == Direction.NORTH:
                exit_direction = Direction.SOUTH
            elif self.incoming_direction == Direction.SOUTH:
                exit_direction = Direction.NORTH
            elif self.incoming_direction == Direction.EAST:
                exit_direction = Direction.WEST
            else:  # WEST
                exit_direction = Direction.EAST
        elif self.action == Action.LEFT:
            if self.incoming_direction == Direction.NORTH:
                exit_direction = Direction.EAST
            elif self.incoming_direction == Direction.SOUTH:
                exit_direction = Direction.WEST
            elif self.incoming_direction == Direction.EAST:
                exit_direction = Direction.SOUTH
            else:  # WEST
                exit_direction = Direction.NORTH
        else:  # RIGHT
            if self.incoming_direction == Direction.NORTH:
                exit_direction = Direction.WEST
            elif self.incoming_direction == Direction.SOUTH:
                exit_direction = Direction.EAST
            elif self.incoming_direction == Direction.EAST:
                exit_direction = Direction.NORTH
            else:  # WEST
                exit_direction = Direction.SOUTH
        
        # Calculate next position based on exit direction
        next_row, next_col = row, col
        next_incoming = None
        if exit_direction == Direction.NORTH:
            next_row -= 1
            next_incoming = Direction.SOUTH
        elif exit_direction == Direction.SOUTH:
            next_row += 1
            next_incoming = Direction.NORTH
        elif exit_direction == Direction.EAST:
            next_col += 1
            next_incoming = Direction.WEST
        else:  # WEST
            next_col -= 1
            next_incoming = Direction.EAST
            
        return (next_row, next_col), next_incoming
        
    def update_position(self, position: Tuple[int, int], incoming_direction: Direction):
        """Update position and track trajectory"""
        self.current_position = position
        self.incoming_direction = incoming_direction
        self.trajectory.append(position)
        
    def __str__(self):
        return f"Vehicle {self.vehicle_id} (Action: {self.action.value})"

class Town:
    """
    A class representing the town grid layout with traffic intersections.
    The town is represented as an NxM matrix where each node is an intersection
    with four directional queues for vehicles.
    """
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        # Initialize the grid of intersections
        # Each intersection has 4 queues (E, S, W, N) for vehicles
        self.grid = []
        for _ in range(rows):
            row = []
            for _ in range(cols):
                intersection = {
                    Direction.EAST: deque(),   # Queue for vehicles from East
                    Direction.SOUTH: deque(),  # Queue for vehicles from South
                    Direction.WEST: deque(),   # Queue for vehicles from West
                    Direction.NORTH: deque()   # Queue for vehicles from North
                }
                row.append(intersection)
            self.grid.append(row)

    def add_vehicle(self, vehicle: Vehicle, position: tuple, incoming_direction: Direction):
        """
        Add a vehicle to a specific intersection from a given direction
        
        Args:
            vehicle: The vehicle to add
            position: Tuple of (row, col) indicating the intersection
            incoming_direction: The direction from which the vehicle is approaching
        """
        row, col = position
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col][incoming_direction].append(vehicle)
            vehicle.update_position(position, incoming_direction)
        else:
            raise ValueError("Invalid position in town grid")

    def remove_vehicle(self, vehicle: Vehicle) -> None:
        """Remove a vehicle from its current intersection"""
        if vehicle.current_position:
            row, col = vehicle.current_position
            intersection = self.grid[row][col]
            for direction_queue in intersection.values():
                if vehicle in direction_queue:
                    direction_queue.remove(vehicle)
                    break
    
    def is_valid_position(self, position: Tuple[int, int]) -> bool:
        """Check if a position is within town boundaries"""
        row, col = position
        return 0 <= row < self.rows and 0 <= col < self.cols
    
    def move_vehicle(self, vehicle: Vehicle) -> bool:
        """
        Move a vehicle according to its action. Returns True if vehicle remains in town,
        False if it moves out of bounds.
        """
        next_position, next_incoming = vehicle.get_next_position()
        
        # Check if next position is valid
        if not self.is_valid_position(next_position):
            self.remove_vehicle(vehicle)
            vehicle.current_position = None
            vehicle.incoming_direction = None
            return False
            
        # Move vehicle to next position
        self.remove_vehicle(vehicle)
        self.add_vehicle(vehicle, next_position, next_incoming)
        
        # Assign random new action
        vehicle.action = random.choice(list(Action))
        return True
        
    def get_total_vehicles(self) -> int:
        """Return the total number of vehicles in the town"""
        total = 0
        for row in self.grid:
            for intersection in row:
                for direction_queue in intersection.values():
                    total += len(direction_queue)
        return total
    
    def get_node_density(self) -> np.ndarray:
        """Calculate the density of vehicles at each node"""
        total_vehicles = self.get_total_vehicles()
        if total_vehicles == 0:
            return np.zeros((self.rows, self.cols))
            
        density = np.zeros((self.rows, self.cols))
        for i in range(self.rows):
            for j in range(self.cols):
                node_vehicles = sum(len(queue) for queue in self.grid[i][j].values())
                density[i][j] = node_vehicles / total_vehicles
        return density
    
    def get_vehicle_queue_info(self, vehicle: Vehicle) -> str:
        """Get information about the vehicle's position in its current queue"""
        if not vehicle.current_position:
            return "Not in town"
            
        row, col = vehicle.current_position
        intersection = self.grid[row][col]
        
        for direction, queue in intersection.items():
            if vehicle in queue:
                position = list(queue).index(vehicle)
                return f"Queue: {direction.value} (Position: {position + 1}/{len(queue)})"
        return "Not found in any queue"

    def visualize(self, window_size: Tuple[int, int] = (1200, 600), 
                 time_step: int = 0, total_vehicles: int = 0, vehicle: Optional[Vehicle] = None):
        """
        Visualize the town grid with vehicle density overlay using pygame
        
        Args:
            window_size: Tuple of (width, height) for the window size
            time_step: Current simulation time step
            total_vehicles: Total number of vehicles in simulation
            vehicle: The vehicle to track and display information for
        """
        # Get the existing display surface
        screen = pygame.display.get_surface()
        if screen is None:
            return
            
        # Calculate panel dimensions
        left_panel_width = window_size[0] // 2
        right_panel_width = window_size[0] - left_panel_width
        height = window_size[1]
        
        # Calculate grid cell size
        cell_size = min(
            (left_panel_width - 40) // self.cols,  # -40 for padding
            (height - 40) // self.rows
        )
        
        # Calculate grid offset to center it in the left panel
        grid_width = cell_size * self.cols
        grid_height = cell_size * self.rows
        offset_x = (left_panel_width - grid_width) // 2
        offset_y = (height - grid_height) // 2
        
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            # Clear the screen
            screen.fill((255, 255, 255))  # White background
            
            # Draw separation line between panels
            pygame.draw.line(screen, (0, 0, 0), (left_panel_width, 0), 
                           (left_panel_width, height))
            
            # Get current density
            density = self.get_node_density()
            
            # Draw grid and density overlay
            for i in range(self.rows):
                for j in range(self.cols):
                    # Calculate cell position
                    x = offset_x + j * cell_size
                    y = offset_y + i * cell_size
                    
                    # Draw cell background with density-based color
                    density_value = density[i][j]
                    color = (255, int(255 * (1 - density_value)), int(255 * (1 - density_value)))
                    pygame.draw.rect(screen, color, 
                                  (x, y, cell_size, cell_size))
                    
                    # Draw cell border
                    pygame.draw.rect(screen, (0, 0, 0), 
                                  (x, y, cell_size, cell_size), 1)
            
            # Draw vehicle trajectory if vehicle is provided
            if vehicle and len(vehicle.trajectory) > 0:
                for i in range(len(vehicle.trajectory) - 1):
                    start_row, start_col = vehicle.trajectory[i]
                    end_row, end_col = vehicle.trajectory[i + 1]
                    
                    start_x = offset_x + start_col * cell_size + cell_size // 2
                    start_y = offset_y + start_row * cell_size + cell_size // 2
                    end_x = offset_x + end_col * cell_size + cell_size // 2
                    end_y = offset_y + end_row * cell_size + cell_size // 2
                    
                    pygame.draw.line(screen, (0, 0, 255), (start_x, start_y), 
                                   (end_x, end_y), 2)
                    
                # Draw current position with a larger dot
                if vehicle.current_position:
                    current_row, current_col = vehicle.current_position
                    center_x = offset_x + current_col * cell_size + cell_size // 2
                    center_y = offset_y + current_row * cell_size + cell_size // 2
                    pygame.draw.circle(screen, (255, 0, 0), (center_x, center_y), 6)
            
            # Right panel information
            font = pygame.font.Font(None, 36)
            y_offset = 50
            
            # Display simulation information
            info_texts = [
                f"Time Step: {time_step}",
                f"Town Size: {self.rows}x{self.cols}",
                f"Running Vehicles: {total_vehicles}"
            ]
            
            # Add vehicle information if available
            if vehicle:
                info_texts.extend([
                    "",
                    "Vehicle Information:",
                    f"ID: {vehicle.vehicle_id}",
                    f"Position: {vehicle.current_position}",
                    f"Direction: {vehicle.incoming_direction.value if vehicle.incoming_direction else 'N/A'}",
                    f"Next Action: {vehicle.action.value}",
                    self.get_vehicle_queue_info(vehicle)
                ])
            
            for text in info_texts:
                text_surface = font.render(text, True, (0, 0, 0))
                text_rect = text_surface.get_rect(
                    center=(left_panel_width + right_panel_width//2, y_offset))
                screen.blit(text_surface, text_rect)
                y_offset += 40
            
            pygame.display.flip()
            clock.tick(30)  # 30 FPS
            
        pygame.quit()

    def __str__(self):
        return f"Town Grid ({self.rows}x{self.cols})"
