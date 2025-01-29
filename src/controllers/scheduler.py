from abc import ABC, abstractmethod
from typing import Dict, Tuple
from ..models.traffic_light import TrafficLight, Direction

class TrafficScheduler(ABC):
    """Base class for traffic light scheduling strategies."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def schedule(self, time_step: int, grid_state: Dict[Tuple[int, int], Dict]) -> None:
        """Update traffic lights based on current grid state."""
        pass

class SimpleScheduler(TrafficScheduler):
    """Simple time-based scheduler that alternates lights every fixed interval."""
    
    def __init__(self, interval: int = 10):
        super().__init__(
            name="Simple Timer",
            description="Alternates lights every fixed interval"
        )
        self.interval = interval
    
    def schedule(self, time_step: int, grid_state: Dict[Tuple[int, int], Dict]) -> None:
        """Update traffic lights based on fixed time intervals."""
        is_horizontal = (time_step // self.interval) % 2 == 0
        for pos, state in grid_state.items():
            light = state.get('light')
            if light:
                light.set_state(Direction.HORIZONTAL if is_horizontal else Direction.VERTICAL)

class DensityBasedScheduler(TrafficScheduler):
    """Scheduler that considers vehicle density in each direction."""
    
    def __init__(self, min_green_time: int = 5, max_green_time: int = 20):
        super().__init__(
            name="Density Based",
            description="Adjusts timing based on traffic density"
        )
        self.min_green_time = min_green_time
        self.max_green_time = max_green_time
        self.current_green_time = {}  # Track how long each light has been green
    
    def schedule(self, time_step: int, grid_state: Dict[Tuple[int, int], Dict]) -> None:
        """Update traffic lights based on vehicle density."""
        for pos, state in grid_state.items():
            light = state.get('light')
            if not light:
                continue
                
            # Initialize tracking for new lights
            if pos not in self.current_green_time:
                self.current_green_time[pos] = 0
                
            # Get queue lengths in each direction
            queues = state.get('queues', {})
            h_count = len(queues.get('East', [])) + len(queues.get('West', []))
            v_count = len(queues.get('North', [])) + len(queues.get('South', []))
            
            # Current state
            is_horizontal = light.is_green(Direction.HORIZONTAL)
            self.current_green_time[pos] += 1
            
            # Determine if we should switch
            should_switch = False
            
            # Must switch if exceeded max green time
            if self.current_green_time[pos] >= self.max_green_time:
                should_switch = True
            # Can switch if minimum time met and other direction has more traffic
            elif self.current_green_time[pos] >= self.min_green_time:
                if is_horizontal and v_count > h_count * 1.5:  # 50% more traffic
                    should_switch = True
                elif not is_horizontal and h_count > v_count * 1.5:
                    should_switch = True
            
            # Switch if conditions met
            if should_switch:
                light.set_state(Direction.VERTICAL if is_horizontal else Direction.HORIZONTAL)
                self.current_green_time[pos] = 0

class AdaptiveScheduler(TrafficScheduler):
    """Advanced scheduler that adapts to traffic patterns and waiting times."""
    
    def __init__(self, min_green_time: int = 5, max_green_time: int = 30):
        super().__init__(
            name="Adaptive",
            description="Adapts to traffic patterns and waiting times"
        )
        self.min_green_time = min_green_time
        self.max_green_time = max_green_time
        self.current_green_time = {}
        self.last_switch_time = {}
    
    def schedule(self, time_step: int, grid_state: Dict[Tuple[int, int], Dict]) -> None:
        """Update traffic lights using adaptive strategy."""
        for pos, state in grid_state.items():
            light = state.get('light')
            if not light:
                continue
                
            # Initialize tracking for new lights
            if pos not in self.current_green_time:
                self.current_green_time[pos] = 0
                self.last_switch_time[pos] = 0
                
            # Get queue information
            queues = state.get('queues', {})
            h_queues = queues.get('East', []) + queues.get('West', [])
            v_queues = queues.get('North', []) + queues.get('South', [])
            
            # Calculate waiting times and queue lengths
            h_wait = sum(v.get_waiting_time() for v in h_queues) if h_queues else 0
            v_wait = sum(v.get_waiting_time() for v in v_queues) if v_queues else 0
            h_count = len(h_queues)
            v_count = len(v_queues)
            
            # Current state
            is_horizontal = light.is_green(Direction.HORIZONTAL)
            self.current_green_time[pos] += 1
            
            # Calculate priority scores
            h_score = h_wait * 1.5 + h_count  # Weight waiting time more
            v_score = v_wait * 1.5 + v_count
            
            # Determine if we should switch
            should_switch = False
            
            # Must switch if exceeded max green time
            if self.current_green_time[pos] >= self.max_green_time:
                should_switch = True
            # Can switch if minimum time met and other direction has higher score
            elif self.current_green_time[pos] >= self.min_green_time:
                if is_horizontal and v_score > h_score * 1.3:  # 30% higher score
                    should_switch = True
                elif not is_horizontal and h_score > v_score * 1.3:
                    should_switch = True
            
            # Switch if conditions met
            if should_switch:
                light.set_state(Direction.VERTICAL if is_horizontal else Direction.HORIZONTAL)
                self.current_green_time[pos] = 0
                self.last_switch_time[pos] = time_step

class IndependentScheduler(TrafficScheduler):
    """Traffic light scheduler that controls each intersection independently."""
    
    def __init__(self):
        """Initialize the independent scheduler."""
        super().__init__(
            name="Independent",
            description="Controls each intersection independently based on local traffic conditions"
        )
        self.intersection_timers = {}  # Track time for each intersection
        self.min_green_time = 5  # Minimum green light duration
        self.max_green_time = 15  # Maximum green light duration
    
    def schedule(self, time_step: int, grid_state: dict) -> None:
        """Schedule traffic lights independently for each intersection.
        
        Args:
            time_step: Current simulation time step
            grid_state: Dictionary containing traffic light and queue information for each intersection
        """
        for pos, state in grid_state.items():
            if pos not in self.intersection_timers:
                self.intersection_timers[pos] = 0
            
            # Get queue lengths for each direction
            horizontal_count = len(state['queues']['East']) + len(state['queues']['West'])
            vertical_count = len(state['queues']['North']) + len(state['queues']['South'])
            
            # Get current light state
            light = state['light']
            current_direction = light.get_state()
            
            # Calculate optimal green time based on queue lengths
            if current_direction == Direction.HORIZONTAL:
                ratio = horizontal_count / (vertical_count + 1)  # Avoid division by zero
                green_time = min(max(self.min_green_time, int(ratio * 10)), self.max_green_time)
            else:
                ratio = vertical_count / (horizontal_count + 1)  # Avoid division by zero
                green_time = min(max(self.min_green_time, int(ratio * 10)), self.max_green_time)
            
            # Switch light if timer exceeds green time
            self.intersection_timers[pos] += 1
            if self.intersection_timers[pos] >= green_time:
                light.switch()
                self.intersection_timers[pos] = 0
