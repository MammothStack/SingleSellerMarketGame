from random import randrange, sample
import numpy as np
import pandas as pd
import os
import configparser
from .player import Agent
from .game import Board, BoardError


class GameController:
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
        max_turn=500,
        available_houses=32,
        available_hotels=12,
        starting_cash=1500,
        # upgrade_limit=20,
        reward_scalars={"cash": 0.005, "value": 0.01, "rent": 0.005, "monopoly": 1.0},
    ):

        self.players = {p.name: p for p in player_list}

        self.max_turn = max_turn
        self.available_hotels = available_hotels
        self.available_houses = available_houses
        self.starting_cash = starting_cash
        self.num_players = len(player_list)
        # self.upgrade_limit = upgrade_limit
        self.reward_scalars = reward_scalars
        self.reset_game()

    def start_game(self, purchase=True, up_down_grade=True, trade=True):
        """Starts the game

        Starts the game with the current configuration. The parameters that can
        be set relate to the actions that the AI can take. This way the flow
        of the game can be somewhat restricted.

        Parameters
        --------------------
        purchase : boolean (default=True)
            If he game should have the purchase actions

        up_down_grade : boolean (default=True)
            If the game should have the upgrade/downgrade actions

        trade : boolean (default=True)
            If the game should have the trade actions

        Returns
        --------------------
        results : dict
            A dictionary of results where the keys are the players of the game
            and the values are a Pandas.Series object containing game
            information

        """

        self.operation_config = {
            "purchase": purchase,
            "up_down_grade": up_down_grade,
            "trade": trade,
        }

        results = {}
        while self.board.alive:
            # Runs through all three actions
            self._full_turn(self.board.current_player)

            # Checks if any properties can still be bought. quit if none
            if up_down_grade == False and trade == False and len(self.players) == 1:
                if self.board.alive:
                    self.board.alive = self.board.is_any_purchaseable()
            self.board.increment_turn()
        for p in self.players.keys():
            self.players[p].learn()
            o = self.board.get_amount_properties_owned(p)
            l = self.board.get_total_levels_owned(p)

            results[p] = pd.Series(
                data=[
                    p,
                    self.board.get_player_cash(p),
                    o,
                    l / o,
                    self.board.current_turn,
                ],
                index=[
                    "name",
                    "cash",
                    "prop_owned",
                    "prop_average_level",
                    "turn_count",
                ],
                name=p,
            )
        return results

    def reset_game(self):
        """Resets all the game parameters so their default values

        Calls all players of the game to reset to their initial values
        as well as the turn counter and "alive" state of the board

        """
        self.board = Board(
            *[p for p in self.players.keys()],
            max_turn=self.max_turn,
            available_houses=self.available_houses,
            available_hotels=self.available_hotels,
            starting_cash=self.starting_cash,
        )

    def _get_state(self, name, opponent=None, offer=None):
        """Returns the processed state for the given name

        Fetches the general and normalized state of the game with the
        given parameters. The specified name narrows the resulting table
        to the including only the general information and the information
        specific to that player.

        If information on an opponent should be included, which is the case
        for trading, an opponent can be added for which the information will
        also be fetched.

        If only the player fetches the information the resulting array will
        include:
            player cash
            player position
            player property specific columns
            general columns

        resulting in a one-dimensional array (393,)

        If the player and opponent data is fetched then the resulting table
        will be made up of the following data:
            player cash
            player position
            player property specific columns
            opponent cash
            opponent position
            opponent property
            general columns

        resulting in a one-dimensional array (562,)

        Parameters
        --------------------
        name : str
            The name of the player for which the information should be fetched

        opponent : str (default=None)
            The name of the opponent for which the information should be
            fetched

        offer : numpy.ndarray (default=None)
            The offer during trade that should be added as to the x array

        Returns
        --------------------
        Gamestate array : numpy.ndarray
             A one-dimensional array (420,)/(616,)

        """
        gen_state = self.board.get_general_state()
        pla_state = self.board.get_player_state(name)

        opp_state = []
        offer_state = []

        if opponent is not None:
            opp_state = self.board.get_player_state(opponent)
        if offer is not None:
            offer_state = offer
        concatenated = np.concatenate((offer_state, opp_state, pla_state, gen_state))
        return np.array((concatenated,))

    def _full_turn(self, name):
        if not self.board.is_player_jailed(name):
            # Roll the dice
            d1, d2 = self.board.roll_dice()

            # Move the player to the new position
            new_pos = self.board.move_player(name, dice_roll=d1 + d2)

            # If player landed on action field
            if self.board.is_action(new_pos):
                r, action_pos = self._land_action_field(name, new_pos)
                if r:
                    purchase = True
                    new_pos = action_pos
                else:
                    purchase = False
            else:
                purchase = self._land_property(name, new_pos, d1 + d2)
            if (
                self.operation_config["purchase"]
                and purchase
                and self.players[name].can_purchase
            ):
                self._purchase_turn(name, new_pos)
        else:
            self.board.set_player_out_of_jail(name)
        if (
            self.operation_config["up_down_grade"]
            and self.players[name].can_up_down_grade
        ):
            self._up_down_grade_turn(name)
        # trade
        if self.operation_config["trade"] and self.players[name].can_trade_offer:
            self._trade_turn(name)

    def _purchase_turn(self, name, new_position):
        state = self._get_state(name)
        action = self.players[name].get_action(state, "purchase")
        reward = self._execute_purchase(name, new_position, action)
        next_state = self._get_state(name)
        done = not self.board.is_any_purchaseable()
        self.players[name].add_training_data(
            "purchase", state, action, reward, next_state, done
        )

    def _up_down_grade_turn(self, name):
        state = self._get_state(name)
        action = self.players[name].get_action(state, "up_down_grade")
        reward = self._execute_up_down_grade(name, action)
        next_state = self._get_state(name)
        done = self.board.get_player_cash(name) < 0
        self.players[name].add_training_data(
            "up_down_grade", state, action, reward, next_state, False
        )

    def _trade_turn(self, name):
        for opponent in self.players.keys():
            if name != opponent and self.players[opponent].can_trade_decision:
                state = self._get_state(name, opponent)
                action = self.players[name].get_action(state, "trade_offer")
                reward = self._evaluate_trade_offer(action, name, opponent)

                state_opp = np.concatenate((state, action))
                action_opp = self.players[name].get_action(state_opp, "trade_decision")
                reward_opp = -reward

                if action_opp[0] == 1:
                    self._execute_trade(action, name, opponent)

                    next_state = self._get_state(name, opponent)
                    potential_action = self.players[name].get_action(
                        next_state, "trade_offer"
                    )
                    next_state_opp = np.concatenate((next_state, potential_action))

                    self.players[name].add_training_data(
                        "trade_offer", state, action, reward, next_state, False
                    )
                    self.players[opponent].add_training_data(
                        "trade_decision",
                        state_opp,
                        action_opp,
                        reward_opp,
                        next_state_opp,
                        False,
                    )

    def _land_action_field(self, name, position):
        # get the action from the position
        act = self.board.get_action(position)

        if type(act) == int:
            self.board.add_player_cash(name, act)
            if act < 0:
                self.board.add_to_free_parking(-act)
        # If the action is money transfer
        elif type(act) == dict:
            if "goto" in act.keys():
                g = act["goto"]
                new_pos = self.board.move_player(name, position=g)
                if g == 0:
                    pass
                elif g == 10:
                    self.board.jail_player(name)
                elif g == 20:
                    self.board.add_player_cash(
                        name, self.board.get_free_parking(clear=True)
                    )
                elif self.board.is_utility(g) or self.board.is_property(g):
                    return (self._land_property(name=name, position=g), g)
            elif "free parking" in act.keys():
                self.board.add_player_cash(
                    name, self.board.get_free_parking(clear=True)
                )
        # If the action requires nothing
        elif act is None:
            pass
        return False, None

    def _land_property(self, name, position, dice_roll=7):
        # If the property is purchaseable
        if self.board.can_purchase(position):
            return True
        # is owned
        else:
            # is owned by player already
            if self.board.is_owned_by(name, position):
                return False
            # is owned by opponent
            else:
                opponent_name = self.board.get_owner_name(position)
                rent = self.board.get_rent(position, dice_roll)
                self.board.add_player_cash(opponent_name, rent)
                self.board.add_player_cash(name, -rent)
                return False

    def _execute_purchase(self, name, position, y):
        ev_before = self.board.get_evaluation(name)
        if y[0] > y[1]:
            self.board.purchase(name, position)
            self.board.add_player_cash(name, -self.board.get_purchase_amount(position))
        ev_after = self.board.get_evaluation(name)

        return self._get_reward(name, "purchase", ev_before, ev_after)

    def _execute_up_down_grade(self, name, action):
        """Executes the the given upgrade/downgrade move

        The decision (y) is executed by the player (name). First the decision
        format is in two halves of the given y list. The first half is the
        property that should be upgraded or unmortgaged. The second half is
        the property that should be downgrade or mortgaged. The difference
        between (un)mortgaging and (down/up)grading is determined automatically,
        which ensures the outcome space to be smaller.

        The decision is split into their upgrade/downgrade halves.The index of
        where the array is 1 is used in conjunction with the board index to find
        the property that should be changed. The action is carried out on the
        board and the reward is calculated based on the results. The result is
        returned as well as if the upgrade/downgrade action can be carried out
        again.

        Parameters
        --------------------
        name : str
            The name of the player that carries out the action

        y : numpy.ndarray
            The decision array that should executed upon. The dimension should
            be (57), where the first 28 entries should be upgrade and the latter
            half should be downgrade, and the last should be to do nothing

        Returns
        --------------------
        Reward : float
            The reward the player gets based on the action that was input

        Continue : boolean
            If the player can carry out an upgrade/downgrade option again. This
            is false if an action cannot be carried out or no property is
            selected to be changed

        """
        upgrade = action[0]
        downgrade = action[1]

        ev_before = self.board.get_evaluation(name)

        if upgrade[-1] == 1:
            pass
        else:
            upgrade_list = self.board.get_prop_list_from_actiontable(
                "up_down_grade", "upgrade", upgrade
            )

            for position in upgrade_list:
                if self.board.can_upgrade(name, position):
                    self.board.add_player_cash(
                        name, -self.board.get_upgrade_amount(position)
                    )
                    self.board.upgrade(name, position)
                # if position can be unmortgaged
                elif self.board.can_unmortgage(name, position):
                    self.board.add_player_cash(
                        name, -self.board.get_mortgage_amount(position)
                    )
                    self.board.unmortgage(name, position)

        if downgrade[-1] == 1:
            pass
        else:
            downgrade_list = self.board.get_prop_list_from_actiontable(
                "up_down_grade", "downgrade", downgrade
            )

            for position in downgrade_list:
                if self.board.can_downgrade(name, position):
                    self.board.add_player_cash(
                        name, self.board.get_downgrade_amount(position)
                    )
                    self.board.downgrade(name, position)
                elif self.board.can_mortgage(name, position):
                    self.board.add_player_cash(
                        name, self.board.get_mortgage_amount(position)
                    )
                    self.board.mortgage(name, position)

        ev_after = self.board.get_evaluation(name)

        return self._get_reward(name, "up_down_grade", ev_before, ev_after)

    def _get_values_from_trade_offer(self, trade_offer):
        offer_cash = self._binary_to_cash(trade_offer[0:14], neg=False)
        take_cash = self._binary_to_cash(trade_offer[14:28], neg=False)
        offer_prop = trade_offer[28:56]
        take_prop = trade_offer[56:84]

        return offer_cash, take_cash, offer_prop, take_prop

    def _evaluate_trade_offer(self, offer, name, opponent):

        offer_cash, take_cash, offer_prop, take_prop = self._get_values_from_trade_offer(
            offer
        )
        offer_prop_value = self.board.get_total_value_owned(name, offer_prop)
        take_prop_value = self.board.get_total_value_owned(opponent, take_prop)

        limit = max(offer_cash + offer_prop_value, take_cash + take_prop_value)
        reward = (
            (take_cash + take_prop_value) - (offer_cash + offer_prop_value)
        ) / limit

        return reward

    def _evaluate_trade_decision(self):

        pass

    def _execute_trade(self, offer, name, opponent):
        offer_cash, take_cash, offer_prop, take_prop = self._get_values_from_trade_offer(
            offer
        )
        self._transfer_cash(name, opponent, offer_cash)
        self._transfer_cash(opponent, name, take_cash)
        self._transfer_properties(name, opponent, offer_prop)
        self._transfer_properties(opponent, name, take_prop)

    def _get_reward(self, player, operation, ev_before, ev_after):
        rho, rho_mode = self.players[player].get_reward_scalars(operation)
        c1 = ev_before["cash"]
        c1 = 0 if c1 < 0 else c1
        c2 = ev_after["cash"]
        c2 = 0 if c2 < 0 else c2

        deg = (1.2 * c2 * rho - 1500) / (1000 + c2 * rho)

        if rho_mode == 1:
            y1 = self.reward_scalars["cash"]
            y2 = self.reward_scalars["value"]
            y3 = self.reward_scalars["rent"]
            y4 = self.reward_scalars["monopoly"]

            v1 = ev_before["value"]
            r1 = ev_before["rent"]
            m1 = ev_before["monopoly"]

            v2 = ev_after["value"]
            r2 = ev_after["rent"]
            m2 = ev_after["monopoly"]

            return deg * (
                y1 * (c2 - c1) + y2 * (v2 - v1) + y3 * (r2 - r1) + y4 * (m2 - m1)
            )
        elif rho_mode == 2:
            if c2 - c1 == 0:
                return 0
            else:
                return deg * ((c2 - c1) / abs(c2 - c1))
        else:
            raise ValueError(f"mode {rho_mode} does not exist")


def get_game_controllers(pool, n_players, config=None):
    if len(pool) % n_players != 0:
        raise ValueError("Pool cannot be split into these segments")
    plan = np.array(sample(range(len(pool)), len(pool))).reshape(-1, n_players)
    bcs = []

    for game_ind in plan:
        if config is not None:
            bcs.append(
                GameController([pool[player_ind] for player_ind in game_ind], **config)
            )
        else:
            bcs.append(GameController([pool[player_ind] for player_ind in game_ind]))
    return bcs
