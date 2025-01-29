from enum import Enum, auto

class Direction(Enum):
    """Enum for traffic light directions."""
    HORIZONTAL = auto()
    VERTICAL = auto()

class TrafficLight:
    """Traffic light that controls traffic flow at intersections."""
    
    def __init__(self):
        """Initialize traffic light with horizontal direction as default green."""
        self._green_direction = Direction.HORIZONTAL
    
    def switch(self):
        """Switch the traffic light between horizontal and vertical."""
        if self._green_direction == Direction.HORIZONTAL:
            self._green_direction = Direction.VERTICAL
        else:
            self._green_direction = Direction.HORIZONTAL
    
    def is_green(self, direction: Direction) -> bool:
        """Check if the given direction has a green light.
        
        Args:
            direction: Direction to check
            
        Returns:
            bool: True if the direction has a green light
        """
        return self._green_direction == direction
    
    def get_state(self) -> Direction:
        """Get the current green direction.
        
        Returns:
            Direction: Current green direction
        """
        return self._green_direction
    
    def update(self, controller) -> None:
        """Update the traffic light state based on the controller's decision.
        
        Args:
            controller: Traffic light controller
        """
        # The controller will call switch() when needed
        pass
