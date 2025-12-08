from card.card import Card

class Hand:
    """ Represents player's of dealer's deck of cars and calculates total score """
    def __init__(self):
        self.players_deck = []

    
    def add_card(self, card):
        """ Add one card into hand """
        self.players_deck.append(card)


    def get_value(self):
        """ Calculates total score, properly handling aces """
        score = 0
        aces_counter = 0

        for card in self.players_deck:
            card_value = card.get_value()

            score += card_value

            if card.rank == 'A':
                aces_counter += 1

            while score > 21 and aces_counter > 0:
                score -= 10
                aces_counter -=1
            
        return score
    
    def __str__(self):
        """ Return Player's or Dealer's deck of cards """
        return ", ".join(str(card) for card in self.players_deck)
    