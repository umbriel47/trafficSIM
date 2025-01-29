from enum import Enum

class Direction(Enum):
    HORIZONTAL = "horizontal"  # Left-right direction
    VERTICAL = "vertical"      # Up-down direction

class TrafficLight:
    def __init__(self):
        """Initialize traffic light with horizontal direction being green."""
        self.green_direction = Direction.HORIZONTAL
    
    def is_green(self, direction: Direction) -> bool:
        """Check if the given direction has green light."""
        return self.green_direction == direction
    
    def switch(self):
        """Switch the traffic light state."""
        self.green_direction = (
            Direction.VERTICAL if self.green_direction == Direction.HORIZONTAL 
            else Direction.HORIZONTAL
        )
    
    def get_state(self) -> Direction:
        """Get current green direction."""
        return self.green_direction
