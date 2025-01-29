from abc import ABC, abstractmethod

class TrafficStrategy(ABC):
    """Abstract base class for traffic light control strategies."""
    
    @abstractmethod
    def should_switch(self, current_cycle: int) -> bool:
        """Determine if the traffic light should switch state."""
        pass

class RegularStrategy(TrafficStrategy):
    """Regular strategy with fixed-time alternation."""
    
    def __init__(self, cycle_length: int = 60):
        self.cycle_length = cycle_length
    
    def should_switch(self, current_cycle: int) -> bool:
        """Switch lights every cycle_length steps."""
        return current_cycle >= self.cycle_length
