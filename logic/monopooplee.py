import random
from random import randrange
import pandas as pd


class Player():
    def __init__(self, color, cash=1500, position=0, model=None):
        self.color = color
        self.position = position
        self.cash = cash
        self.networth = 0
        self.alive = True
        self.model = model
        
    def makeDecision(self, gamestate):
        if self.model:
            return model.evaluate(gamestate)
        else:
            option = [0] * 57
            print(option)
            print(len(option))
            prop_choice = int(input("0-21=buy, 22-43=sell,44-49=buySpec, 50-55=sellSpec, 56 = pass"))
            print(prop_choice)
            option[prop_choice] = 1
            return option

class Board():
    
    def __init__(self, listOfPlayers):
        
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
            "community chest": [20,30,40,50,80,100,200],
            "chance": [-30,-40,-50,-50,-80,-100,-150, 20,30,40,50,80,100,200, "goto:10","goto:0", "goto:20"],
            "go": None,
            "income tax": -200,
            "luxury tax": -100,
            "free parking": "free parking",
            "jail": None
        }
        
        self.free_parking_cash = 0
        self._setTables()
        
    def _setTables(self):
        
        def _makeOwnerTable(df, level=True):
            positions = list(df["position"])
            if level:
                cols = ["level"]+[p for p in self.players]
            else:
                cols = [p for p in self.players]
                
            zeros = pd.np.zeros((len(positions), len(cols)))
            temp = pd.DataFrame(zeros, columns=cols, dtype="int64")
            
            temp_con = pd.concat([df, temp], axis=1)
            
            return temp_con.set_index("position")

        self.properties_pricetable = pd.read_csv("https://raw.githubusercontent.com/MammothStack/Monopooplee/master/properties_pricelist.csv")
        self.properties_pricetable.set_index("position", inplace=True)
          
        property_table_normal = pd.read_csv("https://raw.githubusercontent.com/MammothStack/Monopooplee/master/properties_normal.csv")
        property_table_special = pd.read_csv("https://raw.githubusercontent.com/MammothStack/Monopooplee/master/properties_special.csv")
        
        self.properties = _makeOwnerTable(property_table_normal)
        self.properties_special = _makeOwnerTable(property_table_special, level=False)

        
    def canUpgradeProperty(self, player_color, position):
        prop = self.properties.loc[position]
        prop_color = self.properties.loc[self.properties["color"] == prop["color"]]
                
        if prop["level"] == 0:
            return True
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
        
    def canDowngradeProperty(self, player_color, position):
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
        
    def increaseProperty(self, player_color, position):
        level = self.getPropertyLevel(position)

        upgrade_price = self.getUpgradeCost(position)

        if level >= 1 and level <= 4:
            self.available_houses -= 1
        elif level == 5:
            self.available_houses += 4
            self.available_hotels -= 1
            
        self.changePlayerNetworthAmount(player_color, upgrade_price)
        self.changePlayerCashAmount(player_color, -upgrade_price)

        self.properties.at[position, "level"] = level + 1
        self.properties.at[position, player_color] = 1
            
    def decreaseProperty(self, player_color, position):
        level = self.getPropertyLevel(position)

        downgrade_amount = self.getDowngradeAmount(position)

        if level == 6:
            self.available_houses -= 4
            self.available_hotels += 1
        elif level < 6 and level >= 2:
            self.available_houses += 1

        self.changePlayerCashAmount(player_color, downgrade_amount)
        self.properties.at[position, "level"] = level - 1
        
        nw_amount = self.getUpgradeCost(position)
        self.changePlayerNetworthAmount(player_color, -nw_amount)

        if level == 1:
            self.properties.at[position, player_color] = 0
            
    def canUpgradePropertySpecial(self, player_color, position):
        return self.getOwnerColor(position) is None
    
    def canDowngradePropertySpecial(self, player_color, position):
        return self.getOwnerColor(position) == player_color
            
    def setOwnerSpecialProperty(self, player_color, position, buysell="buy"):
        d = {"buy":1, "sell":0, True:1, False:1}
        
        if position not in self.field_positions_special:
            raise KeyError
        
        self.properties_special.at[position, player_color] = d[buysell]
        if self.properties_special[position, "color"] == "white":
            if d[buysell]:
                amount = -150
            else:
                amount = 75
        elif self.properties_special[position, "color"] == "black":
            if d[buysell]:
                amount = -200
            else:
                amount = 100
                
        self.changePlayerCashAmount(player_color, amount)
        
        
    """
    LANDING ON THE FIELDS NO CHOICE
    """
    def landOpponentProperty(self, player_color, position):
        if position not in self.field_positions_normal:
            raise KeyError

        self.transferCashP2P(from_player=player_color, 
                             to_player=self.getOwnerColor(position), 
                             amount=self.getRentCost(position))
        
    def landOpponentPropertySpecial(self, player_color, position, dice_roll):
        if position not in self.field_positions_special:
            raise KeyError
        
        self.transferCashP2P(from_player=player_color, 
                             to_player=self.getOwnerColor(position), 
                             amount=self.getRentCostSpecial(position, dice_roll))
                    
    def landActionField(self, player_color, position):
        if position not in self.field_positions_action:
            raise KeyError
            
        action = self.action_field_options[self.action_fields[position]]
        if isinstance(action, list):
            action = action[randrange(0,len(action))]
        
        if action is None:
            pass
        
        elif type(action) == int:
            if action < 0:
                self.addToFreeParking(-action)
            self.changePlayerCashAmount(player_color, action)
        elif type(action == str):
            if ":" in action:
                s = action.split(":")
                if s[0] == "goto":
                    self.movePlayer(player_color, s[1])
            elif action == "free parking":
                self.changePlayerCashAmount(player_color, self.getFreeParkingCash())

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
        
    def changePlayerNetworthAmount(self, player_color, amount):
        self.getPlayerByColor(player_color).networth += amount
        
    def getPlayerCash(self, player_color):
        return self.getPlayerByColor(player_color).cash
        
    def getPlayerNetworth(self, player_color):
        return self.getPlayerByColor(player_color).networth
    
    def getPlayerByColor(self, color):
        return self.players[color]
    
    def getPlayerDecision(self, player_color, gamestate):
        buy = ["buy:" + str(x) for x in self.field_positions_normal]
        buy_spec = ["buy:" + str(x) for x in self.field_positions_special]
        
        sell = ["sell:" + str(x) for x in self.field_positions_normal]
        sell_spec = ["sell:" + str(x) for x in self.field_positions_special]
        index = buy + sell + buy_spec + sell_spec + ["pass"]
		
        print(len(index))
        print(index)
        data = self.getPlayerByColor(player_color).makeDecision(gamestate)
		
        print(len(data))
        print(data)
		
        return pd.Series(data, index=index, name="Decision")
    
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
    
    def getRentCost(self, position):
        level = getPropertyLevel(position)
        
        if level == 0:
            return 0
        else:
            return self.properties_pricetable.loc[position, "rent_level_" + str(level)]
    
    def getRentCostSpecial(self, position, dice_roll=7):
        opponent_color = getOwnerColor(position)
        
        if opponent_color is None:
            return 0
        
        if self.properties_special[position, "color"] == "white":
            df = self.properties_special.loc[self.properties_special["color"]=="white"]
            owned = df[opponent_color].sum()
            if owned == 1:
                cost = 4 * dice_roll
            elif owned == 2:
                cost = 10 * dice_roll
            else:
                raise KeyError

        elif self.properties_special[position, "color"] == "black":
            df = self.properties_special.loc[self.properties_special["color"]=="black"]
            owned = df[opponent_color].sum()
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
        else:
            raise KeyError
        
        return cost
    
    
    """
    GETTING Upgrade/Downgrade cost
    """
    def getUpgradeCost(self, position):
        if position in self.field_positions_normal:
            if self.getPropertyLevel(position) == 0:
                return self.properties_pricetable.loc[position, "purchase_price"]
            else:
                return self.properties_pricetable.loc[position, "upgrade_price"]
        else:
            raise KeyError
        
    def getUpgradeCostSpecial(self, position):
        if position in self.field_positions_special:
            if self.properties_special.loc[position, "color"] == "white":
                return 150
            elif self.properties_special.loc[position, "color"] == "black":
                return 200
        else:
            raise KeyError
        
    def getDowngradeAmount(self, position):
        if position in self.field_positions_normal:
            if self.getPropertyLevel(position) == 0:
                return self.properties_pricetable.loc[position, "purchase_price"] / 2
            else:
                return self.properties_pricetable.loc[position, "upgrade_price"] / 2
        else:
            raise KeyError
            
    def getDowngradeAmountSpecial(self, position):
        if position in self.field_positions_special:
            if self.properties_special.loc[position, "color"] == "white":
                return 75
            elif self.properties_special.loc[position, "color"] == "black":
                return 100
        else:
            raise KeyError
    
    
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
        return randrange(1,7), randrange(1,7)
    
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
        
        
    def start(self, verbose):
        game_alive = True
        
        if verbose:
            print("The game has started")
        
        while game_alive:
            
            go_again = self.executeTurn(self.current_player_turn, verbose)
            
            while go_again:
                
                go_again = self.executeTurn(self.current_player_turn, verbose)
            
            
            self.nextTurn()
            
            if self.solePlayerAlive():
                game_alive = False
        
    def executeDecision(self, player_color, decision):
        max = decision.idxmax()
        
        if ":" in max:
            s = max.split(":")
            position = int(s[1])
                
            if s[0] == "buy":
                if position in self.field_positions_normal:
                    self.increaseProperty(player_color, position)
                elif position in self.field_positions_special:
                    self.setOwnerSpecialProperty(player_color, position, "buy")
                
            else:
                if position in self.field_positions_normal:
                    self.downgradeProperty(player_color, position)
                elif position in self.field_positions_special:
                    self.setOwnerSpecialProperty(player_color, position, "sell")
            
            
        elif "pass" == max:
            pass
        else:
            raise Error
        
    def validateDecision(self, player_color, decision, gamestate):
        #Get the index of the maximum
        max = decision.idxmax()
        
        #Get the number of the index
        index = decision.index.get_loc(decision.idxmax())
        
        #Get the validation table
        res = gamestate.loc[["upgradeable" in x or "downgradeable" in x for x in ser.index]]
        
        try:
            return res.iat[index]
        except IndexError:
            return True
        
    def executeTurn(self, player_color, verbose):
        
        if verbose:
            print("It is " + player_color + "'s turn")
        
        #Check if the player is alive else throw error
        if self.isPlayerAlive(player_color) == False:
            if verbose:
                print(player_color + "is out of the game")
            return False
        
        #Get old position
        old_position = self.getPlayerPosition(player_color)
        
        if verbose:
            print("Old position: " + str(old_position) + ", " + self.getPropertyName(old_position))
        
        #roll the dice
        d1, d2 = self.rollDice()
        
        if verbose:
            print("Rolled: " + str(d1) + ", " + str(d2))
        
        #Check if the dice are the same and set the go_again variable
        go_again = d1 == d2
        dice_roll = d1 + d2
        
        #get the new position from the old positino and dice roll
        new_position = self.getNewPosition(old_position, dice_roll)
        
        if verbose:
            print("Went to: " + str(new_position) + ", " + self.getPropertyName(new_position))
        
        #move the player to the new position
        self.movePlayer(player_color, old_position, new_position)
		
        if new_position in self.field_positions_normal or new_position in self.field_positions_special:
			
			owner_color = self.getOwnerColor(new_position)
		
			if player_color == owner_color:
                pass
			elif owner_color is None:
				#MAKE DECISION HERE
				gs = self.getGamestate(player_color, new_position)
				decision = self.getPlayerDecision(player_color, gs)
				if self.validateDecision(player_color, decision, gs):
					self.executeDecision(player_color, decision)
				else:
					pass
			else:
				if new_position in self.field_positions_normal: 
					self.landOpponentProperty(player_color, new_position)
				else:	
					self.landOpponentPropertySpecial(player_color, new_position, dice_roll)
				        
        #Check if the position is an action field
        elif new_position in self.field_positions_action:
            self.landActionField(player_color, new_position)
        
        #If its not any of those then there is an issue and an error is raised
        else:
            raise Error
            
        self.updatePlayerStatus(player_color)
        
        self.upgradeDowngradeLoop(player_color)
            
        return go_again
        
    def upgradeDowngradeLoop(self, player_color):
        #MAKE DECISION HERE
        loop = True
        while loop:
            gs = self.getGamestate(player_color)
            decision = self.getPlayerDecision(player_color, gs)
            if self.validateDecision(player_color, decision, gs):
                self.executeDecision(player_color, decision)
            else:
                break
            
            self.updatePlayerStatus(player_color)
            if self.isPlayerAlive(player_color) == False:
                break
    
    def getGamestate(self, player_color, landed=None):
        
        props = [x for x in self.properties["name"].tolist()]
        props_special = [x for x in self.properties_special["name"].tolist()]
        
        gs = []
        
        if landed is None:
            up = self.properties.apply(
                lambda x: 1 if x.name == landed else 0, 
                axis=1).tolist()
            
            up_cost = self.properties.apply(
                lambda x: self.getUpgradeCost(x.name) if x.name == landed else 0,
                axis=1).tolist()
            
            up_spec = self.properties_special.apply(
                lambda x: 1 if x.name == landed else 0,
                axis=1).tolist()
            
            up_spec_cost = self.properties_special.apply(
                lambda x: self.getUpgradeCostSpecial(x.name) if x.name == landed else 0,
                axis=1).tolist()
            
            down = self.properties.apply(lambda x: 0, axis=1).tolist()
            
            down_cost = self.properties.apply(lambda x: 0, axis=1).tolist()
            
            down_spec = self.properties_special.apply(lambda x: 0, axis=1).tolist()
            
            down_spec_cost = self.properties_special.apply(lambda x: 0, axis=1).tolist()
            
        else:
            up = self.properties.apply(
                lambda x: int(self.canUpgradeProperty(player_color, x.name)), 
                axis=1).tolist()
            
            up_cost = self.properties.apply(
                lambda x: self.getUpgradeCost(x.name) if self.canUpgradeProperty(player_color, x.name) else 0,
                axis=1).tolist()
            
            up_spec = self.properties_special.apply(
                lambda x: int(self.canUpgradePropertySpecial(player_color, x.name)),
                axis=1).tolist()
            
            up_spec_cost = self.properties_special.apply(
                lambda x: self.getUpgradeCostSpecial(x.name) if self.canUpgradePropertySpecial(player_color, x.name) else 0,
                axis=1).tolist()
            
            down = self.properties.apply(
                lambda x: int(self.canDowngradeProperty(player_color, x.name)),
                axis=1).tolist()
            
            down_cost = self.properties.apply(
                lambda x: self.getDowngradeAmount(x.name) if self.canDowngradeProperty(player_color, x.name) else 0,
                axis=1).tolist()
            
            down_spec = self.properties_special.apply(
                lambda x: int(self.canDowngradePropertySpecial(player_color, x.name)),
                axis=1).tolist()
            
            down_spec_cost = self.properties_special.apply(
                lambda x: self.getDowngradeAmountSpecial(x.name) if self.canDowngradePropertySpecial(player_color, x.name) else 0,
                axis=1).tolist()
        
        updown = up + up_cost + down + down_cost + up_spec + up_spec_cost + down_spec + down_spec_cost
        index = [a + x for a in ["upgradeable_", "upgrade_cost_","downgradeable_","downgrade_cost_"] for x in props]
        index2 = [a + x for a in ["upgradeable_spec_", "upgrade_cost_spec_","downgradeable_spec_","downgrade_cost_spec_"] for x in props_special]
        index.extend(index2)
        
        updown_series = pd.Series(updown, index=index)
        
        for color in self.players:
            updown_series = pd.concat([updown_series, self.getPlayerState(color)])
            
        return updown_series

        
    def getPlayerState(self, player_color):
        l1 = [self.getPlayerCash(player_color), 
              self.getPlayerNetworth(player_color), 
              self.getPlayerPosition(player_color)]
        
        owned = self.properties[player_color].tolist()
        
        owned_levels = self.properties.apply(
            lambda x: x["level"] if x[player_color] else 0, 
            axis=1).tolist()
        
        owned_spec = self.properties_special[player_color].tolist()
        
        owned_rent_potent = self.properties.apply(
            lambda x: self.getRentCost(x.name) if x[player_color] else 0, 
            axis=1).tolist()
        
        owned_rent_potent_spec = self.properties_special.apply(
            lambda x: self.getRentCostSpecial(x.name) if x[player_color] else 0, 
            axis=1).tolist()
        
        full_list = l1 + owned + owned_levels + owned_spec + owned_rent_potent + owned_rent_potent_spec
        
        full_index = [
            player_color + ": player_cash",
            player_color + ": player_networth",
            player_color + ": player_position"
        ]
        
        props = [player_color + ": " + x for x in self.properties["name"].tolist()]
        props_special = [player_color + ": " + x for x in self.properties_special["name"].tolist()]
        
        
        full_index.extend([x + " owned" for x in props])
        full_index.extend([x + " levels" for x in props])
        full_index.extend([x + " owned special" for x in props_special])
        full_index.extend([x + " rent" for x in props])
        full_index.extend([x + " rent special" for x in props_special])
        
        return pd.Series(full_list, index=full_index, name=player_color)
    
    
    def __repr__(self):
        properties = pprint.pformat(self.properties)
        string = "properties: " + properties + "\n"
        string = string + "available houses:%s\navailable hotels:%s" % (self.available_houses, self.available_hotels)
        
        return "<Board \n" + string + ">"

    def __str__(self):
        properties = pprint.pformat(self.properties)
        return "Board" % (properties, self.owner, self.level)
