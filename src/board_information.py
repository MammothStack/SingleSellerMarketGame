from math import pow
import pandas as pd
import numpy as np
import os
from random import randrange, randint


class BoardInformation():
    """Stores and handles all information of the board and game

    This class is responsible for initializing a pandas Dataframe that
    holds all the information that pertains to the state of properties
    and the ownership of these in relation to players. This table also
    includes data on the price of property purchase amounts and upgrade
    amounts.

    The Board is initialized with a list of player names, which is used
    to set the table with the relevant player information. It also
    initializes the available houses, hotels, free parking cash, the
    location of the normal, special, and action fields.

    The class gives several methods on manipulating the board through
    player actions.

    Parameters
    --------------------
    player_names : list
        A list of the players as str that are playing on the board

    max_cash_limit : int
        The maximum cash value for unto which other amounts will be normalized

    available_houses : int
        The starting amount of houses for the game

    available_hotels : int
        The starting amount of hotels for the game

    Attributes
    --------------------
    available_houses : int
        amount of the houses that are available to purchase

    available_hotels : int
        amount of the hotels that are available to purchase

    free_parking_cash : int
        amount of cash that is located on the free parking field

    index : list
        A list of the indices of the generated table

    prop_colors : list
        A list of the colors of all the properties

    Methods
    --------------------
    can_purchase(name, position)
        Returns if the property at position can be purchaseable

    can_downgrade(name, position)
        Returns if the property at position can be downgraded

    can_upgrade(name, position)
        Returns if the property at position can be upgraded

    can_mortgage(name, position)
        Returns if the property at position can be mortgaged

    is_monopoly(name, position)
        Returns if the property at position is part of a monopoly

    is_any_purchaseable()
        Returns if any property is still available to purchase

    is_owned_by(position, name)
        Returns if the property at position is owned by the player by name

    is_actionfield(position)
        Returns if the given position is an actionfield

    is_property(position)
        Returns if the given position is a property

    is_special(position)
        Returns if the given position is a special property

    purchase(name, position)
        Sets property at the position to "purchased" by the name

    mortgage(name, position)
        Mortgages the property at the position by the player by name

    unmortgage(name, position)
        Unmortgages the property at the position by the player by name

    upgrade(name, position)
        Upgrades the property at the position by the player by name

    downgrade(name, position)
        Downgrades the property at the position by the player by name

    get_rent(positon, dice_roll)
        Returns the calculated rent of the property at the position

    get_owner_name(position)
        Returns the player name of the owner of the property

    get_purchase_amount(position)
        Returns the purchase price of the property at the position

    get_mortgage_amount(position)
        Returns the amount it takes to mortgage an unmortgage the property

    get_upgrade_amount(position)
        Returns the amount it takes to upgrade the property

    get_downgrade_amount(position)
        Returns the amount it takes to downgrade the property

    get_level(position)
        Returns the current level of the property at the position

    get_property_name(position):
        Returns the name of the property at the position

    get_action(position):
        Returns the action of the action field at the position

    get_normalized_state(name):
        Returns the normalized state that is flattened for ML algorithms

    """
    def __init__(self,
        player_names,
        max_cash_limit=10000,
        available_houses=40,
        available_hotels=8):

        if type(player_names) != list:
            raise ValueError("Given value must be a list with names")

        if not player_names:
            raise ValueError("List cannot be empty")

        if len(player_names) > 8:
            raise BoardError("Cannot be more than 8 players")

        if len(player_names) != len(set(player_names)):
            raise BoardError("Cannot have the same player twice")

        if max_cash_limit < 2000:
            raise BoardError("Cannot have a cash_limit below the maximum value of the board")

        self._max_cash_limit = max_cash_limit
        self._player_names = player_names
        self.available_houses = available_houses
        self.available_hotels = available_hotels
        self.free_parking_cash = 0
        self._fp_normal = [1,3,6,8,9,11,13,14,16,18,19,21,23,
                           24,26,27,29,31,32,34,37,39]
        self._fp_special = [5,12,15,25,28,35]
        self._fp_action = [0,2,4,7,10,17,20,22,30,33,36,38]
        self._action_fields = {
            0:None,
            2:[20,20,20,30,30,40,50,100],
            4:-200,
            7:[-30,-40,-50,-50,-80,-100,-150, 20,
               30,40,50,80,100, ("goto", 0),("goto", 10), ("goto", 20)],
            10:None,
            17:[20,20,20,30,30,40,50,100],
            20:"free parking",
            22:[-30,-40,-50,-50,-80,-100,-150, 20,
                30,40,50,80,100, ("goto", 0),("goto", 10), ("goto", 20)],
            30:("goto", 10),
            33:[20,20,20,30,30,40,50,100],
            36:[-30,-40,-50,-50,-80,-100,-150, 20,
                30,40,50,80,100, ("goto", 0),("goto", 10), ("goto", 20)],
            38:-100
        }

        self._table = self._set_table(player_names)
        self.index = list(self._table.index)

        l = list(self._table["color"].unique())
        l.remove("black")
        l.remove("white")
        self.prop_colors = l

    def _set_table(self, players):
        """Creates the board information table

        Reads the csv file from the git repository. It sets the proper index
        of the table as well as the proper data types used by the
        individual columns

        Parameters
        --------------------
        players : list
            A list of the players as str that are playing on the board

        max_cash_limit : int
            A limit to which all values are capped and normalized

        Examples
        --------------------

        """

        def make(name, index):
            """Makes a DataFrame pertaining to player specific information

            Parameters
            --------------------
            name : str
                The name of the player

            index : array, list
                The index of the board

            Examples
            --------------------

            """
            categories = [
                ":owned",
                ":can_upgrade",
                ":can_downgrade",
                ":can_mortgage",
                ":can_unmortgage"]

            l = [
                pd.Series(
                    data=np.zeros(len(index)),
                    name=name + category,
                    index=index,
                    dtype="bool"
            ) for category in categories]

            return pd.concat(l,axis=1)

        path = os.path.join(os.path.dirname(__file__), 'fields.csv')

        table = pd.read_csv(path)
        table.set_index("position", inplace=True)
        table["purchase_amount:normal"] = table["purchase_amount"] / self._max_cash_limit
        table["mortgage_amount:normal"] = table["mortgage_amount"] / self._max_cash_limit
        table["upgrade_amount:normal"] = table["upgrade_amount"] / self._max_cash_limit
        table["downgrade_amount:normal"] = table["downgrade_amount"] / self._max_cash_limit

        table = table.astype(
            {'value':np.int16,
             'value:normal':np.float,
             'monopoly_owned':np.bool,
             'can_purchase':np.bool,
             'purchase_amount':np.int16,
             'purchase_amount:normal':np.float,
             'mortgage_amount':np.int16,
             'mortgage_amount:normal':np.float,
             'upgrade_amount':np.int16,
             'upgrade_amount:normal':np.float,
             'downgrade_amount':np.int16,
             'downgrade_amount:normal':np.float,
             'current_rent_amount':np.int16,
             'current_rent_amount:normal':np.float,
             'level':np.int8,
             'rent_level:0':np.int16,
             'rent_level:1':np.int16,
             'rent_level:2':np.int16,
             'rent_level:3':np.int16,
             'rent_level:4':np.int16,
             'rent_level:5':np.int16,
             'rent_level:6':np.int16}
        )

        for p in players:
            table = pd.concat([table, make(p, table.index)], axis=1)

        return table

    def can_purchase(self, position):
        """Returns if the property at position can be purchaseable

        Parameters
        --------------------
        position : int
            The position of the property on the board

        Raises
        --------------------
        BoardError
            When the position does not occur in the table

        Examples
        --------------------
        >>>board.can_purchase(1)
        True
        >>>board.purchase("red", 1)
        >>>board.can_purchase(1)
        False

        """
        if position not in self._table.index:
            raise BoardError("given position not in table index")
        return self._table.at[position, "can_purchase"]

    def can_downgrade(self, name, position):
        """Returns if the property at position can be downgraded

        Parameters
        --------------------
        name : str
            The name of the player who wants to downgrade the property

        position : int
            The position of the property on the board

        Raises
        --------------------
        BoardError
            When the position or name does not occur in the table

        Examples
        --------------------
        >>>board.can_downgrade("red", 1)
        True
        >>>board.downgrade("red", 1)
        >>>board.can_downgrade("red", 1)
        False

        """
        if name not in self._player_names:
            raise BoardError("Name does not exist in table")
        if position not in self._table.index:
            raise BoardError("position does not exist in table")

        return self._table.at[position, name + ":can_downgrade"]

    def can_upgrade(self, name, position):
        """Returns if the property at position can be upgraded

        Parameters
        --------------------
        name : str
            The name of the player who wants to upgrade the property

        position : int
            The position of the property on the board

        Raises
        --------------------
        BoardError
            When the position or name does not occur in the table

        Examples
        --------------------
        >>>board.can_upgrade("red", 1)
        True
        >>>board.downgrade("red", 1)
        >>>board.can_upgrade("red", 1)
        False

        """
        if name not in self._player_names:
            raise BoardError("Name does not exist in table")
        if position not in self._table.index:
            raise BoardError("position does not exist in table")
        return self._table.at[position, name + ":can_upgrade"]

    def can_mortgage(self, name, position):
        """Returns if the property at position can be mortgaged

        Parameters
        --------------------
        name : str
            The name of the player who wants to mortgage the property

        position : int
            The position of the property on the board

        Raises
        --------------------
        BoardError
            When the position or name does not occur in the table

        Examples
        --------------------
        >>>board.can_mortgage("red",1)
        True
        >>>board.mortgage("red",1)
        >>>board.can_mortgage("red",1)
        False
        >>>board.can_mortgage("blue",1)
        False

        """
        if name not in self._player_names:
            raise BoardError("Name does not exist in table")
        if position not in self._table.index:
            raise BoardError("position does not exist in table")
        return self._table.at[position, name + ":can_mortgage"]

    def can_unmortgage(self, name, position):
        """Returns if the property at position can be unmortgaged

        Parameters
        --------------------
        name : str
            The name of the player who wants to unmortgage the property

        position : int
            The position of the property on the board

        Raises
        --------------------
        BoardError
            When the position or name does not occur in the table

        """

        if name not in self._player_names:
            raise BoardError("Name does not exist in table")
        if position not in self._table.index:
            raise BoardError("position does not exist in table")
        return self._table.at[position, name + ":can_unmortgage"]

    def is_monopoly(self, position):
        """Returns if the property at position is part of a monopoly

        Parameters
        --------------------
        position : int
            The position of the property that should be checked for monopoly

        Examples
        --------------------
        >>>board.is_monopoly(1)
        False
        >>>board.purchase("red", 3)
        >>>board.is_monopoly(1)
        True

        """
        if position not in self._table.index:
            raise BoardError("position does not exist in table")
        return self._table.at[position, "monopoly_owned"]

    def _is_color_monopoly(self, name, color):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """
        if name not in self._player_names:
            raise BoardError("Name does not exist in table")

        owned = self._table.loc[
            self._table["color"] == color,
            name + ":owned"
        ].all()

        return owned

    def _is_any_in_color_mortgaged(self, color):
        """Returns true if any property in the given monopoly is mortgaged

        Counts the levels of all the properties in the given monopoly. If
        the sum of the levels is less than 3 than the
        """

        count = len(self._table.loc[self._table["color"] == color].index)
        return count > np.sum(
            self._table.loc[self._table["color"] == color, "level"])

    def is_any_purchaseable(self):
        """Returns if any property is still available to purchase

        Checks to see if any property can still be purchased by a player.

        Examples
        --------------------
        >>>board.is_any_purchaseable()
        True
        >>>board.purchase(1)
        >>>board.is_any_purchaseable()
        False

        """
        return self._table["can_purchase"].any()

    def is_owned_by(self, name, position):
        """Returns if the property at position is owned by the player by name

        Returns true if the given player owns the property at the given
        position. This will return false if the given property is owned by
        another player or is not owned at all.

        Parameters
        --------------------
        name : str
            The name of the player that should be checked for ownership

        position : int
            The position of the property on the board

        Examples
        --------------------
        >>>board = BoardInformation(["red", "blue"])
        >>>board.is_owned_by("red", 1)
        False
        >>>board.purchase("red", 1)
        >>>board.is_owned_by("red", 1)
        True
        >>>board.is_owned_by("blue", 1)
        False

        """
        return self._table.at[position, name + ":owned"]

    def is_actionfield(self, position):
        """Returns true if the given position is an action field"""
        return position in self._fp_action

    def is_property(self, position):
        """Returns true if the given position is an property field"""
        return position in self._fp_normal

    def is_special(self, position):
        """Returns true if the given position is an special property field"""
        return position in self._fp_special

    def _update_special_field(self, name, color):
        """Updates the special field data

        Updates the special field at the given position, which includes the
        changing the rent amount of the related fields of the same color.

        The white fields are updated with the average roll of two dice roll (7)

        Parameters
        --------------------
        name : str
            The name of the player

        color : str
            The color of the property that should be changed

        """

        bool_arr = (self._table["color"] == color) & (self._table[name + ":owned"] == True)
        amount_owned = np.sum(bool_arr)
        if color == "black":
            rent = 12.5 * pow(2, amount_owned)
            self._table.loc[bool_arr, "current_rent_amount"] = rent
            self._table.loc[
                bool_arr, "current_rent_amount:normal"
            ] = rent / self._max_cash_limit
        elif color == "white":
            if amount_owned == 1:
                self._table.loc[
                    bool_arr, "current_rent_amount"] = 4 * 7
                self._table.loc[
                    bool_arr, "current_rent_amount:normal"
                ] = (4 * 7) / self._max_cash_limit
            elif amount_owned == 2:
                self._table.loc[
                    bool_arr, "current_rent_amount"] = 10 * 7
                self._table.loc[
                    bool_arr, "current_rent_amount:normal"
                ] = (10 * 7) / self._max_cash_limit

    def remove_ownership(self, name, position):
        """Removes the ownership of the given player at the given position

        Parameters
        --------------------
        name : str
            the name of the player purchasing the property

        position : int
            the position of the property on the board

        Raises
        --------------------
        BoardError : if property cannot be sold by the player

        Examples
        --------------------

        """
        if self.is_owned_by(name, position) == False:
            raise BoardError(name + " does not own the property at " + str(position))

        #color of the property
        color = self._table.at[position, "color"]

        #owned
        self._table.at[position, name + ":owned"] = False

        #can_purchase
        self._table.at[position, "can_purchase"] = True

        #can_mortgage
        self._table.at[position, name + ":can_mortgage"] = False

        #can unmortgage
        self._table.at[position, name + ":can_unmortgage"] = False

        #can downgrade
        self._table.at[position, name +":can_downgrade"] = False

        #value
        self._table.at[position, "value"] = 0

        #Value normalized
        self._table.at[position, "value:normal"] = 0

        #level
        self._table.at[position, "level"] = 0

        if position in self._fp_special:
            self._update_special_field(name, color)
        else:
            #current_rent_amount
            self._table.at[position, "current_rent_amount"] = 0

            self._table.at[position, "current_rent_amount:normal"] = 0

            #update monopoly status
            if self._is_color_monopoly(name, color):
                #Set monopoly
                self._table.loc[
                    self._table["color"] == color,
                    ["monopoly_owned"]
                ] = False

                #if any in the monopoly are mortgaged then none can upgrade
                self._table.loc[
                    self._table["color"] == color,
                    [name + ":can_upgrade"]
                ] = False

    def purchase(self, name, position):
        """Sets property at the position to "purchased" by the player

        Method for controlling the board properties that need to be set
        when a property is purchased. This method works for both normal
        and special properties.

        Sets the following values for the initial purchase  of the property

            owned                   true
            can purchase            false
            can mortgage            true
            can unmortgaged         false
            can downgrade           false
            current rent amount     level 1
            level                   1
            monopoly status         if applicable
            can upgrade             if applicable

        The ownership needs to be indicated to show which player owns the
        property. This goes in conjunction with setting the purchasability
        for a given property. This is to ensure that only one person can
        purchase a given property. At the end the normalized values are
        also updated.

        Parameters
        --------------------
        name : str
            the name of the player purchasing the property

        position : int
            the position of the property on the board

        Raises
        --------------------
        BoardError : if property cannot be purchased by player

        Examples
        --------------------
        >>>board.can_purchase("red", 1)
        True
        >>>board.can_purchase("blue", 1)
        True
        >>>board.purchase("red", 1)
        >>>board.can_purchase("red", 1)
        False
        >>>board.can_purchase("blue", 1)
        False

        """

        if self.can_purchase(position) == False:
            raise BoardError(
                name + " cannot purchase the property at " + str(position))
        #color of the property
        color = self._table.at[position, "color"]

        #owned
        self._table.at[position, name + ":owned"] = True

        #can_purchase
        self._table.at[position, "can_purchase"] = False

        #can_mortgage
        self._table.at[position, name + ":can_mortgage"] = True

        #can unmortgage
        self._table.at[position, name + ":can_unmortgage"] = False

        #can downgrade
        self._table.at[position, name +":can_downgrade"] = False

        #value
        self._table.at[
            position, "value"
        ] = self._table.at[position, "purchase_amount"]

        self._table.at[
            position, "value:normal"
        ] = self._table.at[position, "value"] / self._max_cash_limit

        #level
        self._table.at[position, "level"] = 1

        if position in self._fp_special:
            self._update_special_field(name, color)
        else:
            #current_rent_amount
            self._table.at[
                position, "current_rent_amount"
            ] = self._table.at[position, "rent_level:1"]

            self._table.at[
                position, "current_rent_amount:normal"
            ] = self._table.at[position, "current_rent_amount"] / self._max_cash_limit

            #update monopoly status
            if self._is_color_monopoly(name, color):
                #Set monopoly
                self._table.loc[
                    self._table["color"] == color,
                    ["monopoly_owned"]
                ] = True

                #if any in the monopoly are mortgaged then none can upgrade
                self._table.loc[
                    self._table["color"] == color,
                    [name + ":can_upgrade"]
                ] = ~self._is_any_in_color_mortgaged(color)

    def mortgage(self, name, position):
        """Sets property at position to mortgaged by the player

        The property is mortgaged by the player and several values in the
        board table need to change in order for all configurations to work
        and adhere to the rule of the game. The following properties in the
        table are changed:

            value                  mortgage amount
            can downgrade          False
            can upgrade            False
            can mortgage           False
            can unmortgage         True
            current rent amount    0
            level                  0 if applicable

        Parameters
        --------------------
        name : str
            the name of the player mortgaging the property

        position : int
            the position of the property on the board

        Raises
        --------------------
        BoardError : if property cannot be morgaged by player

        Examples
        --------------------

        """

        if self.can_mortgage(name, position) == False:
            raise BoardError(
                name + " cannot mortgage the property at " + str(position))

        color = self._table.at[position, "color"]

        #value
        self._table.at[
            position, "value"
        ] = self._table.at[
            position, "mortgage_amount"
        ]

        self._table.at[
            position, "value:normal"
        ] = self._table.at[
            position, "value"
        ] / self._max_cash_limit

        #can downgrade
        self._table.at[position, name + ":can_downgrade"] = False

        #can upgrade with the same color (mortgaged props cant be developed)
        self._table.loc[
            self._table["color"] == color,
            [name + ":can_upgrade"]
        ] = False

        #can mortgage
        self._table.at[position, name + ":can_mortgage"] = False

        #can unmortgage
        self._table.at[position, name + ":can_unmortgage"] = True

        #current_rent_amount
        self._table.at[position, "current_rent_amount"] = 0

        self._table.at[position, "current_rent_amount:normal"] = 0

        #level
        self._table.at[position, "level"] = 0

    def unmortgage(self, name, position):
        """Sets property at position to unmortgaged by the player

        The property is unmortgaged by the player and several values in the
        board table need to change in order for all configurations to work
        and adhere to the rule of the game. The following properties in the
        table are changed:

            value                  purchase amount
            can downgrade          false
            can mortgage           true
            can unmortgage         false
            level                  1 if applicable
            can upgrade            if applicable
            current rent amount    rent level 1

        Parameters
        --------------------
        name : str
            the name of the player unmortgaging the property

        position : int
            the position of the property on the board

        Raises
        --------------------
        BoardError : if property cannot be unmortgaged by player

        Examples
        --------------------

        """

        if self.can_unmortgage(name, position) == False:
            raise BoardError(
                name + " cannot unmortgage the property at " + str(position))

        #color of the property
        color = self._table.at[position, "color"]

        #value
        self._table.at[
            position, "value"
        ] = self._table.at[
            position, "purchase_amount"
        ]

        self._table.at[
            position, "value:normal"
        ] = self._table.at[
            position, "value"
        ] / self._max_cash_limit

        #can downgrade
        self._table.at[position, name + ":can_downgrade"] = False

        #can mortgage
        self._table.at[position, name + ":can_mortgage"] = True

        #can unmortgage
        self._table.at[position, name + ":can_unmortgage"] = False

        #level
        self._table.at[position, "level"] = 1

        if position in self._fp_special:
            #can upgrade
            self._table.at[position, name + ":can_upgrade"] = False

            #current_rent_amount
            self._update_special_field(name, color)
        else:
            #can upgrade
            if self._is_color_monopoly(name, color):
                self._table.loc[
                    self._table["color"] == color,
                    [name + ":can_upgrade"]
                ] = ~self._is_any_in_color_mortgaged(color)

            #current_rent_amount
            self._table.at[
                position, "current_rent_amount"
            ] = self._table.at[
                position, "rent_level:1"
            ]

            self._table.at[
                position, "current_rent_amount:normal"
            ] = self._table.at[
                position, "current_rent_amount"
            ]

    def upgrade(self, name, position):
        """Upgrades the property at the position by the player by name

        The property is upgraded by the player and several values in the
        board table need to change in order for all configurations to work
        and adhere to the rule of the game. The following properties in the
        table are changed:

            value                  + upgrade cost
            can downgrade          true
            can mortgage           false (for all in monopoly)
            can unmortgage         false
            level                  + 1
            can upgrade            if applicable
            current rent amount    according rent level

        Parameters
        --------------------
        name : str
            the name of the player upgrade the property

        position : int
            the position of the property on the board

        Raises
        --------------------
        BoardError : if property cannot be upgraded by player

        Examples
        --------------------

        """

        if self.can_upgrade(name, position) == False:
            raise BoardError(
                name + " cannot upgrade the property at " + str(position))

        color = self._table.at[position, "color"]

        #value
        self._table.at[
            position, "value"
        ] = self._table.at[
            position, "value"
        ] + self._table.at[
            position, "upgrade_amount"
        ]

        self._table.at[
            position, "value:normal"
        ] = self._table.at[
            position, "value"
        ] / self._max_cash_limit

        #level
        new_level = self._table.at[position, "level"] + 1
        self._table.at[position, "level"] = new_level

        #upgrade
        self._table.at[position, name + ":can_upgrade"] = new_level != 6

        #downgrade
        self._table.at[position, name + ":can_downgrade"] = True

        #can mortgage, all properties of the same color
        self._table.loc[
            self._table["color"] == color,
            [name + ":can_mortgage"]
        ] = False

        #can unmortgage
        self._table.at[position, name + ":can_unmortgage"] = False

        #current rent amount
        self._table.at[
            position, "current_rent_amount"
        ] = self._table.at[
            position, "rent_level:" + str(new_level)
        ]

        self._table.at[
            position, "current_rent_amount:normal"
        ] = self._table.at[
            position, "current_rent_amount"
        ] / self._max_cash_limit

        n_house = self.available_houses
        n_hotel = self.available_hotels

        #houses and hotels
        if new_level == 6:
            self.available_houses += 4
            self.available_hotels -= 1
        else:
            self.available_houses -= 1

        if n_house == 0 and self.available_houses > 0:
            self._houses_to_available()
        if self.available_houses == 0:
            self._houses_to_unavailable()
        if n_hotel == 0 and self.available_hotels > 0:
            self._hotels_to_available()
        if self.available_hotels == 0:
            self._hotels_to_unavailable()

    def downgrade(self, name, position):
        """Downgrades the property at the position by the player by name

        The property is downgraded by the player and several values in the
        board table need to change in order for all configurations to work
        and adhere to the rule of the game. The following properties in the
        table are changed:

            value                  + upgrade cost
            can downgrade          true
            can mortgage           false (for all in monopoly)
            can unmortgage         false
            level                  + 1
            can upgrade            if applicable
            current rent amount    according rent level

        Parameters
        --------------------
        name : str
            the name of the player downgrade the property

        position : int
            the position of the property on the board

        Raises
        --------------------
        BoardError : if property cannot be downgraded by player

        Examples
        --------------------

        """

        if self.can_downgrade(name, position) == False:
            raise BoardError(
                name + " cannot downgrade the property at " + str(position))

        color = self._table.at[position, "color"]

        #value
        self._table.at[
            position, "value"
        ] = self._table.at[
            position, "value"
        ] - self._table.at[
            position, "upgrade_amount"
        ]

        self._table.at[
            position, "value:normal"
        ] = self._table.at[
            position, "value"
        ] / self._max_cash_limit

        #level
        new_level = self._table.at[position, "level"] - 1
        self._table.at[position, "level"] = new_level

        #can_downgrade
        self._table.at[position, name + ":can_downgrade"] = new_level > 1

        #can mortgage, all properties of the same color
        lvl_sum = np.sum(self._table.loc[
            self._table["color"] == color, ["level"]])

        prop_count = len(self._table.loc[self._table["color"] == color].index)

        self._table.loc[
            self._table["color"] == color,
            [name + ":can_mortgage"]
        ] = prop_count == lvl_sum

        #can unmortgage
        self._table.at[position, name + ":can_unmortgage"] = False

        n_house = self.available_houses
        n_hotel = self.available_hotels

        #houses and hotels
        if new_level == 5:
            self.available_hotels += 1
            self.available_houses -= 4
        elif new_level < 5:
            self.available_houses += 1

        #current rent amount
        self._table.at[
            position, "current_rent_amount"
        ] = self._table.at[
            position, "rent_level:" + str(new_level)
        ]

        self._table.at[
            position, "current_rent_amount:normal"
        ] = self._table.at[
            position, "current_rent_amount"
        ] / self._max_cash_limit

        if n_house == 0 and self.available_houses > 0:
            self._houses_to_available()
        if n_house > 0 and self.available_houses == 0:
            self._houses_to_unavailable()
        if n_hotel == 0 and self.available_hotels > 0:
            self._hotels_to_available()
        if n_hotel > 0 and self.available_hotels == 0:
            self._hotels_to_unavailable()

    def _houses_to_unavailable(self):
        for name in self._player_names:
            self._table.loc[
                (self._table[name + ":owned"] == True) &
                (self._table["level"] < 5),
                [name + ":can_upgrade"]
            ] = False

            self._table.loc[
                (self._table[name + ":owned"] == True) &
                (self._table["level"] == 6),
                [name + ":can_downgrade"]
            ] = False

    def _houses_to_available(self):
        for name in self._player_names:
            #if owned and monopoly exists
            self._table.loc[
                (self._table["monopoly_owned"] == True) &
                (self._table[name + ":owned"] == True),
                name + ":can_upgrade"
            ] = True

            #set false if at max level
            self._table.loc[
                (self._table[name + ":owned"] == True) &
                (self._table["level"] == 6),
                name + ":can_upgrade"
            ] = False

            #set false if any in the monopoly is mortgaged
            for color in self.prop_colors:
                if self._is_color_monopoly(name, color):
                    if self._is_any_in_color_mortgaged(color):
                        self._table.loc[
                            self._table["color"] == color,
                            [name + ":can_upgrade"]
                        ] = False

    def _hotels_to_unavailable(self):
        for name in self._player_names:
            self._table.loc[
                (self._table[name + ":owned"] == True) &
                (self._table["level"] == 5),
                [name + ":can_upgrade"]
            ] = False

    def _hotels_to_available(self):
        for name in self._player_names:
            self._table.loc[
                (self._table[name + ":owned"] == True) &
                (self._table["level"] == 5),
                [name + ":can_upgrade"]
            ] = True

            self._table.loc[
                (self._table[name + ":owned"] == True) &
                (self._table["level"] == 6),
                [name + ":can_downgrade"]
            ] = True

    def get_rent(self, position, dice_roll):
        """Returns the rent of the property

        Parameters
        --------------------
        position : int
            The position of the property

        dice_roll : int
            The roll of the dice that got to the position

        """
        if position == 12 or position == 28:
            return (self._table.at[position, "current_rent_amount"] / 7) * dice_roll
        else:
            return self._table.at[position, "current_rent_amount"]

    def get_owner_name(self, position):
        """Returns the name of the owner at the given position

        Parameters
        --------------------
        position : int
            The position of the property

        """
        s = [a + ":owned" for a in self._player_names]
        own = self._table.loc[position, s]
        if own.any():
            return own[own].index[0][:-6]
        else:
            return None

    def get_purchase_amount(self, position):
        """Returns the amount needed to purchase the property

        Parameters
        --------------------
        position : int
            The position of the property

        """
        return self._table.at[position, "purchase_amount"]

    def get_value(self, position):
        """Returns the value of the property

        Parameters
        --------------------
        position : int
            The position of the property

        """
        return self._table.at[position, "value"]

    def get_mortgage_amount(self, position):
        """Returns the amount received when mortgaging the property

        Parameters
        --------------------
        position : int
            The position of the property

        """
        return self._table.at[position, "mortgage_amount"]

    def get_upgrade_amount(self, position):
        """Returns the amount needed to upgrade the property

        Parameters
        --------------------
        position : int
            The position of the property

        """
        return self._table.at[position, "upgrade_amount"]

    def get_downgrade_amount(self, position):
        """Returns the amount received when downgrading the property

        Parameters
        --------------------
        position : int
            The position of the property

        """

        return self._table.at[position, "downgrade_amount"]

    def get_level(self, position):
        """Returns the level of the property

        Parameters
        --------------------
        position : int
            The position of the property

        """
        return self._table.at[position, "level"]

    def get_property_name(self, position):
        """Returns the name of the property

        Parameters
        --------------------
        position : int
            The position of the property

        """
        if position in self._fp_action:
            return "Action field"
        return self._table.at[position, "name"]

    def get_property_color(self, position):
        """Returns the color of the given property

        Parameters
        --------------------
        position : int
            The position of the property

        """
        if position in self._fp_action:
            return "Action field"
        return self._table.at[position, "color"]

    def get_action(self, position):
        """Get the action for current position

        Parameters
        --------------------
        position : int
            The position of the property

        """
        var = self._action_fields[position]
        if type(var) == list:
            return var[randint(0, len(var)-1)]
        else:
            return var

    def get_all_properties_owned(self, player_name):
        """Returns all the properties that the given player owns

        Returns a list of property location that the given player owns.

        Parameters
        --------------------
        player_name : str
            The name of the player for which the properties should be returned

        Returns
        --------------------
        properties : list
            A list of the all the properties location that the given player owns

        Examples
        --------------------
        >>>bi = BoardInformation(["red"])
        >>>bi.get_all_properties_owned("red")
        []
        >>>bi.purchase("red",1)
        >>>bi.get_all_properties_owned("red")
        [1]
        """

        return list(self._table.loc[self._table["owned"] == True].index)

    def get_amount_properties_owned(self, name):
        """Gets the total amount of properties owned by the given player

        Parameters
        --------------------
        name : str
            The name of the player whose properties should be counted

        Examples
        --------------------
        >>>board.get_amount_properties_owned("red")
        0
        >>>board.purchase(red, 1)
        >>>board.get_amount_properties_owned("red")
        1

        """
        return np.sum(self._table[name + ":owned"])

    def get_total_levels_owned(self, name):
        """Gets the total level of all owned properties by the given player

        Parameters
        --------------------
        name : str
            The name of the of the player whose properties should be counted

        Examples
        --------------------
        >>>board.get_total_levels_owned("red")
        5
        >>>board.upgrade("red", 1)
        >>>board.get_total_levels_owned("red")
        6

        """
        return self._table.loc[
            self._table[name + ":owned"] == True, "level"
        ].sum()

    def get_total_value_owned(self, name, properties=None):
        """Returns the total value of the properties owned by the player

        Returns the sum of all the properties owned by the given player. If
        a the properties parameter contains a list of specific properties then
        only those properties will be summed.

        Parameters
        --------------------
        name : str
            The name of the player for which the property values should be
            summmed

        properties : list (default=None)
            A list of specific properties for which the value should be summed

        Returns
        --------------------
        summed_value : int
            A sum of all the owned values given by the parameters

        """
        if properties is None:
            return np.sum(
                self._table.loc[self._table[name + ":owned"] == True, value])
        else:
            temp = self._table.loc[properties]
            return np.sum(temp.loc[temp[name + ":owned"] == True, value])

    def get_properties_from_color(self, color):
        """Returns the list of properties from the given color

        """
        return list(self._table.loc[self._table["color"] == color].index)

    #Information getting
    def get_normalized_state(self, name=None):
        """Returns the normalized state of the board

        It uses the given name to get player specific values from the table.
        This ensures no matter how many players are in the game. This method
        will always spit out the same table, which helps when training an
        AI that is supposed to be able to play against multiple players at
        the same time.

        The method will fetch the following columns from the table if the
        parameter name has the name of a player:
            owned
            can upgrade
            can downgrade
            can mortgage
            can unmortgage

        The method will fetch the following columns from the table if the
        paramter name is None:
            monpoly owned
            value
            can purchase
            purchase amount
            mortgage amount
            upgrade amount
            downgrade amount
            current rent amount

        since the table is 28 rows deep this results in a table of 28 x 5 or
        28 x 8

        Parameters
        --------------------
        name : str
            The name(s) of the player(s) for whom the normalized state should
            be fetched

        Examples
        --------------------

        """

        if name is not None:
            return self._table[
                [name + ":owned",
                 name + ":can_upgrade",
                 name + ":can_downgrade",
                 name + ":can_mortgage",
                 name + ":can_unmortgage"]]
        else:
            return self._table[[
                "monopoly_owned",
                "value:normal",
                "can_purchase",
                "purchase_amount:normal",
                "mortgage_amount:normal",
                "upgrade_amount:normal",
                "downgrade_amount:normal",
                "current_rent_amount:normal"]]


class BoardError(Exception):
    """Base class for board specific errors"""
    pass
