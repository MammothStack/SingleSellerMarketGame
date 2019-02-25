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
        max_cash_limit=10000,
        max_turn=800,
        upgrade_limit=20,
        reinforce_config=None,
        dynamic_cash_equation=True
    ):
        self.players = {p.name: p for p in player_list}
        self.board = BoardInformation([p.name for p in player_list], max_cash_limit)

        if reinforce_config is None:
            path = os.path.join(os.path.dirname(__file__), 'config.ini')
            self.config = configparser.ConfigParser()
            self.config.read(path)
        else:
            self.config = None

        self.max_cash_limit = max_cash_limit
        self.dynamic_cash_equation = dynamic_cash_equation
        self.alive = True
        self.total_turn = 0
        self.max_turn = max_turn
        self.current_turn = 0
        self.num_players = len(player_list)
        self.upgrade_limit = upgrade_limit
        self.binary_pos = [8192, 4096, 2048, 1024, 512, 256,
            128, 64, 32, 16, 8, 4, 2, 1]
        self.binary_neg = [-1, -2, -4, -8, -16, -32, -64, -128,
            -256, -512, -1024, -2048, -4096, -8192]
        self.binary = self.binary_pos + self.binary_neg

        if starting_order is None:
            self.order = [p.name for p in player_list]
        else:
            num_order = random.sample(
                range(self.num_players), self.num_players)
            self.order = [player_list[i].name for i in num_order]



    def start_game(self,
        purchase=True,
        up_down_grade=True,
        trade=True,
        gather_results=False):
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

        gather_results : boolean (default=True)
            If at the end of the game the results of the games should be
            gathered and returned

        Returns
        --------------------
        result_dict : dict
            A dictionary of results where the keys are the players of the game
            and the values are a Pandas.Series object containing game
            information

        """

        self.operation_config = {
            "purchase" : purchase,
            "up_down_grade" : up_down_grade,
            "trade" : trade
        }

        while self.alive:
            #Runs through all three actions
            self._full_turn(self.order[self.current_turn])

            #Checks if any properties can still be bought. quit if none
            if up_down_grade == False and trade == False:
                if self.alive:
                    self.alive = self.board.is_any_purchaseable()

            #Checks that the game has not exceeded the turn limit
            if self.alive:
                self.alive = self.total_turn < self.max_turn

            #Sets the current turn
            if self.alive:
                self.current_turn = (self.current_turn + 1) % self.num_players
            else:
                #If the game is over then all AIs learn from the game
                for p in self.players.values():
                    p.learn()

            #Turn is incremented
            self.total_turn += 1

        if gather_results:
            result_dict = {}

            for p in self.players:
                o = self.board.get_amount_properties_owned(p)
                l = self.board.get_total_levels_owned(p)

                result_dict = {p: pd.Series(
                    data=[p,
                        self.players[p].cash,
                        o,
                        l/o,
                        self.total_turn,
                        self.players[p].get_training_data("purchase"),
                        self.players[p].get_training_data("up_down_grade"),
                        self.players[p].get_training_data("trade_offer"),
                        self.players[p].get_training_data("trade_decision")],
                    index=["name",
                        "cash",
                        "prop_owned",
                        "prop_average_level",
                        "turn_count",
                        "train_purchase",
                        "train_up_down_grade",
                        "train_trade_offer",
                        "train_trade_decision"],
                    name=p)}
            return result_dict

    def reset_game(self):
        """Resets all the game parameters so their default values

        Calls all players of the game to reset to their initial values
        as well as the turn counter and "alive" state of the board

        """
        for p in self.players.values():
            p.reset_player()

        self.board = BoardInformation([p for p in self.players.keys()])
        self.alive = True
        self.current_turn = 0
        self.total_turn = 0

    def _cash_to_binary(self, cash, neg=False):
        if cash > 16383:
            cash = 16383
        elif cash < -16383:
            cash = -16383

        if neg:
            if cash > 0:
                p = np.array([int(a) for a in list(np.binary_repr(cash, width=14))])
                n = np.zeros(14, dtype=int)
                return np.append(p,n).reshape(-1,1)

            elif cash < 0:
                p = np.zeros(14, dtype=int)
                n = np.array([int(a) for a in list(np.binary_repr(-1 * cash, width=14))])
                return np.append(p,list(reversed(n))).reshape(-1,1)
            else:
                return np.zeros(28, dtype=int).reshape(-1,1)
        else:
            if cash < 0:
                raise ValueError("Must select true for parameter neg")
            else:
                return np.array([int(a) for a in list(np.binary_repr(cash, width=14))])


    def _binary_to_cash(self, arr, neg=False):
        if len(arr.shape) == 2:
            arr = arr.reshape(-1)
        if neg:
            return np.sum(arr * self.binary_pos)
        else:
            return np.sum(arr * self.binary)


    def _get_x(self, name, opponent=None, offer=None):
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
             A one-dimensional array (393,)/(562,)

        """
        def get_state_for_player(name):
            p = self.players[name].position
            v = self.board.get_normalized_player_state(name)
            p_arr = np.full(len(v.index), 0)

            if p in v.index:
                p_arr[v.index.get_loc(p)] = 1

            return np.concatenate(
                (
                    [self.players[name].cash / self.max_cash_limit],
                    p_arr,
                    v.values.flatten("F")
                )
            )

        gen_state = self.board.get_normalized_general_state().values.flatten("F")

        pla_state = get_state_for_player(name)

        opp_state = []
        offer_state = []

        if opponent is not None:
            opp_state = get_state_for_player(opponent)

        if offer is not None:
            offer_state = offer

        return np.concatenate((offer, opp_state, pla_state, gen_state))

    def _get_y(self, name, operation, x, single=True):
        """Get a decision/prediction from the players for the given operation

        Input a player name and an operation for which a decision should be
        made. There is an option to include the opponent in the decision making
        decision, which is the case for trading.

        Parameters
        --------------------
        name : str
            The name of the player making the decision

        operation : str
            The name of the operation for which the decision should be made

        x : numpy.ndarray
            The x input for which the decision should be calculated

        single : boolean (default=True)
            Signifies if only one result can be true or if multiple choices
            can also be true

        Returns
        --------------------
        y : np.array
            Array of length n (where n is the length of the raw input),
            containing only 0 or 1 integers.

        """
        y_raw = self.players[name].get_decision(x, operation)
        y = np.zeros(len(y_raw))
        threshold = self.config.getfloat("Threshold", operation)

        if single:
            ind = np.argmax(y_raw)
            if y_raw[ind] >= threshold:
                y[ind] = 1
        else:
            ind = np.argwhere(y_raw >= threshold).flatten()
            np.put(y, ind, 1)

        return y

    def _get_dynamic_cash_reward(self, cash, risk_level, negative=False):
        """

        """
        cash = 0 if cash < 0 else cash

        if negative:
            return (1 / (((risk_level / 1500) * cash) + 0.5) - 1)
        else:
            return (-1 / (((risk_level / 1500) * cash) + 0.5) + 1)


    def _full_turn(self, name):
        if self.players[name].allowed_to_move:
            #Roll the dice
            d1, d2 = self._roll_dice()

            #Move the player to the new position
            new_pos = self._move_player(name, dice_roll=d1 + d2)

            #If player landed on action field
            if self.board.is_actionfield(new_pos):
                self._land_action_field(name, new_pos)
                purchase = False
            else:
                purchase = self._land_property(name, new_pos)

            if (self.operation_config["purchase"] and
                purchase and
                self.players[name].can_purchase):
                x = self._get_x(name)
                y = self._get_y(name, "purchase", x, True)
                reward = self._execute_purchase(name, new_pos, y)
                self.players[name].add_training_data("purchase", x, y, reward)

            #upgrade/downgrade
            cont = True
            count = 0
            if (self.operation_config["up_down_grade"] and
                self.players[name].can_up_down_grade):
                while cont and count < self.upgrade_limit:
                    x = self._get_x(name)
                    y = self._get_y(name, "up_down_grade", x, True)
                    reward, cont = self._execute_up_down_grade(name, y)
                    count += 1
                    self.players[name].add_training_data("up_down_grade",
                        x, y, reward)

            #trade
            if self.operation_config["trade"] and self.players[name].can_trade_offer:
                for opponent in self.players.keys():
                    if name != opponent and self.players[opponent].can_trade_decision:
                        x = self._get_x(name, opponent)
                        y = self._get_y(name, "trade_offer", x, single=False)
                        reward = self._evaluate_trade_offer(y, name, opponent)

                        x_opp = np.concatenate(y.reshape((-1,3), order="F"), x)
                        y_opp = self._get_y(opponent, "trade_decision", x, single=True)
                        reward_opp = -reward

                        if y_opp[0] == 1:
                            self.players[name].add_training_data("trade_offer",
                                x, y, reward)
                            self.players[name].add_training_data("trade_decision",
                                x_opp, y_opp, reward_opp)

        else:
            self.players[name].allowed_to_move = True

    def _land_action_field(self, name, position):
        #get the action from the position
        act = self.board.get_action(position)

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


    def _land_property(self, name, position):
        #If the property is purchaseable
        if self.board.can_purchase(name, position):
            return True

        #is owned
        else:
            #is owned by player already
            if self.board.is_owned_by(name, position):
                return False
            #is owned by opponent
            else:
                opponent_name = self.board.get_owner_name(position)
                rent = self.board.get_rent(position, d1 + d2)
                self.players[opponent_name].cash += rent
                self.players[name].cash -= rent
                return False

    def _execute_purchase(self, name, position, y):
        if y[0] == 1:
            self.board.purchase(name, position)
            self.players[name].cash -= self.board.get_purchase_amount(position)

            self.alive = self.players[name].cash >= 0

            if self.board.is_monopoly(position):
                reward = self._get_dynamic_cash_reward(
                    self.players[name].cash,
                    self.config.getfloat("dynamic_reward_risk_level", "PurchaseMonopoly"),
                    negative=False
                )
            else:
                reward = self._get_dynamic_cash_reward(
                    self.players[name].cash,
                    self.config.getfloat("dynamic_reward_risk_level", "PurchaseStandard"),
                    negative=False
                )
        else:
            reward = self._get_dynamic_cash_reward(
                self.players[name].cash - self.board.get_purchase_amount(position),
                self.config.getfloat("dynamic_reward_risk_level", "PurchaseNone"),
                negative=True
            )

        return reward

    def _execute_up_down_grade(self, name, y):
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
            be (56), where the first 28 entries should be upgrade and the latter
            half should be downgrade

        Returns
        --------------------
        Reward : float
            The reward the player gets based on the action that was input

        Continue : boolean
            If the player can carry out an upgrade/downgrade option again. This
            is false if an action cannot be carried out or no property is
            selected to be changed

        """
        split = int(len(y) / 2)
        upgrade = y[:split]
        downgrade = y[split:]

        if upgrade.sum() == 1:
            ind = np.argmax(upgrade)
            pos = self.board.index[np.argmax(upgrade)]

            #if position can even be upgraded
            if self.board.can_upgrade(name, pos):
                self.players[name].cash -= self.board.get_upgrade_amount(pos)
                self.board.upgrade(name, pos)
                reward = self._get_dynamic_cash_reward(
                    self.players[name].cash,
                    self.config.getfloat("dynamic_reward_risk_level", "Upgrade"),
                    negative=False
                )
                return reward, True

            #if position can be unmortgaged
            elif self.board.can_unmortgage(name, pos):
                self.players[name].cash -= self.board.get_mortgage_amount(pos)
                self.board.unmortgage(name, pos)
                reward = self._get_dynamic_cash_reward(
                    self.players[name].cash,
                    self.config.getfloat("dynamic_reward_risk_level", "Unmortgage"),
                    negative=False
                )
                return reward, True

            else:
                reward = self.config.getfloat("static_reward", "UpDownNonExec")
                return reward, False

        elif downgrade.sum() == 1:
            ind = np.argmax(downgrade)
            pos = self.board.index[np.argmax(downgrade)]

            if self.board.can_downgrade(name, pos):
                self.players[name].cash += self.board.get_downgrade_amount(pos)
                self.board.downgrade(name, pos)
                reward = self._get_dynamic_cash_reward(
                    self.players[name].cash,
                    self.config.getfloat("dynamic_reward_risk_level", "Downgrade"),
                    negative=True
                )
                return reward, True

            elif self.board.can_mortgage(name, pos):
                self.players[name].cash += self.board.get_mortgage_amount(pos)
                self.board.mortgage(name, pos)
                reward = self._get_dynamic_cash_reward(
                    self.players[name].cash,
                    self.config.getfloat("dynamic_reward_risk_level", "Mortgage"),
                    negative=True
                )
                return reward, True

            else:
                reward = self.config.getfloat("static_reward", "UpDownNonExec")
                return reward, False
        else:
            reward = self.config.getfloat("static_reward", "UpDownNone")
            return reward, False

    def _evaluate_trade_offer(self, offer, name, opponent):
        offer_cash = self._binary_to_cash(trade_offer[0:14], neg=False)
        take_cash = self._binary_to_cash(trade_offer[14:28], neg=False)
        offer_prop = self.board.get_total_value_owned(name, trade_offer[28:56])
        take_prop = self.board.get_total_value_owned(opponent, trade_offer[56:84])

        limit = max(offer_cash + offer_prop, take_cash + take_prop)
        reward = ((take_cash + take_prop) - (offer_cash + offer_prop)) / limit
        return reward

    def _evaluate_trade_decision(self):

        pass

    def _execute_trade(self, offer, name, opponent):
        self._transfer_cash(
            name, opponent, self._binary_to_cash(offer[0:14], neg=False))
        self._transfer_cash(
            opponent, name, self._binary_to_cash(offer[14:28], neg=False))
        self._transfer_properties(name, opponent, offer[28:56])
        self._transfer_properties(opponent, name, offer[56:84])

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

    def _transfer_cash(self, from_player, to_player, amount):
        if amount < 0:
            raise ValueError("Amount cannot be less than 0")

        self.players[from_player].cash -= amount
        self.players[to_player].cash += amounts

    def _transfer_properties(self,
        from_player,
        to_player,
        properties):
        """Transfers properties between two players

        """

        if set(properties).issubset(
            set(self.board.get_all_properties_owned(from_player))):
            cash_gained = 0
            #Get the colors for the properties list
            colors = set([self.board.get_property_color(p) for p in properties])
            properties_to_downgrade = [
                self.board.get_properties_from_color(c) for c in colors
            ]
            #Downgrade all properties to level 1
            for property in properties_to_downgrade:
                while self.board.get_level(property) > 1:
                    cash_gained += self.board.get_downgrade_amount(property)
                    self.board.downgrade(from_player, property)

            for property in properties:
                self.board.remove_ownership(from_player, property)
                self.board.purchase(to_player, property)

            return cash_gained
        else:
            raise ValueError("Cannot transfer properties that are not owned")
