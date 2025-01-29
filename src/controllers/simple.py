from typing import Dict, Tuple
from ..models.traffic_light import TrafficLight, Direction
from .scheduler import SimpleScheduler, DensityBasedScheduler, AdaptiveScheduler, IndependentScheduler

class SimpleController:
    """Simple traffic light controller."""
    
    def __init__(self, grid, switch_interval: int = 10):
        """Initialize controller with grid reference."""
        self.grid = grid
        self.switch_interval = switch_interval
        
        # Initialize available schedulers with descriptions
        self.schedulers = {
            'simple': SimpleScheduler(switch_interval),
            'density': DensityBasedScheduler(),
            'adaptive': AdaptiveScheduler(),
            'independent': IndependentScheduler()
        }
        
        # Scheduler descriptions
        self.scheduler_descriptions = {
            'simple': "Fixed-time scheduler that switches lights at regular intervals",
            'density': "Adjusts timing based on vehicle density in each direction",
            'adaptive': "Adapts timing based on traffic patterns and waiting times",
            'independent': "Controls each intersection independently based on local conditions"
        }
        
        # Set default scheduler to independent
        self.current_scheduler = self.schedulers['independent']
    
    def set_scheduler(self, scheduler_name: str) -> None:
        """Change the current scheduling strategy."""
        if scheduler_name.lower() in self.schedulers:
            print(f"Switching to {scheduler_name} scheduler")  # Debug print
            self.current_scheduler = self.schedulers[scheduler_name.lower()]
            
            # Reset any scheduler-specific state
            if hasattr(self.current_scheduler, 'current_green_time'):
                self.current_scheduler.current_green_time = {}
            if hasattr(self.current_scheduler, 'last_switch_time'):
                self.current_scheduler.last_switch_time = {}
            if hasattr(self.current_scheduler, 'intersection_timers'):
                self.current_scheduler.intersection_timers = {}
    
    def get_available_schedulers(self) -> Dict[str, str]:
        """Get list of available schedulers with their descriptions."""
        return self.scheduler_descriptions
    
    def get_current_scheduler(self) -> str:
        """Get name of current scheduler."""
        for name, scheduler in self.schedulers.items():
            if scheduler == self.current_scheduler:
                return name
        return 'unknown'
    
    def update(self, time_step: int) -> None:
        """Update traffic lights using current scheduler."""
        # Prepare grid state for scheduler
        grid_state = {}
        for pos in self.grid.intersection_queues:
            grid_state[pos] = {
                'light': self.grid.get_traffic_light(pos),
                'queues': self.grid.intersection_queues[pos]
            }
        
        # Update using current scheduler
        self.current_scheduler.schedule(time_step, grid_state)
