# Python Question
In this task you will need to write a Monte Carlo simulator for a cut down version of Blackjack. In this
version of Blackjack only one player plays against the dealer.
The simulator needs to follow these rules.
- The ‘player’ takes all his turns first and then the dealer afterwards
- The player will automatically hit (take another card) if the total they have is less than 17, otherwise they will stand (stick with the cards they have). The player could hit multiple times
- If the player hits and goes bust, then the dealer will win
- If the player has the same value as the dealer then it’s a draw
- If the player has more than the dealer, then the dealer will hit. The dealer could hit multiple times
- Remember that an Ace can be worth 1 or 11.

You can ignore the other rules of Blackjack, such splitting when a person receives a pair, as we want
to keep this simple

Your simulator should be runnable for N number of simulations

The output of the simulation should be:


```
The simulator ran N times
The player won _ times
The dealer won _ times
There were _ draws
```
