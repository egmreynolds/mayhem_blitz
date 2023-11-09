### war_game
##### Obviously needs a better name

## Game overview:
#### Dominion-like deck builder meets competitive card game meets random chance.
Deal damage and invest in your army through a series of battles to ultimately become the winner.

# Installation

- use python3.9 -> python3.11
- create virtual env (python3 -m venv env)
- activate env (source env/bin/activate)
- install requirements (pip install -r requirements.txt)
- config env vars (server and client)

# TODO
- implement logic for ending threads (server and client)

# Desireable Features - Functionality:
- login screen
- search for game queue
- Avoid ping_timeout (currently set to 120 seconds...)

# Desireable Features - Gameplay Logic
- Add cost variable for cards
- Lich ability doesn't work
- New Cards  
- Log game state and/or game outcome in database

# Desireable Features - Game Display
- Add description to cards
- Add images to cards
- Avoid gamelog overwrite, convert to scrollable game-log.
- Add thorough game rules section

How to play:
Start with set of generic small deck of cards.
Each player draws a hand of 5 cards from which they will select 3 to play face down in front of them in an order of your choice.
Each card played 'faces-off' against the opponents respective card, the winner earns gold (1), the loser's cards ability is activated.
Each players "army" - sum of played cards attack power - faces off and the loser takes the difference in damage to their HP.
If a player reaches 0 HP, their opponent wins.
A purchase phase after each round allows players to buy a card from the communal supply with the gold they have earned and add this card to their discard pile.
All cards in play and in hand are discarded.
A new round begins. <Discard piles are shuffled into decks when decks are empty>.

Abilities are described in abilities_functions.py

Feel free to add any ability ideas you have, even if you don't implement them.

Upcoming changes of interest:
Make a gui representation either ktinker, unity, unreal, I don't know.
Set up server, either local or AWS, so we can play online against each other.
Make it so opponent can't see your hand / cards played...
