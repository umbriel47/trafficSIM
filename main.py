from src.simulation import Simulation

def main():
    # Create and run simulation
    sim = Simulation(rows=10, cols=10, p1=0.3)
    try:
        while True:
            sim.step()
    except KeyboardInterrupt:
        print("\nSimulation ended by user")

if __name__ == "__main__":
    main()
