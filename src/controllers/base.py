from abc import ABC, abstractmethod
from typing import Tuple
from src.models.grid import Grid

class BaseController(ABC):
    """Base class for traffic light controllers."""
    
    def __init__(self, grid: Grid):
        self.grid = grid
    
    @abstractmethod
    def update(self, time_step: int):
        """Update traffic light states based on current conditions.
        
        Args:
            time_step: Current simulation time step
        """
        pass
    
    def get_intersection_load(self, position: Tuple[int, int]) -> int:
        """Get the number of vehicles at an intersection."""
        return len(self.grid.intersections[position])
