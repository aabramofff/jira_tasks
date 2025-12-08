from deck.deck import Deck
from hand.hand import Hand
from game.game import Game
from simulation.simulation import Simulation

if __name__ == '__main__':
    NUM_RUNS = 100_000

    try:
        monte_carlo = Simulation(NUM_RUNS)
        monte_carlo.run_simulation()

        monte_carlo.calculate_statistics()
    except ValueError as e:
        print(f"Parameters error: {e}")
