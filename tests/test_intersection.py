import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from src.models.grid import Grid
from src.models.vehicle import Vehicle
from src.models.traffic_strategy import RegularStrategy

class MockVehicle(Vehicle):
    """Mock vehicle class for testing."""
    def __init__(self, turn_type: str, next_direction: str):
        self.mock_turn_type = turn_type
        self.mock_next_direction = next_direction
        super().__init__((0, 0), (1, 1), (10, 10))  # Dummy positions
    
    def get_turn_type(self) -> str:
        return self.mock_turn_type
    
    def get_next_direction(self) -> str:
        return self.mock_next_direction
    
    def move(self):
        pass  # Do nothing for testing

class TestIntersection(unittest.TestCase):
    def setUp(self):
        self.grid = Grid((0, 0))
        # Set a shorter cycle for testing
        self.grid.traffic_light.set_strategy(RegularStrategy(cycle_length=4))
    
    def test_right_turn_always_allowed(self):
        """Test that right turns are allowed regardless of traffic light state."""
        # Add right-turning vehicles to all directions
        right_turns = {
            'N': MockVehicle('right', 'E'),
            'E': MockVehicle('right', 'S'),
            'S': MockVehicle('right', 'W'),
            'W': MockVehicle('right', 'N')
        }
        
        for direction, vehicle in right_turns.items():
            self.grid.add_vehicle(vehicle, direction)
        
        # Process intersection with NS green
        self.grid.traffic_light.ns_green = True
        self.grid.update()
        
        # All queues should be empty as right turns are always allowed
        for direction in ['N', 'E', 'S', 'W']:
            self.assertEqual(self.grid.get_queue_length(direction), 0,
                           f"Right turn from {direction} should be allowed with NS green")
    
    def test_straight_and_left_turn_rules(self):
        """Test that straight and left turns follow traffic light rules."""
        # Add straight-going vehicles to all directions
        straight_vehicles = {
            'N': MockVehicle('straight', 'N'),
            'E': MockVehicle('straight', 'E'),
            'S': MockVehicle('straight', 'S'),
            'W': MockVehicle('straight', 'W')
        }
        
        for direction, vehicle in straight_vehicles.items():
            self.grid.add_vehicle(vehicle, direction)
        
        # Test with NS green
        self.grid.traffic_light.ns_green = True
        self.grid.update()
        
        # NS vehicles should have moved
        self.assertEqual(self.grid.get_queue_length('N'), 0)
        self.assertEqual(self.grid.get_queue_length('S'), 0)
        # EW vehicles should still be waiting
        self.assertEqual(self.grid.get_queue_length('E'), 1)
        self.assertEqual(self.grid.get_queue_length('W'), 1)
    
    def test_one_vehicle_per_queue_per_step(self):
        """Test that only one vehicle per queue can move in each time step."""
        # Add two straight-going vehicles to each NS direction
        for _ in range(2):
            self.grid.add_vehicle(MockVehicle('straight', 'N'), 'N')
            self.grid.add_vehicle(MockVehicle('straight', 'S'), 'S')
        
        # Set NS green and update
        self.grid.traffic_light.ns_green = True
        self.grid.update()
        
        # Each queue should have processed exactly one vehicle
        self.assertEqual(self.grid.get_queue_length('N'), 1)
        self.assertEqual(self.grid.get_queue_length('S'), 1)
    
    def test_traffic_light_cycle(self):
        """Test that traffic light cycles correctly affect vehicle movement."""
        # Add straight-going vehicles
        self.grid.add_vehicle(MockVehicle('straight', 'N'), 'N')
        self.grid.add_vehicle(MockVehicle('straight', 'E'), 'E')
        
        # Initial state (NS green)
        self.grid.traffic_light.ns_green = True
        self.grid.update()
        self.assertEqual(self.grid.get_queue_length('N'), 0)  # N vehicle should move
        self.assertEqual(self.grid.get_queue_length('E'), 1)  # E vehicle should wait
        
        # Run for cycle_length steps to change light
        for _ in range(4):
            self.grid.update()
        
        # Now EW should be green
        self.assertFalse(self.grid.traffic_light.is_ns_green())
        self.grid.update()
        self.assertEqual(self.grid.get_queue_length('E'), 0)  # E vehicle should move
    
    def test_multiple_right_turns_allowed(self):
        """Test that multiple right turns are allowed in a single step."""
        # Add multiple right-turning vehicles to North queue
        for _ in range(3):
            self.grid.add_vehicle(MockVehicle('right', 'E'), 'N')
        
        # Add a straight-going vehicle behind the right turns
        self.grid.add_vehicle(MockVehicle('straight', 'N'), 'N')
        
        # Update with NS red light
        self.grid.traffic_light.ns_green = False
        self.grid.update()
        
        # All right turns should have moved, leaving only the straight vehicle
        self.assertEqual(self.grid.get_queue_length('N'), 1)
        # Verify the remaining vehicle is the straight-going one
        self.assertEqual(self.grid.queues['N'][0].get_turn_type(), 'straight')
    
    def test_mixed_turns_in_queue(self):
        """Test mixed right turns and straight/left turns in same queue."""
        # Queue: [right, straight, right, left, right]
        vehicles = [
            MockVehicle('right', 'E'),
            MockVehicle('straight', 'N'),
            MockVehicle('right', 'E'),
            MockVehicle('left', 'W'),
            MockVehicle('right', 'E')
        ]
        
        for vehicle in vehicles:
            self.grid.add_vehicle(vehicle, 'N')
        
        # Update with NS red light
        self.grid.traffic_light.ns_green = False
        self.grid.update()
        
        # All right turns should move (3 vehicles), leaving straight and left (2 vehicles)
        self.assertEqual(self.grid.get_queue_length('N'), 2)
        remaining_types = [v.get_turn_type() for v in self.grid.queues['N']]
        self.assertEqual(remaining_types, ['straight', 'left'])
        
        # Now update with NS green light
        self.grid.traffic_light.ns_green = True
        self.grid.update()
        
        # Only one straight/left vehicle should move
        self.assertEqual(self.grid.get_queue_length('N'), 1)
        self.assertEqual(self.grid.queues['N'][0].get_turn_type(), 'left')

if __name__ == '__main__':
    unittest.main()
