from random import randrange
import numpy as np
import pandas as pd
import os
import configparser
from .player import Player
from .board_information import BoardInformation, BoardError

class BoardController():
    def __init__(
        self,
        player_list,
        starting_order=None,
        max_turn=1000,
        upgrade_limit=30,
        reinforce_config=None
    ):
        self.players = {p.name: p for p in player_list}
        self.board = BoardInformation([p.name for p in player_list])

        if reinforce_config is None:
            path = os.path.join(os.path.dirname(__file__), 'config.ini')
            self.config = configparser.ConfigParser()
            self.config.read(path)
        else:
            self.config = reinforce_config

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
            for p in self.players:
                print(p)
                o = self.board.get_amount_properties_owned(p)
                l = self.board.get_total_levels_owned(p)
                print({
                    "cash": self.players[p].cash,
                    "prop owned": o,
                    "prop average level": l / o
                })

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
                if self.board.is_owned_by(new_pos, name):
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
                self.config.getint("purchase_threshold", "Threshold")
            )
        else:
            pass

        if decision[0] > self.config.getint("purchase_threshold", "Threshold"):
            self.board.purchase(name, position)
            self.players[name].cash -= self.board.get_purchase_price(position)

            if self.players[name].cash < 0:
                reward = self.config.getint("purchase_reward", "Suicide")
                self.alive = False
            else:
                if self.board.is_monopoly(position):
                    reward = self.config.getint("purchase_reward", "PurchaseMonopoly")
                else:
                    reward = self.config.getint("purchase_reward", "PurchaseStandard")
        else:
            reward = self.config.getint("purchase_reward", "None")

        if self.players[name].is_ai:
            self.players[name].give_reward("purchase", reward)

    def _step_upgrade_downgrade(self, name):
        if self.players[name].is_ai:
            decision = self.players[name].get_decision(
                self.board.get_normalized_state(name),
                "up_down_grade"
            )
        else:
            pass

        ind = np.argmax(decision)
        pos = self.decision_index[ind]
        cont = False

        #if decision is above threshold
        if decision[ind] > self.config.getint("upgrade_threshold", "Threshold"):

            #if decision is downgrade/mortgage
            if ind + 1 > len(decision) / 2:

                #if position can even be downgraded
                if self.board.can_downgrade(name, pos):
                    reward = self.config.getint("updown_reward", "CanDowngrade")
                    cont = True
                    print("downgrade: " + name + " " + str(pos))
                    self.board.downgrade(name, pos)

                elif self.board.can_mortgage(name, pos):
                    reward = self.config.getint("updown_reward", "CanMortgage")
                    cont = True
                    print("mortgaged: " + name + " " + str(pos))
                    self.board.mortgage(name, pos)

                #if position cant be dowgraded
                else:
                    reward = self.config.getint("updown_reward", "NonExecutableDecision")
                    cont = False

            #if decision is upgrade
            else:

                #if position can even be upgraded
                if self.board.can_upgrade(name, pos):
                    reward = self.config.getint("updown_reward", "CanUpgrade")
                    cont = True
                    print("upgrade: " + name + " " + str(pos))
                    self.board.upgrade(name, pos)

                #if position can be unmortgaged
                elif self.board.can_unmortgage(name, pos):
                    reward = self.config.getint("updown_reward", "CanUnmortgage")
                    cont = True
                    print("unmortgaged: " + name + " " + str(pos))
                    self.board.unmortgage(name, pos)

                else:
                    reward = self.config.getint("updown_reward", "NonExecutableDecision")
                    cont = False

                #if upgrade causes bankruptcy
                if self.players[name].cash < 0:
                    cont = False
                    reward = self.config.getint("updown_reward", "UpgradeSuicide")
                    self.alive = False

        #if decision is pass
        else:
            reward = self.config.getint("updown_reward", "None")
            cont = False

        if self.players[name].is_ai:
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
                #print("mortgaged")
                self.board.mortgage(name, pos)
            else:
                #print("downgrade")
                self.board.downgrade(name, pos)

    def _upgrade(self, name, pos):
        if self.board.can_upgrade(name, pos):
            if self.board.get_level(pos) == 0:
                #print("unmortgaged")
                self.board.unmortgage(name, pos)
            else:
                #print("upgrade")
                self.board.upgrade(name, pos)
