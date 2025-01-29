# Traffic Simulation Project

This project simulates traffic flow in a grid-based city model with traffic lights. It allows testing different traffic light control strategies to optimize traffic flow.

## Features

- NxM grid model of intersections with periodic boundary conditions
- Vehicle generation and movement simulation
- Traffic light control with customizable strategies
- Real-time visualization of traffic density

## Requirements

- Python 3.8+
- Dependencies listed in requirements.txt

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the simulation:
```bash
python src/simulation.py
```

## Project Structure

- `src/models/`: Core data models
- `src/controllers/`: Traffic light control strategies
- `src/visualization/`: Visualization components
