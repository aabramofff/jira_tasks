from random import shuffle
from card.card import Card


class Deck:
    """ Creates a deck of 52 cards, shuffling & giveaway """

    # Lists of card suits and ranks to create full deck
    SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']


    def __init__(self):
        self.deck = []
        self._deck_create()


    def _deck_create(self):
        """ The internal method, which fills the deck """
        for suit in self.SUITS:
            for rank in self.RANKS:
                self.deck.append(Card(suit, rank))
        
        self.shuffle()

    
    def shuffle(self):
        """ Shuffle elements randomly """
        shuffle(self.deck)


    def deal_card(self):
        """ 
        Returns one card from deck
        If the deck is empty, returns None
        """
        if not self.deck:
            return None
        
        card = self.deck.pop()
        return card
