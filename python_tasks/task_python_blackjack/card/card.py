class Card:
    """ Card model """

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        
    
    def get_value(self):
        """ Converts given rank into integer values """
        if self.rank in ('K', 'Q', 'J', '10'):
            return 10

        if self.rank == 'A':
            return 11
        
        if '2' <= self.rank <= '9':
            return int(self.rank)
        
        return -1
    

    def __str__(self):
        """ Returns a string representation of the card, for example, 'King of Hearts' """
        return f"{self.rank} of {self.suit}"
    