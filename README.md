# Single Seller Market (Monopoly) Game
This repository contains a simple python implementation of Monopoly. The objective is to train a machine learning algorithm (actually multiple) to make decisions that are encountered in monopoly. The decisions that these algorithms have to make are purchasing, upgrading/downgrading, make a trade offer, decide to accept or reject trade offer. The algorithms are trained using Q-learning, meaning the algorithms start off executing random actions and learn from the rewards received based on those actions. 

## Reward
Monopoly is a complex game and decisions can be positive or negative depending on what metric you choose to measure. The factors included in calculating the reward are cash, total rent the player's properties can charge, the total value of the player's properties, the amount of monopolies owned. These values are taken before and after an action and the reward is calculated based on those values and how much the action has changed them. The reward is calculated by the following equation:

![Reward Equation](/images/reward_equation_latex.gif)

## Game State
All decisions rely on the state of the game as an input. The input consists of two types of states, the general state and the state of the player in relation to the fields. 

### Player State
The player state consists of six columns with each row being a unique property that can be purchased (utilities/properties):
* If the player is currently positioned on the property
* If the player owns the property
* If the player can upgrade the property
* If the player can downgrade the property
* If the player can mortgage the property
* If the player can unmortgage the property

### General State
The general state consists of eight columns that are the same for each player. The State has the same structure as the player state as each row pertains to a unique field that can be purchased (utilities/properties):
* If a monopoly is owned for that field
* The value of the field (Sum of purchase and all upgrades invested)
* If any player can purchase the field
* The purchase amount
* The mortgage amount
* The upgrade amount
* The downgrade amount
* The current rent being charged for all players (apart from the owner)

Together these states are used as inputs for player decisions.

## Purchasing
The purchasing decision is made from the player state and general state when the player lands on a field that has not been purchased yet and is not an actionfield. The output is two values: purchase, not purchase.

## Upgrading/Downgrading
The house, hotel buying decision also rely on the player state and general state. The output for this decision is 57 possible outcomes:
The first 28 is upgrading a field which are referenced sequentially in the list. As utilities such as water and railroads cannot be upgraded and subsequently downgraded they are only subjected to mortgage and unmortgage actions. This means that the first 28 slot alotment in the decision is valid for both upgrading and unmortgaging as those two actions equate to the same action. This is the same for the next 28 alotments in the decision which mean downgrading/mortgaging. The last alotment is for doing nothing.

## Trading
The trading action is done in tandem with two algorithms: the trade offer and the trade decision. The trade offer algorithm generates an offer consisting of cash and properties from the general state, the player state of the player making the offer, and the player state of the player the offer is directed at. The trade decision takes the general state, player state that gave the offer, its own player state, and the offer as input and has an output of accept or decline.

## Authors
* **Patrick Bogner** - [MammothStack](https://github.com/MammothStack)

## Acknowledgments
* All those kind souls helping out on StackOverflow <3
