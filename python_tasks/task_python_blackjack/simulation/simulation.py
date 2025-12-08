from game.game import Game


class Simulation:
    """ Simulates Monte-Carlo Blackjack game process """
    def __init__(self, num_simulations):
        if num_simulations < 6:
            raise ValueError("Simulation number must be positive integer!")

        self.num_simulations = num_simulations
        self.results = {
            'Player Win' : 0,
            'Dealer Win' : 0,
            'Draw' : 0
        }

    
    def run_simulation(self):
        """ Starts the set number of rounds of the game. """
        print(f"Simulation starts with {self.num_simulations} iterations...")

        for _ in range(self.num_simulations):
            game = Game()

            result = game.play_round()

            if result in self.results:
                self.results[result] += 1
        
        print("The simulation was completed successfully")

    
    def calculate_statistics(self):
        """ Calculates and outputs the percentage probabilities of outcomes """
        print("==============Monte-Carlo Blackjack simulation results==============")

        total_rounds = self.num_simulations

        win_rate = (self.results['Player Win'] / total_rounds) * 100
        loss_rate = (self.results['Dealer Win'] / total_rounds) * 100
        draw_rate = (self.results['Draw'] / total_rounds) * 100

        print("Total rounds:", total_rounds)

        print(f"The number of Player's Wins: {self.results['Player Win']};\nPlayer's Win Rate: {win_rate:.2f} %\n")
        print(f"The number of Dealer's Wins: {self.results['Dealer Win']};\nDealer's Win Rate: {loss_rate:.2f} %\n")
        print(f"The number of Draws: {self.results['Draw']};\nDraw's Rate: {draw_rate:.2f} %\n")

        if abs(win_rate + loss_rate + draw_rate - 100) > 0.01:
            print("An error was occored: you have too big error rate!")

        return self.results
        