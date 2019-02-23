from src import BoardInformation, BoardError

import unittest

class TestInit(unittest.TestCase):
    def test_list(self):
        #self.assertRaises(ValueError, BoardInformation("red", 10000))
        self.failUnlessRaises(ValueError, BoardInformation, "red", 10000)

    def test_empty_list(self):
        self.failUnlessRaises(ValueError, BoardInformation, [])

    def test_low_max_cash(self):
        self.failUnlessRaises(BoardError, BoardInformation, (["red"], 0))

    def test_maximum_players(self):
        self.failUnlessRaises(BoardError, BoardInformation, ([str(i) for i in range(10)], 1500))

    def test_no_duplicate_player_names(self):
        self.failUnlessRaises(BoardError, BoardInformation, (["red", "red"], 10000))

class TestCanPurchase(unittest.TestCase):
    def test_can_purchase_unowned(self):
        bi = BoardInformation(["red","blue"], 10000)

        self.assertTrue(bi.can_purchase("red", 1))
        self.assertTrue(bi.can_purchase("blue", 1))

    def test_can_purchase_owned(self):
        bi = BoardInformation(["red","blue"], 10000)
        bi.purchase("red", 1)

        self.assertFalse(bi.can_purchase("red", 1))
        self.assertFalse(bi.can_purchase("blue", 1))

    def test_can_purchase_non_property(self):
        bi = BoardInformation(["red","blue"], 10000)
        self.assertRaises(BoardError, bi.can_purchase("red", 2))

    def test_can_purchase_wrong_name(self):
        bi = BoardInformation(["red","blue"], 10000)
        self.assertRaises(ValueError, bi.can_purchase("reed", 2))

"""


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
if __name__ == "__main__":
    unittest.main()
