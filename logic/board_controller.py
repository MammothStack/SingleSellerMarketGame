from random import randrange
import numpy as np
import pandas as pd

class BoardController():
    def __init__(
        self,
        player_list,
        starting_order=None,
        max_turn=1000,
        upgrade_limit=30,
        display=False
    ):
        self.players = {p.name: p for p in player_list}
        self.board = BoardInformation([p.name for p in player_list])
        self.alive = True
        self.total_turn = 0
        self.max_turn = max_turn
        self.current_turn = 0
        self.num_players = len(player_list)
        self.upgrade_limit = upgrade_limit
        self.display = display
        pos = self.board.get_table().index
        self.decision_index = pos + pos

        if starting_order is None:
            self.order = [p.name for p in player_list]
        else:
            num_order = random.sample(
                range(self.num_players), self.num_players)
            self.order = [player_list[i].name for i in num_order]

    def start_game(self, verbose=0):
        while self.alive:
            self._full_turn(self.order[self.current_turn], verbose)

            if self.alive:
                self.alive = self.board.is_any_purchaseable()

            if self.alive:
                self.alive = self.total_turn < self.max_turn

            if self.alive:
                self.current_turn = (self.current_turn + 1) % self.num_players
            else:
                for p in self.players.values():
                    if p.is_ai:
                        p.learn()

            self.total_turn += 1

    def reset_game(self):
        for p in self.players.values():
            p.reset_player()

        self.board = BoardInformation([p for p in self.players.keys()])
        self.alive = True
        self.current_turn = 0
        self.total_turn = 0


    def _full_turn(self, name, verbose=0):
        if self.players[name].allowed_to_move:

            if verbose:
                print(name)
            #move
            pos = self._turn_move(name,verbose)

            #upgrade/downgrade
            cont = True
            count = 0
            while cont and count < self.upgrade_limit:
                cont = self._step_upgrade_downgrade(name,verbose)
                count += 1

            #trade
        else:
            self.players[name].allowed_to_move = True

    def _turn_move(self, name, verbose=0):
        #Roll the dice
        d1, d2 = self._roll_dice()

        #Move the player to the new position
        new_pos = self._move_player(name, dice_roll=d1 + d2)

        if verbose:
            print("moved to: " +
                  str(new_pos) +
                  ":" +
                  self.board.get_property_name(new_pos))

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
                if verbose:
                    print(self.players[name].cash)

                self.players[name].cash += act

                if verbose:
                    print(self.players[name].cash)

                if verbose:
                    print(name +
                          " gets " +
                          str(act) +
                          " cash/" +
                          str(self.players[name].cash))

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
                self._step_purchase(name, new_pos, verbose)

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
                    if verbose:
                        print(name + " --" + str(rent) + "-> " + opponent_name)

        else:
            raise ValueError("field not found")

    def _step_purchase(self, name, position, verbose=0):
        if self.players[name].is_ai:
            decision = self.players[name].get_decision(
                self.board.get_normalized_state(name),
                "purchase"
            )
        else:
            pass

        if decision[0] > 0.5:
            if verbose:
                print("purchase")
                print(self.players[name].cash)

            self.board.purchase(name, position)
            self.players[name].cash -= self.board.get_purchase_price(position)

            if verbose:
                print(self.players[name].cash)

            if self.players[name].cash < 0:
                reward = -1
                self.alive = False
                if verbose:
                    print("XXXXXXX made an oopsie")
            else:
                if self.board.is_monopoly(position):
                    reward = 2
                else:
                    reward = 1
        else:
            reward = 0

        if self.players[name].is_ai:
            self.players[name].give_reward("purchase", reward)

    def _step_upgrade_downgrade(self, name, verbose=0):
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
        if decision[ind] > 0.5:

            #if decision is downgrade
            if ind + 1 > len(decision) / 2:

                #if position can even be downgraded
                if self.board.can_downgrade(name, pos):
                    reward = 0
                    if self.board.get_level(pos) == 1:
                        print("mortgaged")
                        self.board.mortgage(name, pos)
                    else:
                        print("downgrade")
                        self.board.downgrade(name, pos)

                    cont = True

                #if position cant be dowgraded
                else:
                    reward = -1
                    cont = False

            #if decision is upgrade
            else:

                #if position can even be upgraded
                if self.board.can_upgrade(name, pos):
                    reward = 1
                    if self.board.get_level(pos) == 0:
                        if verbose:
                            print("unmortgaged")
                        self.board.unmortgage(name, pos)
                    else:
                        if verbose:
                            print("upgrade")
                        self.board.upgrade(name, pos)

                    cont = True

                    #if upgrade causes bankruptcy
                    if self.players[name].cash < 0:
                        cont = False
                        reward = -1
                        self.alive = False
                        if verbose:
                            print("XXXXXXX made an oopsie")
                #if position cant be upgraded
                else:
                    cont = False
                    reward = -1

        #if decision is pass
        else:
            reward = 0
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
                print("mortgaged")
                self.board.mortgage(name, pos)
            else:
                print("downgrade")
                self.board.downgrade(name, pos)

    def _upgrade(self, name, pos):
        if self.board.can_upgrade(name, pos):
            if self.board.get_level(pos) == 0:
                print("unmortgaged")
                self.board.unmortgage(name, pos)
            else:
                print("upgrade")
                self.board.upgrade(name, pos)
