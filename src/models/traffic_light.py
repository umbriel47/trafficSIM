from .traffic_strategy import TrafficStrategy, RegularStrategy

class TrafficLight:
    """Represents a traffic light at an intersection."""
    def __init__(self, strategy: TrafficStrategy = None):
        self.strategy = strategy or RegularStrategy()
        self.current_cycle = 0
        self.ns_green = True  # True for N-S green, False for E-W green
    
    def update(self):
        """Update traffic light state."""
        self.current_cycle += 1
        if self.strategy.should_switch(self.current_cycle):
            self.current_cycle = 0
            self.ns_green = not self.ns_green
    
    def is_ns_green(self) -> bool:
        """Check if North-South direction is green."""
        return self.ns_green
    
    def is_ew_green(self) -> bool:
        """Check if East-West direction is green."""
        return not self.ns_green
    
    def get_state(self) -> dict:
        """Get the current state of the traffic light."""
        return {
            'ns_green': self.ns_green,
            'cycle': self.current_cycle
        }
    
    def set_strategy(self, strategy: TrafficStrategy):
        """Change the traffic light control strategy."""
        self.strategy = strategy
        self.current_cycle = 0
