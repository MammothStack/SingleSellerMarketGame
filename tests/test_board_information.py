from src import BoardInformation, BoardError

import unittest

class TestInit(unittest.TestCase):
    def test_list(self):
        self.failUnlessRaises(ValueError, BoardInformation, "red", 10000)

    def test_empty_list(self):
        self.failUnlessRaises(ValueError, BoardInformation, [])

    def test_low_max_cash(self):
        self.failUnlessRaises(BoardError, BoardInformation, ["red"], 0)

    def test_maximum_players(self):
        self.failUnlessRaises(BoardError, BoardInformation, [str(i) for i in range(10)], 1500)

    def test_no_duplicate_player_names(self):
        self.failUnlessRaises(BoardError, BoardInformation, ["red", "red"], 10000)

class TestCanPurchase(unittest.TestCase):
    def test_can_purchase_unowned(self):
        bi = BoardInformation(["red","blue"], 10000)

        self.assertTrue(bi.can_purchase(1))

    def test_can_purchase_owned(self):
        bi = BoardInformation(["red","blue"], 10000)
        bi.purchase("red", 1)

        self.assertFalse(bi.can_purchase(1))


    def test_can_purchase_non_property_alt(self):
        bi = BoardInformation(["red","blue"], 10000)
        with self.assertRaises(BoardError):
            bi.can_purchase(2)

class TestCanDowngrade(unittest.TestCase):
    def test_can_downgrade_unowned(self):
        bi = BoardInformation(["red","blue"], 10000)

        self.assertFalse(bi.can_downgrade("red", 1))
        self.assertFalse(bi.can_downgrade("blue", 1))

    def test_can_downgrade_non_monopoly(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)

        self.assertFalse(bi.can_downgrade("red", 1))
        self.assertFalse(bi.can_downgrade("blue", 1))

    def test_can_downgrade_level_1(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertFalse(bi.can_downgrade("red", 1))
        self.assertFalse(bi.can_downgrade("blue", 1))

        self.assertFalse(bi.can_downgrade("red", 3))
        self.assertFalse(bi.can_downgrade("blue", 3))


    def test_can_downgrade_monopoly_level_4(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)

        self.assertTrue(bi.can_downgrade("red", 1))
        self.assertFalse(bi.can_downgrade("blue", 1))
        self.assertFalse(bi.can_downgrade("red", 3))

    def test_can_downgrade_monopoly_level_6(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)

        self.assertTrue(bi.can_downgrade("red", 1))
        self.assertFalse(bi.can_downgrade("blue", 1))

    def test_can_downgrade_monopoly_mortgaged(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)
        bi.mortgage("red", 1)

        self.assertFalse(bi.can_downgrade("red", 1))
        self.assertFalse(bi.can_downgrade("blue", 1))

    def test_can_downgrade_max_no_houses(self):
        bi = BoardInformation(["red","blue"], 10000, 4, 4)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.purchase("blue",6)
        bi.purchase("blue",8)
        bi.purchase("blue",9)

        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)

        bi.upgrade("blue", 6)
        bi.upgrade("blue", 6)
        bi.upgrade("blue", 6)
        bi.upgrade("blue", 6)


        self.assertFalse(bi.can_downgrade("red", 1))
        self.assertTrue(bi.can_downgrade("blue", 6))


    def test_can_downgrade_4_houses(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)
        bi.available_houses = 4

        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)


        self.assertTrue(bi.can_downgrade("red", 1))
        self.assertFalse(bi.can_downgrade("blue", 1))

class TestCanUpgrade(unittest.TestCase):

    def test_can_upgrade_unowned(self):
        bi = BoardInformation(["red","blue"], 10000)
        self.assertFalse(bi.can_upgrade("red", 1))
        self.assertFalse(bi.can_upgrade("blue", 1))

    def test_can_upgrade_owned(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)

        self.assertFalse(bi.can_upgrade("red", 1))
        self.assertFalse(bi.can_upgrade("blue", 1))

    def test_can_upgrade_monopoly(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertTrue(bi.can_upgrade("red", 1))
        self.assertFalse(bi.can_upgrade("blue", 1))

        self.assertTrue(bi.can_upgrade("red", 3))
        self.assertFalse(bi.can_upgrade("blue", 3))

    def test_can_upgrade_max_level(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red" , 1)
        bi.upgrade("red" , 1)
        bi.upgrade("red" , 1)
        bi.upgrade("red" , 1)
        bi.upgrade("red" , 1)

        self.assertFalse(bi.can_upgrade("red", 1))
        self.assertFalse(bi.can_upgrade("blue", 1))

        self.assertTrue(bi.can_upgrade("red", 3))
        self.assertFalse(bi.can_upgrade("blue", 3))

    def test_can_upgrade_mortgaged(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.mortgage("red", 1)

        self.assertFalse(bi.can_upgrade("red", 1))
        self.assertFalse(bi.can_upgrade("red", 3))

        self.assertFalse(bi.can_upgrade("blue", 1))
        self.assertFalse(bi.can_upgrade("blue", 3))

    def test_can_upgrade_no_houses(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.available_houses = 1

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red", 1)

        self.assertFalse(bi.can_upgrade("red", 1))
        self.assertFalse(bi.can_upgrade("red", 3))

    def test_can_upgrade_no_hotels(self):
        bi = BoardInformation(["red","blue"], 10000, 20, 1)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red" , 1)
        bi.upgrade("red" , 1)
        bi.upgrade("red" , 1)
        bi.upgrade("red" , 1)

        self.assertFalse(bi.can_upgrade("red", 1))
        self.assertTrue(bi.can_upgrade("red", 3))


class TestUpgrade(unittest.TestCase):

    """
    value                  + upgrade cost
    can downgrade          true
    can mortgage           false (for all in monopoly)
    can unmortgage         false
    level                  + 1
    can upgrade            if applicable
    current rent amount

    """

    def test_non_property_position(self):
        bi = BoardInformation(["red","blue"], 10000)
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        with self.assertRaises(BoardError):
            bi.upgrade("red", 2)

    def test_unowned_property(self):
        bi = BoardInformation(["red","blue"], 10000)
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        with self.assertRaises(BoardError):
            bi.upgrade("red", 6)

    def test_wrong_player(self):
        bi = BoardInformation(["red","blue"], 10000)
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        with self.assertRaises(BoardError):
            bi.upgrade("blue", 2)

    def test_unknown_player(self):
        bi = BoardInformation(["red","blue"], 10000)
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        with self.assertRaises(BoardError):
            bi.upgrade("reed", 2)

    def test_value(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red", 1)

        self.assertEquals(110, bi.get_value(1))

        bi.upgrade("red", 1)

        self.assertEquals(160, bi.get_value(1))

    def test_can_downgrade(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red", 1)

        self.assertTrue(bi.can_downgrade("red", 1))

        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)

        self.assertTrue(bi.can_downgrade("red", 1))

    def test_can_mortgage(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red", 1)

        self.assertFalse(bi.can_mortgage("red", 1))

    def test_can_mortgage_other_props_of_same_color(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red", 1)

        self.assertFalse(bi.can_mortgage("red", 1))
        self.assertFalse(bi.can_mortgage("red", 3))


    def test_can_unmortgage(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red", 1)

        self.assertFalse(bi.can_unmortgage("red", 1))
        self.assertFalse(bi.can_unmortgage("red", 3))

    def test_level(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertEquals(bi.get_level(1), 1)

        bi.upgrade("red", 1)

        self.assertEquals(bi.get_level(1), 2)

        bi.upgrade("red", 1)

        self.assertEquals(bi.get_level(1), 3)

        bi.upgrade("red", 1)

        self.assertEquals(bi.get_level(1), 4)

        bi.upgrade("red", 1)

        self.assertEquals(bi.get_level(1), 5)

        bi.upgrade("red", 1)

        self.assertEquals(bi.get_level(1), 6)

    def test_can_upgrade_non_max(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red", 1)

        self.assertTrue(bi.can_upgrade("red", 1))

    def test_can_upgrade_max(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)

        self.assertFalse(bi.can_upgrade("red", 1))

    def test_current_rent_amount(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertEquals(bi.get_rent(1, 7), 2)
        bi.upgrade("red", 1)

        self.assertEquals(bi.get_rent(1, 7), 10)
        bi.upgrade("red", 1)

        self.assertEquals(bi.get_rent(1, 7), 30)
        bi.upgrade("red", 1)

        self.assertEquals( bi.get_rent(1, 7), 90)
        bi.upgrade("red", 1)

        self.assertEquals(bi.get_rent(1, 7), 160)
        bi.upgrade("red", 1)

        self.assertEquals(bi.get_rent(1, 7), 250)

    def test_houses_decline(self):
        bi = BoardInformation(["red","blue"], 10000, 20, 4)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertEquals(20, bi.available_houses)
        bi.upgrade("red", 1)
        self.assertEquals(19, bi.available_houses)
        bi.upgrade("red", 1)
        self.assertEquals(18, bi.available_houses)
        bi.upgrade("red", 1)
        self.assertEquals(17, bi.available_houses)

    def test_houses_return_when_hotel_upgrade(self):
        bi = BoardInformation(["red","blue"], 10000, 20, 4)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertEquals(20, bi.available_houses)
        self.assertEquals(4, bi.available_hotels)
        bi.upgrade("red", 1)
        self.assertEquals(19, bi.available_houses)
        self.assertEquals(4, bi.available_hotels)
        bi.upgrade("red", 1)
        self.assertEquals(18, bi.available_houses)
        self.assertEquals(4, bi.available_hotels)
        bi.upgrade("red", 1)
        self.assertEquals(17, bi.available_houses)
        self.assertEquals(4, bi.available_hotels)
        bi.upgrade("red", 1)
        self.assertEquals(16, bi.available_houses)
        self.assertEquals(4, bi.available_hotels)

        bi.upgrade("red", 1)
        self.assertEquals(20, bi.available_houses)
        self.assertEquals(3, bi.available_hotels)




"""


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
