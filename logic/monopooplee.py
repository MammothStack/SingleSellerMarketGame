import random
from random import randrange
import pandas as pd
import numpy as np
from functools import lru_cache as cache
from sklearn.preprocessing import StandardScaler

class Player():
    def __init__(self, color, cash=1500, position=0, model=None):
        self.color = color
        self.position = position
        self.cash = cash
        self.networth = 0
        self.alive = True
        self.model = model
        self.valid_decisions = 0
        self.invalid_decisions = 0
        
    def makeDecision(self, field_info, player_info):
        if self.model:
            
            field_arr = field_info.values.flatten("F")
            player_arr = player_info.values.flatten()
            bias = np.array(([1]))
            state = np.concatenate((player_arr, field_arr, bias))
            pred = self.model.predict(np.array((state,)))
            return pred[0]
        else:
            option = [0] * 56
            user_input = input("pick")
            
            #print(user_input)

            try:
                option[field_info.index.get_loc(int(user_input))] = 1
                return option
            except ValueError:
                return option


class Board():
    
    def __init__(self, listOfPlayers, move_restrictions=None):
        
        self.available_houses = 40
        self.available_hotels = 8
        self.players = {p.color: p for p in listOfPlayers}
        self.turn_count = 0
        self.current_player_turn = list(self.players.keys())[0]
        self.gameAlive = True
        self.field_positions_normal = [1,3,6,8,9,11,13,14,16,18,19,21,23,24,26,27,29,31,32,34,37,39]
        self.field_positions_special = [5,12,15,25,28,35]
        self.field_positions_action = [0,2,4,7,10,17,20,22,30,33,36,38]
        action_field_order = ["go","community chest","income tax","chance",
                              "jail","community chest","free parking","chance",
                              "go to jail","community chest","chance","luxury tax"]
        self.action_fields = dict(zip(self.field_positions_action, action_field_order))
        self.action_field_options = {
            "go to jail": "goto:10",
            "community chest": [20,30,40,50,80,100],
            "chance": [-30,-40,-50,-50,-80,-100,-150, 20,30,40,50,80,100,150, "goto:10","goto:0", "goto:20"],
            "go": None,
            "income tax": -200,
            "luxury tax": -100,
            "free parking": "free parking",
            "jail": None
        }
        self.move_restrictions = move_restrictions
        
        self.scaler_value = StandardScaler().fit([[0],[1400]])
        self.scaler_rent = StandardScaler().fit([[0],[2000]])
        self.scaler_updown_cost = StandardScaler().fit([[0],[200]])
        self.scaler_updown = StandardScaler().fit([[0],[1]])
        self.scaler_position = StandardScaler().fit([[0],[39]])
        self.scaler_cash = StandardScaler().fit([[0],[5000]])
        
        self.free_parking_cash = 0
        self._setTables()
        
    def _setTables(self):
        
        def _makeOwnerTable(df, level=True):
            positions = list(df["position"])
            if level:
                cols = ["level"]+[p for p in self.players] + ["value"]
            else:
                cols = [p for p in self.players] + ["value"]
                
            zeros = pd.np.zeros((len(positions), len(cols)))
            temp = pd.DataFrame(zeros, columns=cols, dtype="int64")
            
            temp_con = pd.concat([df, temp], axis=1)
            
            return temp_con.set_index("position")

        self.properties_pricetable = pd.read_csv("Monopooplee/data/properties_pricelist.csv")
        self.properties_pricetable.set_index("position", inplace=True)
          
        property_table_normal = pd.read_csv("Monopooplee/data/properties_normal.csv")
        property_table_special = pd.read_csv("Monopooplee/data/properties_special.csv")
        
        self.properties = _makeOwnerTable(property_table_normal)
        self.properties_special = _makeOwnerTable(property_table_special, level=False)

        
    def canUpgrade(self, player_color, position):
        if position in self.field_positions_normal:
            
            prop = self.properties.loc[position]
            prop_color = self.properties.loc[self.properties["color"] == prop["color"]]

            if prop["level"] == 0:
                return position == self.getPlayerPosition(player_color)
            else:
                #Checks if the property is owned at all or by the player
                owned = prop[player_color]

                #Checks that the level is below max level
                below_max_level = prop["level"] < 6

                #Checks all other properties are owned by the player
                all_other_color_props_owned = prop_color[player_color].all()

                #Checks that enough buildings are available
                if prop["level"] < 5 and prop["level"] > 0:
                    enough_buildings = self.available_houses > 0
                elif prop["level"] == 5:
                    enough_buildings = self.available_hotels > 0
                else:
                    enough_buildings = True

                return owned and below_max_level and all_other_color_props_owned and enough_buildings
            
        elif position in self.field_positions_special:
            return self.getOwnerColor(position) is None and position == self.getPlayerPosition(player_color)
        else:
            raise KeyError
        
    def canDowngrade(self, player_color, position):
        if position in self.field_positions_normal:
            prop = self.properties.loc[position]
            prop_color = self.properties.loc[self.properties["color"] == prop["color"]]

            #Checks if the property is owned at all or by the player
            owned = prop[player_color]

            prop_color_without = prop_color.loc[prop_color["name"] != prop["name"]]
            temp = prop_color_without["level"].map(lambda x: x <= 1)
            other_props_no_buildings = temp.all()

            #Checks that enough buildings are available
            if prop["level"] == 6:
                enough_buildings = self.available_houses >= 4
            else:
                enough_buildings = True

            if prop["level"] == 0:
                return False
            elif prop["level"] == 1:
                return owned
            else:
                return owned and other_props_no_buildings and enough_buildings
        
        elif position in self.field_positions_special:
            
            return self.getOwnerColor(position) == player_color
        
        else:
            raise KeyError
        
    def upgradeProperty(self, player_color, position):
        level = self.getPropertyLevel(position)

        upgrade_price = self.getUpgradeCost(position)

        if level >= 1 and level <= 4:
            self.available_houses -= 1
        elif level == 5:
            self.available_houses += 4
            self.available_hotels -= 1
            
        self.properties.at[position, "value"] += upgrade_price
        self.changePlayerCashAmount(player_color, -upgrade_price)

        self.properties.at[position, "level"] = level + 1
        self.properties.at[position, player_color] = 1
            
    def downgradeProperty(self, player_color, position):
        level = self.getPropertyLevel(position)

        downgrade_amount = self.getDowngradeAmount(position)

        if level == 6:
            self.available_houses -= 4
            self.available_hotels += 1
        elif level < 6 and level >= 2:
            self.available_houses += 1

        self.changePlayerCashAmount(player_color, downgrade_amount)
        self.properties.at[position, "level"] = level - 1
        self.properties.at[position, "value"] -= self.getUpgradeCost(position)

        if level == 1:
            self.properties.at[position, player_color] = 0
          
    def setOwnerSpecialProperty(self, player_color, position, buysell="buy"):
        d = {"buy":1, "sell":0, True:1, False:1}
        
        if position not in self.field_positions_special:
            raise KeyError

        self.properties_special.at[position, player_color] = d[buysell]

        if self.properties_special.loc[position, "color"] == "white":
            if d[buysell]:
                amount = -150
                nw = 150
            else:
                amount = 75
                nw = 0
        elif self.properties_special.loc[position, "color"] == "black":
            if d[buysell]:
                amount = -200
                nw = 200
            else:
                amount = 100
                nw = 0
                
        self.changePlayerCashAmount(player_color, amount)
        self.properties_special.at[position, "value"] = nw
        
    def transferProperties(self, from_player_color, to_player_color, properties="all"):
        if type(properties) == list:
            bool_arr_prop = [pos in properties and self.properties.loc[pos, from_player_color] for pos in self.properties.index]
            bool_arr_prop_spec = [pos in properties and self.properties_special.loc[pos, from_player_color] for pos in self.properties_special.index]
            
        elif properties == "all":
            bool_arr_prop = [self.properties[from_player_color] == 1]
            bool_arr_prop_spec = [self.properties_special[from_player_color] == 1]
        else:
            raise Error
            
        self.properties[from_player_color][bool_arr_prop] = 0
        self.properties_special[from_playe_color][bool_arr_prop_spec] = 0
        if to_player_color is None:
            self.properties["level"][bool_arr_prop] = 0
            self.properties["value"][bool_arr_prop] = 0
            self.properties_special["level"][bool_arr_prop_spec] = 0
            self.properties_special["value"][bool_arr_prop_spec] = 0
        else:
            self.properties[to_player_color][bool_arr_prop] = 1
            self.properties_special[to_player_color][bool_arr_prop_spec] = 1
        
        
    """
    LANDING ON THE FIELDS NO CHOICE
    """
    
    def landOpponentField(self, player_color, position, dice_roll, verbose=1):
        if position not in self.field_positions_normal and position not in self.field_positions_special:
            raise KeyError
        
        owner_color = self.getOwnerColor(position)
        cost = self.getRentCost(position, dice_roll)
        
        if verbose == 2:
            print("landed on " + owner_color + "'s property and has to pay " + str(cost))
        
        self.transferCashP2P(from_player=player_color, 
                             to_player=owner_color, 
                             amount=cost)
                    
    def landActionField(self, player_color, position, verbose=1):
        if position not in self.field_positions_action:
            raise KeyError
            
        action = self.action_field_options[self.action_fields[position]]
        if isinstance(action, list):
            action = action[randrange(0,len(action))]
        
        if action is None:
            if verbose == 2:
                print("No action")
            pass
        
        elif type(action) == int:
            if action < 0:
                self.addToFreeParking(-action)
            self.changePlayerCashAmount(player_color, action)
            
            if verbose == 2:
                print(player_color + " gets/pays: " + str(action))
                
        elif type(action == str):
            if ":" in action:
                s = action.split(":")
                if s[0] == "goto":
                    self.movePlayer(player_color, position, int(s[1]))
                    
                    if verbose == 2:
                        print(player_color + " moved to " + s[1])
            elif action == "free parking":
                fpc = self.getFreeParkingCash()
                self.changePlayerCashAmount(player_color, fpc)
                
                if verbose == 2:
                    print(player_color + " landed on free parking and receives " + str(fpc))

        else:
            raise KeyError
        
    def getOwnerColor(self, position):
        if position in self.field_positions_normal:
            ser = self.properties.loc[position, list(self.players.keys())]
        elif position in self.field_positions_special:
            ser = self.properties_special.loc[position, list(self.players.keys())]
        else:
            raise KeyError
        try:
            return ser[ser == 1].index[0]
        except IndexError:
            return None
    
    @cache(maxsize=None)
    def getPropertyName(self, position):
        if position in self.field_positions_normal:
            return self.properties.loc[position, "name"]
        elif position in self.field_positions_special:
            return self.properties_special.loc[position, "name"]
        elif position in self.field_positions_action:
            return self.action_fields[position]
        else:
            raise Error
        
    def changePlayerCashAmount(self, player_color, amount):
        self.getPlayerByColor(player_color).cash += amount
        
    def getPlayerCash(self, player_color):
        return self.getPlayerByColor(player_color).cash
        
    def getPlayerNetworth(self, player_color):
        pw = self.properties.loc[self.properties[player_color] == 1]
        psw =self.properties_special.loc[self.properties_special[player_color] == 1]
        
        return pw["value"].sum() + psw["value"].sum()
    
    @cache(maxsize=None)
    def getPlayerByColor(self, color):
        return self.players[color]
    
    def getPlayerDecision(self, player_color, field_info, player_info):
        
        b = ["upgrade:" + str(x) for x in field_info.index]
        s = ["downgrade:" + str(x) for x in field_info.index]
        
        data = self.getPlayerByColor(player_color).makeDecision(field_info, player_info)
        
        return pd.Series(data, index=b + s, name="Decision")
    
    def isPlayerAlive(self, player_color):
        return self.getPlayerByColor(player_color).alive
    
    def setPlayerStatus(self, player_color, alive=True):
        self.getPlayerByColor(player_color).alive = alive
        
    def updatePlayerStatus(self, player_color):
        self.setPlayerStatus(player_color, self.getPlayerCash(player_color) > 0)
            
    def transferCashP2P(self, from_player, to_player, amount):
        self.getPlayerByColor(from_player).cash -= amount
        self.getPlayerByColor(to_player).cash += amount
        
    def getPropertyLevel(self, position):
        if position in self.field_positions_normal:
            return self.properties.loc[position, "level"]
        else:
            raise KeyError
              
    """
    GETTING RENT COST NORMAL/SPECIAL PROPERTIES
    """
    
    def getRentCost(self, position, dice_roll=7):
        if position in self.field_positions_normal:
            return self._getRentCostNormal(position, self.getPropertyLevel(position))
        elif position in self.field_positions_special:
            opponent_color = self.getOwnerColor(position)
        
            if opponent_color is None:
                return 0

            if self.properties_special.loc[position, "color"] == "white":
                df = self.properties_special.loc[self.properties_special["color"]=="white"]
                owned = df[opponent_color].sum()
                return self._getRentCostUtil(owned, dice_roll)

            elif self.properties_special.loc[position, "color"] == "black":
                df = self.properties_special.loc[self.properties_special["color"]=="black"]
                owned = df[opponent_color].sum()
                return self._getRentCostRailroad(owned)
            else:
                raise KeyError

        else:
            raise KeyError
            
    @cache(maxsize=None)
    def _getRentCostNormal(self, position, level):
        if level == 0:
            return 0
        else:
            return self.properties_pricetable.loc[position, "rent_level_" + str(level)]
    
    @cache(maxsize=None)
    def _getRentCostUtil(self, owned, dice_roll):
        if owned == 1:
            cost = 4 * dice_roll
        elif owned == 2:
            cost = 10 * dice_roll
        else:
            raise KeyError
            
        return cost
    
    @cache(maxsize=None)
    def _getRentCostRailroad(self, owned):
        if owned == 1:
            cost = 25
        elif owned == 2:
            cost = 50
        elif owned == 3:
            cost = 100
        elif owned == 4:
            cost = 200
        else:
            raise KeyError
        
        return cost
    
    
    """
    GETTING Upgrade/Downgrade cost
    """
    
    def getUpgradeCost(self, position):
        if position in self.field_positions_normal:
            return self._getUpgradeCostNormal(position, self.getPropertyLevel(position))
        elif position in self.field_positions_special:
            return self._getUpgradeCostSpecial(position)
        else:
            raise KeyError
            
    @cache(maxsize=None)
    def _getUpgradeCostNormal(self, position, level):
        if level == 0:
            return self.properties_pricetable.loc[position, "purchase_price"]
        else:
            return self.properties_pricetable.loc[position, "upgrade_price"]
    
    @cache(maxsize=None)
    def _getUpgradeCostSpecial(self, position):
        if self.properties_special.loc[position, "color"] == "white":
            return 150
        elif self.properties_special.loc[position, "color"] == "black":
            return 200
            
    
    def getDowngradeAmount(self, position):
        if position in self.field_positions_normal:
            return self._getDowngradeAmountNormal(position, self.getPropertyLevel(position))
        elif position in self.field_positions_special:
            return self._getDowngradeAmountSpecial(position)
        else:
            raise KeyError
            
    @cache(maxsize=None)
    def _getDowngradeAmountNormal(self, position, level):
        if level == 0:
            return self.properties_pricetable.loc[position, "purchase_price"] / 2
        else:
            return self.properties_pricetable.loc[position, "upgrade_price"] / 2
        
    @cache(maxsize=None)
    def _getDowngradeAmountSpecial(self, position):
        if self.properties_special.loc[position, "color"] == "white":
            return 75
        elif self.properties_special.loc[position, "color"] == "black":
            return 100

    
    """
    FREE PARKING
    """
    #Add cash to free parking
    def addToFreeParking(self, amount):
        self.free_parking_cash += amount

    #retrieve the free parking cash, sets it to 0
    def getFreeParkingCash(self):
        cash = self.free_parking_cash
        self.free_parking_cash = 0
        return cash
 

    def nextTurn(self):
        self.turn_count += 1
        self.current_player_turn = list(self.players.keys())[self.turn_count % len(self.players)]

    
    def rollDice(self):
        if self.move_restrictions is None:
            return randrange(1,7), randrange(1,7)
        else:
            return randrange(self.move_restrictions[0],self.move_restrictions[1])
    
    def solePlayerAlive(self):
        i = 0
        for p in self.players:
            if self.isPlayerAlive(p):
                i += 1
        return i == 1
    
    def getPlayerPosition(self, player_color):
        return self.players[player_color].position
    
    def getNewPosition(self, old_position, dice_roll):
        return (old_position + dice_roll) % 40
        
    def movePlayer(self, player_color, old_position, new_position):
        if new_position < old_position:
            self.changePlayerCashAmount(player_color, 200)
        self.players[player_color].position = new_position
        
    
    def start(self, verbose=0, max_turn=1000):
        game_alive = True
        intervals = [max_turn * y for y in [0.25,0.5,0.75,1]]
        
        if verbose == 2:
            print("The game has started")
        
        while game_alive:
            
            if verbose == 2:
                if self.turn_count in intervals:
                    percentage = self.turn_count / max_turn * 100
                    print("Game is " + str(percentage) + "% of max turn")

            go_again = self.executeTurn(self.current_player_turn, verbose)
            
            while go_again:
                
                go_again = self.executeTurn(self.current_player_turn, verbose)
            
            if self.turn_count == max_turn:
                game_alive = False
            
            self.nextTurn()
            
            if self.solePlayerAlive():
                game_alive = False
                
        if verbose == 1 or verbose == 2:
            print("Game finished")
            for player in self.players:
                print(player + 
                      " Cash: " + 
                      str(self.getPlayerCash(player)) + 
                      " Networth: " + 
                      str(self.getPlayerNetworth(player)) + 
                      " Alive: " + 
                      str(self.isPlayerAlive(player)))
                
        
        
    def executeDecision(self, player_color, decision, threshold=0.5, verbose=0):
        dec = decision.idxmax()
        if verbose == 2:
            print(player_color + " chose " + dec + " with confidence: " + str(decision[dec]))
        
        if decision[dec] < threshold:
            if verbose == 2:
                print(dec + " not above threshold")
            return False
        
        s = dec.split(":")
        position = int(s[1])

        if s[0] == "upgrade":
            if verbose == 2:
                print("upgrading: " + str(position))
            if position in self.field_positions_normal:
                self.upgradeProperty(player_color, position)
            elif position in self.field_positions_special:
                self.setOwnerSpecialProperty(player_color, position, "buy")

        elif s[0] == "downgrade":
            if verbose == 2:
                print("downgrading: " + str(position))
            if position in self.field_positions_normal:
                self.downgradeProperty(player_color, position)
            elif position in self.field_positions_special:
                self.setOwnerSpecialProperty(player_color, position, "sell")
        else:
            raise KeyError
        return True
        
    def validateDecision(self, player_color, decision, field_info, threshold=0.5):
        #print(decision.round(3))
        var = decision.idxmax()
        
        if decision[var] < threshold:
            return True
        
        if len(decision.loc[decision == decision.max()]) > 1:
            return False
        
        s = var.split(":")
        
        col = player_color + ":" + s[0]
                
        return field_info.loc[int(s[1]), col] == 1
        
    def executeTurn(self, player_color, verbose=0):
        
        if verbose == 2:
            print("It is " + player_color + "'s turn")
        
        #Check if the player is alive else throw error
        if self.isPlayerAlive(player_color) == False:
            if verbose == 2:
                print(player_color + "is out of the game")
            return False
        
        #Get old position
        old_position = self.getPlayerPosition(player_color)
        
        if verbose == 2:
            print("Old position: " + str(old_position) + ", " + self.getPropertyName(old_position))
        
        #roll the dice
        if self.move_restrictions is None:
            d1, d2 = self.rollDice()
        else:
            d1 = self.rollDice()
            d2 = 0
            
        if verbose == 2:
            print("Rolled: " + str(d1) + ", " + str(d2))
        
        #Check if the dice are the same and set the go_again variable
        go_again = d1 == d2
        dice_roll = d1 + d2
        
        #get the new position from the old positino and dice roll
        new_position = self.getNewPosition(old_position, dice_roll)
        
        if verbose == 2:
            print("Went to: " + str(new_position) + ", " + self.getPropertyName(new_position))
        
        #move the player to the new position
        self.movePlayer(player_color, old_position, new_position)
        
        owner_color = None
        
        if new_position in self.field_positions_normal or new_position in self.field_positions_special:
			
            owner_color = self.getOwnerColor(new_position)
            
            if verbose == 2:
                print("Field owned by: " + str(owner_color))
            
            if player_color == owner_color:
                if verbose == 2:
                    print(player_color + " owns this property. Nothing happens")
            elif owner_color is None:
                if verbose == 2:
                    #print("This property is owned by nobody")
                    print("Cash: " + str(self.getPlayerCash(player_color)))
                
                fi, pi = self.getGamestate(player_color)
                decision = self.getPlayerDecision(player_color, fi, pi)
                
                #print(decision)
                valid = bool(self.validateDecision(player_color, decision, fi))
                if valid:
                    self.getPlayerByColor(player_color).valid_decisions += 1
                    if verbose == 2:
                        print("Valid decision")
                    self.executeDecision(player_color, decision, verbose=verbose)
                else:
                    self.getPlayerByColor(player_color).invalid_decisions += 1
                    if verbose == 2:
                        print("Invalid decision")
            else:	
                self.landOpponentField(player_color, new_position, dice_roll, verbose=verbose)
				        
        #Check if the position is an action field
        elif new_position in self.field_positions_action:
            self.landActionField(player_color, new_position, verbose)
        
        #If its not any of those then there is an issue and an error is raised
        else:
            raise Error
            
        #self.updatePlayerStatus(player_color)
        
        self.upgradeDowngradeLoop(player_color, verbose)
        
        if self.getPlayerCash(player_color) < 0:
            self.setPlayerStatus(player_color, False)
            if owner_color == player_color or owner_color is None:
                self.transferProperties(player_color, None)
            else:
                self.transferProperties(player_color, owner_color)
        return go_again
        
    def upgradeDowngradeLoop(self, player_color, verbose=0):
        loop = True
        while loop:
            if verbose == 2:
                print("Cash: " + str(self.getPlayerCash(player_color)))
                
            fi, pi = self.getGamestate(player_color)
            
            if self.getPlayerByColor(player_color).model is None:
                print(fi.loc[fi[player_color + ":upgrade"] == 1, player_color + ":upgrade_cost",])
                print(fi.loc[fi[player_color + ":downgrade"] == 1, player_color + ":downgrade_amount"])
            decision = self.getPlayerDecision(player_color, fi, pi)
            valid = self.validateDecision(player_color, decision, fi)
            if valid:
                self.getPlayerByColor(player_color).valid_decisions += 1
                if verbose == 2:
                    print("Valid decision")
                loop = self.executeDecision(player_color, decision, verbose=verbose)
            else:
                self.getPlayerByColor(player_color).invalid_decisions += 1
                break
            
            #self.updatePlayerStatus(player_color)
            #if self.isPlayerAlive(player_color) == False:
            #    break
    
    def getGamestate(self, player_color):       
        fields = self._getFieldState(self.properties, self.properties_special, player_color)     
        
        player_info = [self.getPlayerCash(player_color), self.getPlayerNetworth(player_color), self.getPlayerPosition(player_color)]
            
        player_state = pd.Series(player_info, index=["cash","networth","position"])
        
        #print(player_state)
        rent_list = [player_color + ":rent_cost"]
        
        updown_cost_list = [player_color + ":upgrade_cost", 
                            player_color + ":downgrade_amount"]
        
        updown_list = [player_color, player_color + ":upgrade", player_color + ":downgrade"]
        
        fields[["value"]] = self.scaler_value.transform(fields[["value"]])
        fields[rent_list] = self.scaler_rent.transform(fields[rent_list])
        fields[updown_cost_list] = self.scaler_updown_cost.transform(fields[updown_cost_list])
        fields[updown_list] = self.scaler_updown.transform(fields[updown_list])
        player_state["position"] = self.scaler_position.transform(player_state["position"])
        player_state["cash"] = self.scaler_cash.transform(player_state["cash"])
        player_state["networth"] = self.scaler_cash.transform(player_state["networth"])
        
        return fields[updown_list + rent_list + updown_cost_list], player_state
    
    #@cache(maxsize=None)
    def _getFieldState(self, properties, special, player_color):
        pn = properties.copy()
        ps = special.copy()

        pn.drop(columns=["level", "name","color"], inplace=True)
        ps.drop(columns=["name", "color"], inplace=True)
        
        fields = pd.concat([pn, ps])
        fields.sort_index(inplace=True)
        
        fields[player_color + ":upgrade"] = fields.apply(
            lambda x: int(self.canUpgrade(player_color, x.name)), axis=1)
        
        fields[player_color + ":upgrade_cost"] = fields.apply(
            lambda x: self.getUpgradeCost(x.name) if x[player_color + ":upgrade"] else 0, axis=1)
        
        fields[player_color + ":downgrade"] = fields.apply(
            lambda x: int(self.canDowngrade(player_color, x.name)), axis=1)
        
        fields[player_color + ":downgrade_amount"] = fields.apply(
            lambda x: self.getDowngradeAmount(x.name) if x[player_color + ":downgrade"] else 0, axis=1)
        
        fields[player_color + ":rent_cost"] = fields.apply(
            lambda x: self.getRentCost(x.name), axis=1)
        
        return fields
    
    def __repr__(self):
        properties = pprint.pformat(self.properties)
        string = "properties: " + properties + "\n"
        string = string + "available houses:%s\navailable hotels:%s" % (self.available_houses, self.available_hotels)
        
        return "<Board \n" + string + ">"

    def __str__(self):
        properties = pprint.pformat(self.properties)
        return "Board" % (properties, self.owner, self.level)
