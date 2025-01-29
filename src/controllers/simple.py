from src.controllers.base import BaseController

class SimpleController(BaseController):
    """Simple traffic light controller that switches lights at fixed intervals."""
    
    def __init__(self, grid, switch_interval: int = 5):
        """Initialize controller with a switch interval.
        
        Args:
            grid: The traffic grid
            switch_interval: Number of time steps between switches
        """
        super().__init__(grid)
        self.switch_interval = switch_interval
    
    def update(self, time_step: int):
        """Update traffic lights based on fixed time interval."""
        if time_step % self.switch_interval == 0:
            # Switch all traffic lights
            for pos in self.grid.traffic_lights:
                self.grid.traffic_lights[pos].switch()
