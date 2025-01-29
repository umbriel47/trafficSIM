from typing import Tuple, List, Dict, Optional
from collections import deque
from .traffic_light import TrafficLight
from .vehicle import Vehicle

class Grid:
    """Represents a single intersection in the traffic grid."""
    def __init__(self, position: Tuple[int, int]):
        self.position = position
        # Queues for vehicles from each direction (N, E, S, W)
        self.queues = {
            'N': deque(),  # North queue
            'E': deque(),  # East queue
            'S': deque(),  # South queue
            'W': deque()   # West queue
        }
        # Initialize traffic light
        self.traffic_light = TrafficLight()
        # Track processed queues in current step
        self.processed_queues = set()
    
    def add_vehicle(self, vehicle: Vehicle, direction: str):
        """Add a vehicle to the specified direction queue."""
        self.queues[direction].append(vehicle)
    
    def remove_vehicle(self, direction: str) -> Optional[Vehicle]:
        """Remove and return the first vehicle from the specified direction queue."""
        if self.queues[direction]:
            return self.queues[direction].popleft()
        return None
    
    def get_queue_length(self, direction: str) -> int:
        """Get the length of the queue for the specified direction."""
        return len(self.queues[direction])
    
    def update(self):
        """Update the intersection state."""
        # Update traffic light
        self.traffic_light.update()
        
        # Reset processed queues for new step
        self.processed_queues.clear()
        
        # Process all directions
        for direction in ['N', 'E', 'S', 'W']:
            self._process_queue(direction)
    
    def _process_queue(self, direction: str):
        """Process vehicles in a specific direction queue."""
        if not self.queues[direction]:
            return
        
        # Process all right turns first
        processed_right_turns = []
        for i, vehicle in enumerate(self.queues[direction]):
            if vehicle.get_turn_type() == 'right':
                processed_right_turns.append(i)
                vehicle.move()
        
        # Remove right-turning vehicles from highest index to lowest
        for i in reversed(processed_right_turns):
            self.queues[direction].rotate(-i)
            self.remove_vehicle(direction)
            self.queues[direction].rotate(i)
        
        # Then process one straight/left turn if possible
        if self.queues[direction] and direction not in self.processed_queues:
            vehicle = self.queues[direction][0]
            turn_type = vehicle.get_turn_type()
            
            if turn_type in ['straight', 'left']:
                # Check if the direction has green light
                if direction in ['N', 'S']:
                    has_green = self.traffic_light.is_ns_green()
                else:  # ['E', 'W']
                    has_green = self.traffic_light.is_ew_green()
                
                if has_green:
                    self.remove_vehicle(direction)
                    vehicle.move()
                    # Mark this queue as processed for straight/left turns
                    self.processed_queues.add(direction)
    
    def get_state(self) -> Dict:
        """Get the current state of the intersection."""
        return {
            'position': self.position,
            'queue_lengths': {
                direction: len(queue) for direction, queue in self.queues.items()
            },
            'traffic_light': self.traffic_light.get_state(),
            'processed_queues': list(self.processed_queues)
        }
