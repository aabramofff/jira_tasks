from deck.deck import Deck
from hand.hand import Hand


class Game:
    """ Simulates one round of simplified Blackjack """
    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.is_player_bust = False
        self.is_dealer_bust = False
        self.round_result = None

    
    def start_round(self):
        """ Give two start cards """
        for _ in range(2):
            self.player_hand.add_card(self.deck.deal_card())
            self.dealer_hand.add_card(self.deck.deal_card())
        
        self.player_turn()

    
    def player_turn(self):
        """ Fixed Player strategy (Hit < 17, Stand >= 17) """
        while self.player_hand.get_value() < 17:
            card = self.deck.deal_card()
            if card is None:
                break
            self.player_hand.add_card(card)

            if self.player_hand.get_value() > 21:
                self.is_player_bust = True
                self.round_result = 'Dealer Win'
                return


    def dealer_turn(self):
        """
        Dealer's strategy. 
        The dealer only moves if the player has not busted And the dealer's score is less than the player's score.
        """
        player_score = self.player_hand.get_value()
        dealer_score = self.dealer_hand.get_value()

        while dealer_score < player_score:
            card = self.deck.deal_card()
            if card is None:
                break
            self.dealer_hand.add_card(card)
            dealer_score = self.dealer_hand.get_value()

            if dealer_score > 21:
                self.is_dealer_bust = True
                self.round_result = 'Player Win'
                return


    def determine_winner(self):
        """ Determines and returns final result of the round """
        if self.is_player_bust:
            return 'Dealer Win'
        
        if self.round_result is None:
            self.dealer_turn()

        if self.is_dealer_bust:
            return 'Player Win'
        
        player_score = self.player_hand.get_value()
        dealer_score = self.dealer_hand.get_value()

        if player_score > dealer_score:
            return 'Player Win'
        elif player_score < dealer_score:
            return 'Dealer Win'
        else:
            return 'Draw'
        
    
    def play_round(self):
        """ Starts full round and returns the result """
        self.start_round()

        if self.round_result is None:
            self.round_result = self.determine_winner()

        return self.round_result
