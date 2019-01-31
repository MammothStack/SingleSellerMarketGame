from random import randrange
import numpy as np
import pandas as pd
import os
import configparser
from .player import Player
from .board_information import BoardInformation, BoardError

class BoardController():
    """Controls the sequence of the game from start to finish

    The BoardController sets the game up by inializing the BoardInformation
    with the relevant information. This controller then controls the sequence
    of actions that are performed by players such as purchasing, upgrading,
    downgrading, mortgaging, unmortgaging, and trading.

    The procedure of the game is determined here, which includes whose turn
    it is, how many times they can upgrade and downgrade something, the rewards
    that are calculated for the ais, where the players move, how  much cash
    they have, etc.

    These things are all setup with the initialization of this class. The only
    available methods are to start the game and reset the game after it has
    finished.

    Parameters
    --------------------


    Attributes
    --------------------


    Methods
    --------------------

    """
    def __init__(
        self,
        player_list,
        starting_order=None,
        max_turn=1000,
        upgrade_limit=30,
        reinforce_config=None,
        dynamic_cash_equation=True
    ):
        self.players = {p.name: p for p in player_list}
        self.board = BoardInformation([p.name for p in player_list])

        if reinforce_config is None:
            path = os.path.join(os.path.dirname(__file__), 'config.ini')
            self.config = configparser.ConfigParser()
            self.config.read(path)
        else:
            self.config = None

        self._cash_reward_function = {
            "positive" : lambda x: (-1 / ((0.004 * x) + 0.5) + 1),
            "negative" : lambda x: (1 / ((0.004 * x) + 0.5) - 1)
        }

        self.dynamic_cash_equation = dynamic_cash_equation
        self.alive = True
        self.total_turn = 0
        self.max_turn = max_turn
        self.current_turn = 0
        self.num_players = len(player_list)
        self.upgrade_limit = upgrade_limit
        pos = self.board.index
        self.decision_index = pos + pos

        if starting_order is None:
            self.order = [p.name for p in player_list]
        else:
            num_order = random.sample(
                range(self.num_players), self.num_players)
            self.order = [player_list[i].name for i in num_order]

    def start_game(self, show_results=False):
        while self.alive:
            self._full_turn(self.order[self.current_turn])

            """
            if self.alive:
                self.alive = self.board.is_any_purchaseable()
            """
            if self.alive:
                self.alive = self.total_turn < self.max_turn

            if self.alive:
                self.current_turn = (self.current_turn + 1) % self.num_players
            else:
                for p in self.players.values():
                    if p.is_ai:
                        p.learn()

            self.total_turn += 1

        if show_results:
            result_dict = {
                "player": [],
                "cash": [],
                "prop owned": [],
                "prop average level": []
            }
            for p in self.players:
                #print(p)
                o = self.board.get_amount_properties_owned(p)
                l = self.board.get_total_levels_owned(p)
                result_dict["player"].append(p.name)
                result_dict["cash"].append(self.players[p].cash)
                result_dict["prop owned"].append(o)
                result_dict["prop average level"].append(l / o)

            return result_dict


    def reset_game(self):
        for p in self.players.values():
            p.reset_player()

        self.board = BoardInformation([p for p in self.players.keys()])
        self.alive = True
        self.current_turn = 0
        self.total_turn = 0


    def _full_turn(self, name):
        if self.players[name].allowed_to_move:
            #move
            pos = self._turn_move(name)

            #upgrade/downgrade
            cont = True
            count = 0
            while cont and count < self.upgrade_limit:
                cont = self._step_upgrade_downgrade(name)
                count += 1

            #trade
        else:
            self.players[name].allowed_to_move = True

    def _get_dynamic_cash_reward(self, cash, pos_neg):
        if cash > 0:
            return self._cash_reward_function[pos_neg](cash)
        else:
            if pos_neg == "positive":
                return -1
            elif pos_neg == "negative":
                return 1

    def _turn_move(self, name):
        #Roll the dice
        d1, d2 = self._roll_dice()

        #Move the player to the new position
        new_pos = self._move_player(name, dice_roll=d1 + d2)

        #If player landed on action field
        if self.board.is_actionfield(new_pos):

            #get the action from the position
            act = self.board.get_action(new_pos)

            #If the action requires nothing
            if act is None:
                pass

            #If the action is free parking
            elif type(act) == str:
                self.players[name].cash += self.board.free_parking_cash
                self.board.free_parking_cash = 0

            #If the action is money transfer
            elif type(act) == int:
                #change player cash amount
                self.players[name].cash += act

                #if negative, cash added to free parking
                if act < 0:
                    self.board.free_parking_cash -= act

            #if the action is a "goto"
            elif type(act) == tuple:
                #move the player
                self._move_player(name, position=act[1])

                #if player moves to go
                if act[1] == 0:
                    pass

                #if player moves to jail
                elif act[1] == 10:
                    self.players[name].allowed_to_move = False

                #if player moves to free parking
                elif act[1] == 20:
                    self.players[name].cash += self.board.free_parking_cash
                    self.board.free_parking_cash = 0
            else:
                raise ValueError("Something went way wrong here")

            return new_pos

        #If player lands on a property field
        elif self.board.is_property(new_pos) or self.board.is_special(new_pos):
            #If the property is purchaseable
            if self.board.can_purchase(name, new_pos):
                self._step_purchase(name, new_pos)

            #is owned
            else:
                #is owned by player already
                if self.board.is_owned_by(name, new_pos):
                    pass

                #is owned by opponent
                else:
                    opponent_name = self.board.get_owner_name(new_pos)
                    rent = self.board.get_rent(new_pos, d1 + d2)
                    self.players[opponent_name].cash += rent
                    self.players[name].cash -= rent

        else:
            raise ValueError("field not found")

    def _step_purchase(self, name, position):
        if self.players[name].is_ai:
            decision = self.players[name].get_decision(
                self.board.get_normalized_state(name),
                "purchase",
                self.config.getfloat("purchase_threshold", "Threshold")
            )
        else:
            pass

        if decision[0] > self.config.getfloat("purchase_threshold", "Threshold"):
            self.board.purchase(name, position)
            self.players[name].cash -= self.board.get_purchase_amount(position)

            if self.players[name].cash < 0:
                reward = self.config.getfloat("purchase_reward", "Suicide")
                reward_dynamic = reward
                self.alive = False
            else:
                reward_dynamic = self._get_dynamic_cash_reward(self.players[name].cash, "positive")
                if self.board.is_monopoly(position):
                    reward_dynamic += 1
                    reward = self.config.getfloat("purchase_reward", "PurchaseMonopoly")
                else:
                    reward = self.config.getfloat("purchase_reward", "PurchaseStandard")
        else:
            reward_dynamic = self._get_dynamic_cash_reward(self.players[name].cash, "negative")
            reward = self.config.getfloat("purchase_reward", "None")

        if self.players[name].is_ai:
            if self.dynamic_cash_equation:
                self.players[name].give_reward("purchase", reward_dynamic)
            else:
                self.players[name].give_reward("purchase", reward)

    def _step_upgrade_downgrade(self, name):
        if self.players[name].is_ai:
            decision = self.players[name].get_decision(
                self.board.get_normalized_state(name),
                "up_down_grade",
                self.config.getfloat("upgrade_threshold", "Threshold")
            )
        else:
            pass

        ind = np.argmax(decision)
        pos = self.decision_index[ind]
        cont = False

        #if decision is above threshold
        if decision[ind] > self.config.getfloat("upgrade_threshold", "Threshold"):

            #if decision is downgrade/mortgage
            if ind + 1 > len(decision) / 2:

                #if position can even be downgraded
                if self.board.can_downgrade(name, pos):
                    self.players[name].cash += self.board.get_downgrade_amount(pos)
                    reward = self.config.getfloat("updown_reward", "CanDowngrade")
                    reward_dynamic = self._get_dynamic_cash_reward(self.players[name].cash, "negative")
                    cont = True
                    self.board.downgrade(name, pos)

                elif self.board.can_mortgage(name, pos):
                    self.players[name].cash += self.board.get_mortgage_amount(pos)
                    reward = self.config.getfloat("updown_reward", "CanMortgage")
                    reward_dynamic = self._get_dynamic_cash_reward(self.players[name].cash, "negative")
                    cont = True
                    self.board.mortgage(name, pos)

                #if position cant be dowgraded
                else:
                    reward = self.config.getfloat("updown_reward", "NonExecutableDecision")
                    reward_dynamic = reward
                    cont = False

            #if decision is upgrade
            else:

                #if position can even be upgraded
                if self.board.can_upgrade(name, pos):
                    self.players[name].cash -= self.board.get_upgrade_amount(pos)
                    reward = self.config.getfloat("updown_reward", "CanUpgrade")
                    reward_dynamic = self._get_dynamic_cash_reward(self.players[name].cash, "positive")
                    cont = True
                    self.board.upgrade(name, pos)

                #if position can be unmortgaged
                elif self.board.can_unmortgage(name, pos):
                    self.players[name].cash -= self.board.get_mortgage_amount(pos)
                    reward = self.config.getfloat("updown_reward", "CanUnmortgage")
                    reward_dynamic = self._get_dynamic_cash_reward(self.players[name].cash, "positive")
                    cont = True
                    self.board.unmortgage(name, pos)

                else:
                    reward = self.config.getfloat("updown_reward", "NonExecutableDecision")
                    reward_dynamic = reward
                    cont = False

                #if upgrade causes bankruptcy
                if self.players[name].cash < 0:
                    cont = False
                    reward = self.config.getfloat("updown_reward", "UpgradeSuicide")
                    reward_dynamic = reward
                    self.alive = False

        #if decision is pass
        else:
            reward = self.config.getfloat("updown_reward", "None")
            reward_dynamic = reward
            cont = False

        if self.players[name].is_ai:
            if self.dynamic_cash_equation:
                self.players[name].give_reward("up_down_grade", reward_dynamic)
            else:
                self.players[name].give_reward("up_down_grade", reward)

        return cont

    def _turn_trade(self, name):
        pass

    def _roll_dice(self):
        return randrange(1,7), randrange(1,7)

    def _move_player(self, name, dice_roll=None, position=None):
        if position is None and dice_roll is not None:
            new_position = (self.players[name].position + dice_roll) % 40
        elif position is not None and dice_roll is None:
            new_position = position
        else:
            raise ValueError("Wrong Input")

        if new_position < self.players[name].position:
            self.players[name].cash += 200
        self.players[name].position = new_position

        return new_position

    def _downgrade(self, name, pos):
        if self.board.can_downgrade(name, pos):
            if self.board.get_level(pos) == 1:
                self.board.mortgage(name, pos)
            else:
                self.board.downgrade(name, pos)

    def _upgrade(self, name, pos):
        if self.board.can_upgrade(name, pos):
            if self.board.get_level(pos) == 0:
                self.board.unmortgage(name, pos)
            else:
                self.board.upgrade(name, pos)
