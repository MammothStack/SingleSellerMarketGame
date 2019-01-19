from math import pow
import pandas as pd
import numpy as np
from random import randrange, randint


class BoardInformation():
    """
    
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
        
        l = list(self._table["color"].unique())
        l.remove("black")
        l.remove("white")
        
        #self.prop_colors = l
        
    def _set_table(self, players):
        
        def make(player_color, index):
            owned = pd.Series(
                data=pd.np.zeros(len(index)), 
                name=player_color + ":owned",
                index=index,
                dtype="bool"
            )
            
            owned_nm = pd.Series(
                data=[-1 for i in range(len(index))],
                index=index, 
                name=player_color + ":owned:normal", 
                dtype="int8")
            
            canupgrade = pd.Series(
                data=pd.np.zeros(len(index)), 
                name=player_color + ":can_upgrade",
                index=index,
                dtype="bool"
            )
            
            canupgrade_nm = pd.Series(
                data=[-1 for i in range(len(index))],
                name=player_color + ":can_upgrade:normal",
                index=index,
                dtype="int8"
            )
            
            candowngrade = pd.Series(
                data=pd.np.zeros(len(index)), 
                name=player_color + ":can_downgrade",
                index=index,
                dtype="bool"
            )
            
            candowngrade_nm = pd.Series(
                data=[-1 for i in range(len(index))],
                name=player_color + ":can_downgrade:normal",
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
        return self._table.at[
            position, "can_purchase"
        ]
        
    def can_downgrade(self, name, position):
        return self._table.at[
            position, name + ":can_downgrade"
        ]
        
    def can_upgrade(self, name, position):
        return self._table.at[
            position, name + ":can_upgrade"
        ]
    
    def is_monopoly(self, position):
        return self._table.at[position, "monopoly_owned"]
        
    def _is_monopoly(self, name, color):
        owned = self._table.loc[
            self._table["color"] == color,
            name + ":owned"
        ].all()
        
        return owned
    
    def is_any_purchaseable(self):
        return self._table["can_purchase"].any()
    
    def is_actionfield(self, position):
        return position in self._fp_action
    
    def is_property(self, position):
        return position in self._fp_normal
    
    def is_special(self, position):
        return position in self._fp_special
    
    def _update_normal_binary(self, position, check_col, normal_col):
        if self._table.at[position, check_col]:
            self._table.at[position, normal_col] = 1
        else:
            self._table.at[position, normal_col] = -1
    
    def _update_normal_value_max(self, position, val_col, max_col, normal_col):
        val = self._table.at[position, val_col]
        halfmax = self._table.at[position, max_col] / 2
        self._table.at[position, normal_col] = (val - halfmax) / halfmax
    
    def _update_normalisation(self, name, position):
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
            position, "current_rent_amount", "rent_level:6", "current_rent_amount:normal"
        )
    
    def purchase(self, name, position):
        """ Sets the properties to purchase
        
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
        purchase a given property.
        
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
        if position == 12 or position == 28:
            return (self._table.at[position, "current_rent_amount"] / 7) * dice_roll
        else:
            return self._table.at[position, "current_rent_amount"]
    
    def is_owned_by(self, position, name):
        return self._table.at[position, name + ":owned"]
    
    def get_owner_name(self, position):
        s = [a + ":owned" for a in self._player_names]
        own = self._table.loc[position, s]
        if own.any():
            return own[own].index[0][:-6]
        else:
            return None
            
    def get_purchase_price(self, position):
        return self._table.at[position, "purchase_amount"]
    
    def get_level(self, position):
        return self._table.at[position, "level"]
    
    def get_property_name(self, position):
        if position in self._fp_action:
            return "Action field"
        return self._table.at[position, "name"]
    
    def get_action(self, position):
        var = self._action_fields[position]
        if type(var) == list:
            return var[randint(0, len(var)-1)]
        else:
            return var

    #Information getting
    def get_normalized_state(self, name):
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
    
    def get_table(self):
        return self._table
