from math import pow
import pandas as pd
import numpy as np
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

    Attributes
    --------------------
    available_houses : int
        amount of the houses that are available to purchase

    available_hotels : int
        amount of the hotels that are available to purchase

    free_parking_cash : int
        amount of cash that is located on the free parking field

    Methods
    --------------------
    can_purchase(name, position)
        Returns if the property at position can be purchaseable

    can_downgrade(name, position)
        Returns if the property at position can be downgraded

    can_upgrade(name, position)
        Returns if the property at position can be upgraded

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

    get_purchase_price(position)
        Returns the purchase price of the property at the position

    get_level(position)
        Returns the current level of the property at the position

    get_property_name(position):
        Returns the name of the property at the position

    get_action(position):
        Returns the action of the action field at the position

    get_normalized_state(name):
        Returns the normalized state that is flattened for ML algorithms

    get_state():
        Returns a DataFrame that shows all information of the board

    Examples
    --------------------

    """
    def __init__(self, player_names):

        self._player_names = player_names
        self.available_houses = 40
        self.available_hotels = 8
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

        #l = list(self._table["color"].unique())
        #l.remove("black")
        #l.remove("white")
        #self.prop_colors = l

    def _set_table(self, players):
        """Creates the board information table

        Reads the csv file from the git repository. It sets the proper index
        of the table as well as the proper data types used by the
        individual columns

        Parameters
        --------------------
        players : list
            A list of the players as str that are playing on the board

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
            owned = pd.Series(
                data=pd.np.zeros(len(index)),
                name=name + ":owned",
                index=index,
                dtype="bool"
            )

            owned_nm = pd.Series(
                data=[-1 for i in range(len(index))],
                index=index,
                name=name + ":owned:normal",
                dtype="int8")

            canupgrade = pd.Series(
                data=pd.np.zeros(len(index)),
                name=name + ":can_upgrade",
                index=index,
                dtype="bool"
            )

            canupgrade_nm = pd.Series(
                data=[-1 for i in range(len(index))],
                name=name + ":can_upgrade:normal",
                index=index,
                dtype="int8"
            )

            candowngrade = pd.Series(
                data=pd.np.zeros(len(index)),
                name=name + ":can_downgrade",
                index=index,
                dtype="bool"
            )

            candowngrade_nm = pd.Series(
                data=[-1 for i in range(len(index))],
                name=name + ":can_downgrade:normal",
                index=index,
                dtype="int8"
            )

            return pd.concat(
                [owned,
                 canupgrade,
                 candowngrade,
                 owned_nm,
                 canupgrade_nm,
                 candowngrade_nm],
                axis=1)

        table = pd.read_csv("Monopooplee/data/fields.csv")
        table.set_index("position", inplace=True)
        table = table.astype(
            {'value':np.int16,
             'value:normal':np.float,
             'value:max':np.int16,
             'monopoly_owned':np.bool,
             "monopoly_owned:normal":np.int8,
             'can_purchase':np.bool,
             'can_purchase:normal':np.int8,
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


    def can_purchase(self, name, position):
        """Returns if the property at position can be purchaseable

        Parameters
        --------------------
        name : str
            The name of the player who wants to purchase the property

        position : int
            The position of the property on the board

        Examples
        --------------------
        >>>board.can_purchase("red", 1)
        True
        >>>board.purchase("red", 1)
        >>>board.can_purchase("red", 1)
        False

        """
        return self._table.at[
            position, "can_purchase"
        ]

    def can_downgrade(self, name, position):
        """Returns if the property at position can be downgraded

        Parameters
        --------------------
        name : str
            The name of the player who wants to downgrade the property

        position : int
            The position of the property on the board

        Examples
        --------------------
        >>>board.can_downgrade("red", 1)
        True
        >>>board.downgrade("red", 1)
        >>>board.can_downgrade("red", 1)
        False

        """
        return self._table.at[
            position, name + ":can_downgrade"
        ]

    def can_upgrade(self, name, position):
        """Returns if the property at position can be upgraded

        Parameters
        --------------------
        name : str
            The name of the player who wants to upgrade the property

        position : int
            The position of the property on the board

        Examples
        --------------------
        >>>board.can_upgrade("red", 1)
        True
        >>>board.downgrade("red", 1)
        >>>board.can_upgrade("red", 1)
        False

        """
        return self._table.at[
            position, name + ":can_upgrade"
        ]

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
        return self._table.at[position, "monopoly_owned"]

    def _is_monopoly(self, name, color):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """
        owned = self._table.loc[
            self._table["color"] == color,
            name + ":owned"
        ].all()

        return owned

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

    def is_owned_by(self, position, name):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """
        return self._table.at[position, name + ":owned"]

    def is_actionfield(self, position):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """
        return position in self._fp_action

    def is_property(self, position):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """
        return position in self._fp_normal

    def is_special(self, position):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """
        return position in self._fp_special

    def _update_normal_binary(self, position, check_col, normal_col):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """
        if self._table.at[position, check_col]:
            self._table.at[position, normal_col] = 1
        else:
            self._table.at[position, normal_col] = -1

    def _update_normal_value_max(self, position, val_col, max_col, normal_col):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """
        val = self._table.at[position, val_col]
        halfmax = self._table.at[position, max_col] / 2
        self._table.at[position, normal_col] = (val - halfmax) / halfmax

    def _update_normalisation(self, name, position):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """

        #owned
        self._update_normal_binary(
            position, name + ":owned", name + ":owned:normal")

        #can ugrade
        self._update_normal_binary(
            position, name + ":can_upgrade", name + ":can_upgrade:normal")

        #can downgrade
        self._update_normal_binary(
            position, name + ":can_downgrade", name + ":can_downgrade:normal")

        #monopoly owned
        self._update_normal_binary(
            position, "monopoly_owned", "monopoly_owned:normal")

        #can purchase
        self._update_normal_binary(
            position, "can_purchase", "can_purchase:normal")

        #value
        self._update_normal_value_max(
            position, "value", "value:max", "value:normal")

        #current rent
        self._update_normal_value_max(
            position,
            "current_rent_amount",
            "rent_level:6",
            "current_rent_amount:normal"
        )

    def purchase(self, name, position):
        """Sets property at the position to "purchased" by the name

        Method for controlling the board properties that need to be set
        when a property is purchased. This method works for both normal
        and special properties.

        Sets the following values for the initial purchase  of the property

            Owned
                the Owned flag is set for the player

            can purchase
                flag to purchase is set to false

            can downgrade
                the flag to downgrade is set to to true

            current rent amount
                The current rent amount is set to level 1

            level
                The level of the property is set to 1

            monopoly status
                Checks the monopoly level and sets if true

        The ownership needs to be indicated to show which player owns the
        property. This goes in conjunction with setting the purchasability
        for a given property. This is to ensure that only one person can
        purchase a given property. At the end the normalized values are
        also updated.


        Parameters
        --------------------

        Examples
        --------------------

        """

        color = self._table.at[position, "color"]

        #owned
        self._table.at[
            position, name + ":owned"
        ] = True

        #can_purchase
        self._table.at[
            position, "can_purchase"
        ] = False

        #can_downgrade
        self._table.at[
            position, name + ":can_downgrade"
        ] = True

        #value
        self._table.at[
            position, "value"
        ] = self._table.at[position, "purchase_amount"]

        if position in self._fp_special:
            self._update_special_field(name, position, color)
        else:
            #current_rent_amount
            self._table.at[
                position, "current_rent_amount"
            ] = self._table.at[position, "rent_level:1"]

            #level
            self._table.at[
                position, "level"
            ] = 1

            is_mono = self._is_monopoly(name, color)
            #update monopoly status
            if is_mono:
                self._table.loc[
                    self._table["color"] == color,
                    ["monopoly_owned", name + ":can_upgrade"]
                ] = True

        self._update_normalisation(name, position)

    def mortgage(self, name, position):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """

        #value
        self._table.at[
            position, "value"
        ] = self._table.at[
            position, "mortgage_amount"
        ]

        #can downgrade
        self._table.at[
            position, name + ":can_downgrade"
        ] = False

        #can upgrade
        self._table.at[
            position, name + ":can_upgrade"
        ] = True

        #current_rent_amount
        self._table.at[
            position, "current_rent_amount"
        ] = 0

        if position in self._fp_normal:
            #level
            self._table.at[
                position, "level"
            ] = 0

        self._update_normalisation(name, position)

    def unmortgage(self, name, position):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """

        #value
        self._table.at[
            position, "value"
        ] = self._table.at[
            position, "purchase_amount"
        ]

        #can downgrade
        self._table.at[
            position, name + ":can_downgrade"
        ] = True

        if position in self._fp_special:
            #can upgrade
            self._table.at[
                position, name + ":can_upgrade"
            ] = False

            #current_rent_amount
            self._update_special_field(
                name,
                position,
                self._table.at[position, "color"]
            )
        else:
            #can upgrade
            self._table.at[
                position, name + ":can_upgrade"
            ] = True

            #current_rent_amount
            self._table.at[
                position, "current_rent_amount"
            ] = self._table.at[
                position, "rent_level:1"
            ]

            #level
            self._table.at[
                position, "level"
            ] = 1

        self._update_normalisation(name, position)


    def upgrade(self, name, position):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """

        #value
        self._table.at[
            position, "value"
        ] = self._table.at[
            position, "value"
        ] + self._table.at[
            position, "upgrade_amount"
        ]

        #level
        new_level = self._table.at[position, "level"] + 1
        self._table.at[position, "level"] = new_level
        if new_level == 6:
            self._table.at[position, name + ":can_upgrade"] = False

        #houses and hotels
        if new_level == 6:
            self.available_houses += 4
            self.available_hotels -= 1
        else:
            self.available_houses -= 1

        #current rent amount
        self._table.at[
            position, "current_rent_amount"
        ] = self._table.at[
            position, "rent_level:" + str(new_level)
        ]

        #update upgrade status
        self._update_can_upgrade()

        #update downgrade status
        self._update_can_downgrade()

        self._update_normalisation(name, position)

    def downgrade(self, name, position):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """

        #value
        self._table.at[
            position, "value"
        ] = self._table.at[
            position, "value"
        ] - self._table.at[
            position, "upgrade_amount"
        ]

        #level
        new_level = self._table.at[position, "level"] - 1
        self._table.at[position, "level"] = new_level

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

        #update upgrade status
        self._update_can_upgrade()

        #update downgrade status
        self._update_can_downgrade()

        self._update_normalisation(name, position)



    def _update_can_upgrade(self):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """

        #if owned and monopoly exists
        for name in self._player_names:
            self._table.loc[
                (self._table["monopoly_owned"] == True) &
                (self._table[name + ":owned"] == True) &
                (self._table["level"] < 6),
                name + ":can_upgrade"
            ] = True

        #if no houses exist, props that would have houses
        #for next upgrade are set to False
        if self.available_houses == 0:
            self._table.loc[
                (self._table["level"] > 0) &
                (self._table["level"] < 5),
                [n + ":can_upgrade" for n in self._player_names]
            ] = False

        #if no hotels exist props with level 5 cant upgrade
        if self.available_hotels == 0:
            self._table.loc[
                (self._table["level"] == 5),
                [n + ":can_upgrade" for n in self._player_names]
            ] = False

    def _update_can_downgrade(self):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """

        #if owned and monopoly exists
        if ~self._table["can_purchase"].all():
            for name in self._player_names:
                self._table.loc[
                    (self._table[name + ":owned"] == True) &
                    (self._table["level"] > 0),
                    name + ":can_downgrade"
                ] = True

        #if less than 4 houses exist
        if self.available_houses < 4:
            self._table.loc[
                (self._table["level"] == 6),
                [n + ":can_downgrade" for n in self._player_names]
            ] = False

    def _update_special_field(self, name, position, color):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """

        bool_arr = (self._table["color"] == color) & (self._table[name + ":owned"] == True)
        no = np.sum(bool_arr)
        if color == "black":
            self._table.loc[bool_arr, "current_rent_amount"] = 12.5 * pow(2, no)
        elif color == "white":
            if no == 1:
                self._table.loc[bool_arr, "current_rent_amount"] = 4 * 7
            elif no == 2:
                self._table.loc[bool_arr, "current_rent_amount"] = 10 * 7

    def get_rent(self, position, dice_roll):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """
        if position == 12 or position == 28:
            return (self._table.at[position, "current_rent_amount"] / 7) * dice_roll
        else:
            return self._table.at[position, "current_rent_amount"]

    def get_owner_name(self, position):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """
        s = [a + ":owned" for a in self._player_names]
        own = self._table.loc[position, s]
        if own.any():
            return own[own].index[0][:-6]
        else:
            return None

    def get_purchase_price(self, position):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """
        return self._table.at[position, "purchase_amount"]

    def get_level(self, position):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """
        return self._table.at[position, "level"]

    def get_property_name(self, position):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """
        if position in self._fp_action:
            return "Action field"
        return self._table.at[position, "name"]

    def get_action(self, position):
        """
        Parameters
        --------------------

        Examples
        --------------------

        """
        var = self._action_fields[position]
        if type(var) == list:
            return var[randint(0, len(var)-1)]
        else:
            return var

    #Information getting
    def get_normalized_state(self, name):
        """Returns the normalized state that is flattened for ML algorithms
        Parameters
        --------------------

        Examples
        --------------------

        """
        l = [name + ":owned:normal",
             name + ":can_upgrade:normal",
             name + ":can_downgrade:normal",
             "monopoly_owned:normal",
             "value:normal",
             "can_purchase:normal",
             "purchase_amount:normal",
             "mortgage_amount:normal",
             "upgrade_amount:normal",
             "downgrade_amount:normal",
             "current_rent_amount:normal"]

        return self._table[l].values.flatten("F")

    def get_state(self):
        """Returns a DataFrame that shows all information of the board

        The information returned pertains to all the information that can be
        seen by all players, which includes ownership and possible upgrade.
        parameter. It also shows the general state of the board for example
        if properties can be purchased, upgraded, how many houses are on it
        etc.

        """
        l = ["position",
             "name",
             "color",
             "monopoly_owned",
             "value",
             "can_purchase",
             "purchase_amount",
             "mortgage_amount",
             "upgrade_amount",
             "downgrade_amount",
             "current_rent_amount",
             "level"]

        return self._table[l]