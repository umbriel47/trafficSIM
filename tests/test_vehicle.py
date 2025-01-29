import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from src.models.vehicle import Vehicle
import numpy as np

class TestVehicle(unittest.TestCase):
    def setUp(self):
        # Set random seed for reproducibility
        np.random.seed(42)
        self.grid_size = (10, 10)
    
    def test_path_calculation_normal(self):
        """Test path calculation without crossing boundaries."""
        # Test case 1: Simple horizontal movement
        vehicle = Vehicle((5, 2), (5, 7), self.grid_size)
        path = vehicle.path
        self.assertEqual(path[0], (5, 2))  # Start
        self.assertEqual(path[-1], (5, 7))  # End
        self.assertEqual(len(path), 6)  # Should take 5 steps
        
        # Test case 2: Simple diagonal movement
        vehicle = Vehicle((2, 2), (4, 4), self.grid_size)
        path = vehicle.path
        self.assertEqual(path[0], (2, 2))
        self.assertEqual(path[-1], (4, 4))
        self.assertTrue(len(path) <= 5)  # Should take at most 4 steps
    
    def test_path_calculation_periodic_horizontal(self):
        """Test path calculation with horizontal periodic boundaries."""
        # Test case: When going right through boundary is shorter
        vehicle = Vehicle((5, 8), (5, 1), self.grid_size)
        path = vehicle.path
        self.assertEqual(path[0], (5, 8))
        self.assertEqual(path[-1], (5, 1))
        self.assertTrue(len(path) <= 4)  # Should take 3 steps through boundary
        
        # Verify that path goes through right boundary
        positions = set((pos[0], pos[1]) for pos in path)
        self.assertTrue((5, 9) in positions)  # Should pass through rightmost column
        
        # Test opposite direction
        vehicle = Vehicle((5, 1), (5, 8), self.grid_size)
        path = vehicle.path
        self.assertTrue(len(path) <= 4)  # Should take 3 steps through boundary
    
    def test_path_calculation_periodic_vertical(self):
        """Test path calculation with vertical periodic boundaries."""
        # Test case: When going through top boundary is shorter
        vehicle = Vehicle((8, 5), (1, 5), self.grid_size)
        path = vehicle.path
        self.assertEqual(path[0], (8, 5))
        self.assertEqual(path[-1], (1, 5))
        self.assertTrue(len(path) <= 4)  # Should take 3 steps through boundary
        
        # Verify that path goes through top boundary
        positions = set((pos[0], pos[1]) for pos in path)
        self.assertTrue((9, 5) in positions)  # Should pass through bottom row
        
        # Test opposite direction
        vehicle = Vehicle((1, 5), (8, 5), self.grid_size)
        path = vehicle.path
        self.assertTrue(len(path) <= 4)  # Should take 3 steps through boundary
    
    def test_path_calculation_periodic_diagonal(self):
        """Test path calculation with both horizontal and vertical periodic boundaries."""
        # Test case: When going through both boundaries is shorter
        vehicle = Vehicle((8, 8), (1, 1), self.grid_size)
        path = vehicle.path
        self.assertEqual(path[0], (8, 8))
        self.assertEqual(path[-1], (1, 1))
        
        # The path should be shorter than going through the middle
        self.assertTrue(len(path) <= 7)  # Should take at most 6 steps
        
        # Test opposite direction
        vehicle = Vehicle((1, 1), (8, 8), self.grid_size)
        path = vehicle.path
        self.assertTrue(len(path) <= 7)  # Should take at most 6 steps
    
    def test_periodic_movement(self):
        """Test that vehicle correctly handles movement across periodic boundaries."""
        # Test horizontal boundary crossing
        vehicle = Vehicle((5, 9), (5, 0), self.grid_size)
        initial_pos = vehicle.current_pos
        vehicle.move()  # Move to position (5, 0)
        self.assertEqual(vehicle.current_pos, (5, 0))
        
        # Test vertical boundary crossing
        vehicle = Vehicle((9, 5), (0, 5), self.grid_size)
        initial_pos = vehicle.current_pos
        vehicle.move()  # Move to position (0, 5)
        self.assertEqual(vehicle.current_pos, (0, 5))
        
        # Test diagonal boundary crossing
        vehicle = Vehicle((9, 9), (0, 0), self.grid_size)
        initial_pos = vehicle.current_pos
        vehicle.move()
        self.assertTrue(vehicle.current_pos in [(0, 9), (9, 0)])  # Should move either up or right

if __name__ == '__main__':
    unittest.main()
