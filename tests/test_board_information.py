from src import BoardInformation, BoardError

import unittest

class TestFieldType(unittest.TestCase):
    self.bi = BoardInformation(["red","blue"], 10000)

    def test_0(self):
        self.assertTrue(bi.is_action(0))
        self.assertFalse(bi.is_utility(0))
        self.assertFalse(bi.is_property(0))

    def test_1(self):
        self.assertFalse(bi.is_action(1))
        self.assertFalse(bi.is_utility(1))
        self.assertTrue(bi.is_property(1))

    def test_2(self):
        self.assertTrue(bi.is_action(2))
        self.assertFalse(bi.is_utility(2))
        self.assertFalse(bi.is_property(2))

    def test_3(self):
        self.assertFalse(bi.is_action(3))
        self.assertFalse(bi.is_utility(3))
        self.assertTrue(bi.is_property(3))

    def test_4(self):
        self.assertTrue(bi.is_action(4))
        self.assertFalse(bi.is_utility(4))
        self.assertFalse(bi.is_property(4))

    def test_5(self):
        self.assertFalse(bi.is_action(5))
        self.assertTrue(bi.is_utility(5))
        self.assertFalse(bi.is_property(5))

    def test_6(self):
        self.assertFalse(bi.is_action(6))
        self.assertFalse(bi.is_utility(6))
        self.assertTrue(bi.is_property(6))

    def test_7(self):
        self.assertTrue(bi.is_action(7))
        self.assertFalse(bi.is_utility(7))
        self.assertFalse(bi.is_property(7))

    def test_8(self):
        self.assertFalse(bi.is_action(8))
        self.assertFalse(bi.is_utility(8))
        self.assertTrue(bi.is_property(8))

    def test_9(self):
        self.assertFalse(bi.is_action(9))
        self.assertFalse(bi.is_utility(9))
        self.assertTrue(bi.is_property(9))

    def test_10(self):
        self.assertTrue(bi.is_action(10))
        self.assertFalse(bi.is_utility(10))
        self.assertFalse(bi.is_property(10))

    def test_11(self):
        self.assertFalse(bi.is_action(11))
        self.assertFalse(bi.is_utility(11))
        self.assertTrue(bi.is_property(11))

    def test_12(self):
        self.assertFalse(bi.is_action(12))
        self.assertTrue(bi.is_utility(12))
        self.assertFalse(bi.is_property(12))

    def test_13(self):
        self.assertFalse(bi.is_action(13))
        self.assertFalse(bi.is_utility(13))
        self.assertTrue(bi.is_property(13))

    def test_14(self):
        self.assertFalse(bi.is_action(14))
        self.assertFalse(bi.is_utility(14))
        self.assertTrue(bi.is_property(14))

    def test_15(self):
        self.assertFalse(bi.is_action(15))
        self.assertTrue(bi.is_utility(15))
        self.assertFalse(bi.is_property(15))

    def test_16(self):
        self.assertFalse(bi.is_action(16))
        self.assertFalse(bi.is_utility(16))
        self.assertTrue(bi.is_property(16))

    def test_17(self):
        self.assertTrue(bi.is_action(17))
        self.assertFalse(bi.is_utility(17))
        self.assertFalse(bi.is_property(17))

    def test_18(self):
        self.assertFalse(bi.is_action(18))
        self.assertFalse(bi.is_utility(18))
        self.assertTrue(bi.is_property(18))

    def test_19(self):
        self.assertFalse(bi.is_action(19))
        self.assertFalse(bi.is_utility(19))
        self.assertTrue(bi.is_property(19))

    def test_20(self):
        self.assertTrue(bi.is_action(20))
        self.assertFalse(bi.is_utility(20))
        self.assertFalse(bi.is_property(20))

    def test_21(self):
        self.assertFalse(bi.is_action(21))
        self.assertFalse(bi.is_utility(21))
        self.assertTrue(bi.is_property(21))

    def test_22(self):
        self.assertTrue(bi.is_action(22))
        self.assertFalse(bi.is_utility(22))
        self.assertFalse(bi.is_property(22))

    def test_23(self):
        self.assertFalse(bi.is_action(23))
        self.assertFalse(bi.is_utility(23))
        self.assertTrue(bi.is_property(23))

    def test_24(self):
        self.assertFalse(bi.is_action(24))
        self.assertFalse(bi.is_utility(24))
        self.assertTrue(bi.is_property(24))

    def test_25(self):
        self.assertFalse(bi.is_action(25))
        self.assertTrue(bi.is_utility(25))
        self.assertFalse(bi.is_property(25))

    def test_26(self):
        self.assertFalse(bi.is_action(26))
        self.assertFalse(bi.is_utility(26))
        self.assertTrue(bi.is_property(26))

    def test_27(self):
        self.assertFalse(bi.is_action(27))
        self.assertFalse(bi.is_utility(27))
        self.assertTrue(bi.is_property(27))

    def test_28(self):
        self.assertFalse(bi.is_action(28))
        self.assertTrue(bi.is_utility(28))
        self.assertFalse(bi.is_property(28))

    def test_29(self):
        self.assertFalse(bi.is_action(29))
        self.assertFalse(bi.is_utility(29))
        self.assertTrue(bi.is_property(29))

    def test_30(self):
        self.assertTrue(bi.is_action(22))
        self.assertFalse(bi.is_utility(22))
        self.assertFalse(bi.is_property(22))

    def test_31(self):
        self.assertFalse(bi.is_action(31))
        self.assertFalse(bi.is_utility(31))
        self.assertTrue(bi.is_property(31))

    def test_32(self):
        self.assertFalse(bi.is_action(32))
        self.assertFalse(bi.is_utility(32))
        self.assertTrue(bi.is_property(32))

    def test_33(self):
        self.assertTrue(bi.is_action(22))
        self.assertFalse(bi.is_utility(22))
        self.assertFalse(bi.is_property(22))

    def test_34(self):
        self.assertFalse(bi.is_action(34))
        self.assertFalse(bi.is_utility(34))
        self.assertTrue(bi.is_property(34))

    def test_35(self):
        self.assertFalse(bi.is_action(35))
        self.assertTrue(bi.is_utility(35))
        self.assertFalse(bi.is_property(35))

    def test_36(self):
        self.assertTrue(bi.is_action(36))
        self.assertFalse(bi.is_utility(36))
        self.assertFalse(bi.is_property(36))

    def test_37(self):
        self.assertFalse(bi.is_action(37))
        self.assertFalse(bi.is_utility(37))
        self.assertTrue(bi.is_property(37))

    def test_38(self):
        self.assertTrue(bi.is_action(38))
        self.assertFalse(bi.is_utility(38))
        self.assertFalse(bi.is_property(38))

    def test_39(self):
        self.assertFalse(bi.is_action(39))
        self.assertFalse(bi.is_utility(39))
        self.assertTrue(bi.is_property(39))

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
        bi = BoardInformation(["red","blue"], 10000, 20, 0)

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

class TestDowngrade(unittest.TestCase):

    def test_non_property_position(self):
        bi = BoardInformation(["red","blue"], 10000)
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        with self.assertRaises(BoardError):
            bi.downgrade("red", 2)

    def test_unowned_property(self):
        bi = BoardInformation(["red","blue"], 10000)
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        with self.assertRaises(BoardError):
            bi.downgrade("red", 6)

    def test_wrong_player(self):
        bi = BoardInformation(["red","blue"], 10000)
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        with self.assertRaises(BoardError):
            bi.downgrade("blue", 2)

    def test_unknown_player(self):
        bi = BoardInformation(["red","blue"], 10000)
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        with self.assertRaises(BoardError):
            bi.downgrade("reed", 2)

    def test_value(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red", 1)

        self.assertEquals(110, bi.get_value(1))

        bi.downgrade("red", 1)

        self.assertEquals(60, bi.get_value(1))

    def test_can_downgrade(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red", 1)

        self.assertTrue(bi.can_downgrade("red", 1))

        bi.downgrade("red", 1)

        self.assertFalse(bi.can_downgrade("red", 1))

        bi.mortgage("red", 1)

        self.assertFalse(bi.can_downgrade("red", 1))

        bi.unmortgage("red",1)

        self.assertFalse(bi.can_downgrade("red", 1))

        bi.upgrade("red", 1)

        self.assertTrue(bi.can_downgrade("red", 1))

    def test_can_mortgage(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red", 1)
        bi.upgrade("red", 1)

        self.assertFalse(bi.can_mortgage("red", 1))
        bi.downgrade("red", 1)
        self.assertFalse(bi.can_mortgage("red", 1))
        bi.downgrade("red", 1)
        self.assertTrue(bi.can_mortgage("red", 1))


    def test_can_mortgage_other_props_of_same_color(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red", 1)

        self.assertFalse(bi.can_mortgage("red", 1))
        self.assertFalse(bi.can_mortgage("red", 3))

        bi.downgrade("red", 1)

        self.assertTrue(bi.can_mortgage("red", 1))



    def test_can_unmortgage(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red", 1)
        bi.downgrade("red", 1)

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

        bi.downgrade("red", 1)

        self.assertEquals(bi.get_level(1), 5)

        bi.downgrade("red", 1)

        self.assertEquals(bi.get_level(1), 4)

        bi.downgrade("red", 1)

        self.assertEquals(bi.get_level(1), 3)

        bi.downgrade("red", 1)

        self.assertEquals(bi.get_level(1), 2)

        bi.downgrade("red", 1)

        self.assertEquals(bi.get_level(1), 1)

    def test_can_downgrade_non_max(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.downgrade("red", 1)

        self.assertTrue(bi.can_downgrade("red", 1))

    def test_can_downgrade_max(self):
        bi = BoardInformation(["red","blue"], 10000)

        bi.purchase("red", 1)
        bi.purchase("red", 3)

        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)

        self.assertTrue(bi.can_downgrade("red", 1))

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
        bi.downgrade("red", 1)
        self.assertEquals(bi.get_rent(1, 7), 160)
        bi.downgrade("red", 1)
        self.assertEquals(bi.get_rent(1, 7), 90)
        bi.downgrade("red", 1)
        self.assertEquals( bi.get_rent(1, 7), 30)
        bi.downgrade("red", 1)
        self.assertEquals(bi.get_rent(1, 7), 10)
        bi.downgrade("red", 1)
        self.assertEquals(bi.get_rent(1, 7), 2)

    def test_houses_increase(self):
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
        bi.downgrade("red", 1)
        self.assertEquals(18, bi.available_houses)
        bi.downgrade("red", 1)
        self.assertEquals(19, bi.available_houses)
        bi.downgrade("red", 1)
        self.assertEquals(20, bi.available_houses)

    def test_houses_return_when_hotel_upgrade(self):
        bi = BoardInformation(["red","blue"], 10000, 20, 4)

        bi.purchase("red", 1)
        bi.purchase("red", 3)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)
        bi.upgrade("red", 1)

        self.assertEquals(20, bi.available_houses)
        self.assertEquals(3, bi.available_hotels)

        bi.downgrade("red", 1)

        self.assertEquals(16, bi.available_houses)
        self.assertEquals(4, bi.available_hotels)

class TestMortgage(unittest.TestCase):

    #unownedprop
    def test_unowned_property(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertRaises(BoardError, lambda: bi.mortgage("red", 6))

        with self.assertRaises(BoardError):
            bi.mortgage("red", 6)
    #nonprop
    def test_non_property(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertRaises(BoardError, lambda: bi.mortgage("red", 2))

        with self.assertRaises(BoardError):
            bi.mortgage("red", 2)

    #nonplayer
    def test_non_player(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertRaises(BoardError, lambda: bi.mortgage("reed", 3))

        with self.assertRaises(BoardError):
            bi.mortgage("reed", 3)

    #value
    def test_value(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertEquals(60, bi.get_value(1))

        bi.mortgage("red", 1)

        self.assertEquals(30, bi.get_value(1))

    #level
    def test_level(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 1)
        bi.purchase("red", 3)
        self.assertEquals(1, bi.get_level(1))

        bi.mortgage("red", 1)

        self.assertEquals(0, bi.get_level(1))

    #rent
    def test_rent(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertEquals(2, bi.get_rent(1, dice_roll=7))

        bi.mortgage("red", 1)

        self.assertEquals(0, bi.get_rent(1, dice_roll=7))

    def test_mortgage_without_monopoly(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 1)

        try:
            bi.mortgage("red", 1)
        except BoardError:
            self.fail("Game rules allow this")

    #canmortgage
    def test_can_mortgage(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 1)
        self.assertTrue(bi.can_mortgage("red", 1))
        bi.purchase("red", 3)

        self.assertTrue(bi.can_mortgage("red", 1))
        self.assertTrue(bi.can_mortgage("red", 3))

        bi.mortgage("red", 1)

        self.assertFalse(bi.can_mortgage("red", 1))
        self.assertTrue(bi.can_mortgage("red", 3))

        bi.mortgage("red", 3)

        self.assertFalse(bi.can_mortgage("red", 1))
        self.assertFalse(bi.can_mortgage("red", 3))

    #canunmortgage
    def test_can_unmortgage(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 1)
        self.assertFalse(bi.can_unmortgage("red", 1))
        bi.purchase("red", 3)

        self.assertFalse(bi.can_unmortgage("red", 1))
        self.assertFalse(bi.can_unmortgage("red", 3))

        bi.mortgage("red", 1)

        self.assertTrue(bi.can_unmortgage("red", 1))
        self.assertFalse(bi.can_unmortgage("red", 3))

        bi.mortgage("red", 3)

        self.assertTrue(bi.can_unmortgage("red", 1))
        self.assertTrue(bi.can_unmortgage("red", 3))

    #canupgrade
    def test_can_upgrade(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertTrue(bi.can_upgrade("red", 1))

        bi.mortgage("red", 1)

        self.assertFalse(bi.can_upgrade("red", 1))

    #candowngrade
    def test_can_downgrade(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertFalse(bi.can_downgrade("red", 1))

        bi.mortgage("red", 1)

        self.assertFalse(bi.can_downgrade("red", 1))

    #canpurchase
    def test_can_purchase(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertFalse(bi.can_purchase(1))

        bi.mortgage("red", 1)

        self.assertFalse(bi.can_purchase(1))

    #other props cant upgrade
    def test_other_props_cant_upgrade(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertTrue(bi.can_upgrade("red", 1))

        bi.mortgage("red", 1)

        self.assertRaises(BoardError, lambda: bi.upgrade("red", 3))
        self.assertRaises(BoardError, lambda: bi.upgrade("red", 1))

class TestUnmortgage(unittest.TestCase):

    def test_unowned_property(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertRaises(BoardError, lambda: bi.unmortgage("red", 6))

        bi.purchase("blue", 6)

        self.assertRaises(BoardError, lambda: bi.unmortgage("red", 6))

        bi.mortgage("blue", 6)

        self.assertRaises(BoardError, lambda: bi.unmortgage("red", 6))

        bi.unmortgage("blue", 6)

        self.assertRaises(BoardError, lambda: bi.unmortgage("red", 6))


    def test_non_property(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 1)
        bi.purchase("red", 3)

        self.assertRaises(BoardError, lambda: bi.unmortgage("red", 2))
        self.assertRaises(BoardError, lambda: bi.unmortgage("red", 10))

    def test_non_player(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 6)
        bi.purchase("red", 8)
        bi.purchase("red", 9)

        self.assertRaises(BoardError, lambda: bi.unmortgage("reed", 6))

    def test_value(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 6)
        bi.purchase("red", 8)
        bi.purchase("red", 9)

        self.assertEquals(100, bi.get_value(6))
        self.assertEquals(100, bi.get_value(8))
        self.assertEquals(120, bi.get_value(9))

        bi.mortgage("red", 6)
        bi.mortgage("red", 8)
        bi.mortgage("red", 9)

        self.assertEquals(50, bi.get_value(6))
        self.assertEquals(50, bi.get_value(8))
        self.assertEquals(60, bi.get_value(9))

        bi.unmortgage("red", 6)
        bi.unmortgage("red", 8)
        bi.unmortgage("red", 9)

        self.assertEquals(100, bi.get_value(6))
        self.assertEquals(100, bi.get_value(8))
        self.assertEquals(120, bi.get_value(9))

    def test_level(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 6)
        bi.purchase("red", 8)
        bi.purchase("red", 9)

        self.assertEquals(1, bi.get_level(6))
        self.assertEquals(1, bi.get_level(8))
        self.assertEquals(1, bi.get_level(9))

        bi.mortgage("red", 6)
        bi.mortgage("red", 8)
        bi.mortgage("red", 9)

        self.assertEquals(0, bi.get_level(6))
        self.assertEquals(0, bi.get_level(8))
        self.assertEquals(0, bi.get_level(9))

        bi.unmortgage("red", 6)
        bi.unmortgage("red", 8)
        bi.unmortgage("red", 9)

        self.assertEquals(1, bi.get_level(6))
        self.assertEquals(1, bi.get_level(8))
        self.assertEquals(1, bi.get_level(9))

    def test_rent(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 6)
        bi.purchase("red", 8)
        bi.purchase("red", 9)

        self.assertEquals(6, bi.get_rent(6, 7))
        self.assertEquals(6, bi.get_rent(8, 7))
        self.assertEquals(8, bi.get_rent(9, 7))

        bi.mortgage("red", 6)
        bi.mortgage("red", 8)
        bi.mortgage("red", 9)

        self.assertEquals(0, bi.get_rent(6, 7))
        self.assertEquals(0, bi.get_rent(8, 7))
        self.assertEquals(0, bi.get_rent(9, 7))

        bi.unmortgage("red", 6)
        bi.unmortgage("red", 8)
        bi.unmortgage("red", 9)

        self.assertEquals(6, bi.get_rent(6, 7))
        self.assertEquals(6, bi.get_rent(8, 7))
        self.assertEquals(8, bi.get_rent(9, 7))

    def test_unmortgage_without_mortgaging(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 6)
        bi.purchase("red", 8)
        bi.purchase("red", 9)

        self.assertRaises(BoardError, lambda: bi.unmortgage("red", 6))
        self.assertRaises(BoardError, lambda: bi.unmortgage("red", 8))
        self.assertRaises(BoardError, lambda: bi.unmortgage("red", 9))

    def test_can_mortgage(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 6)
        bi.purchase("red", 8)
        bi.purchase("red", 9)

        self.assertTrue(bi.can_mortgage("red", 6))
        self.assertTrue(bi.can_mortgage("red", 8))
        self.assertTrue(bi.can_mortgage("red", 9))

        bi.mortgage("red", 6)
        bi.mortgage("red", 8)
        bi.mortgage("red", 9)

        self.assertFalse(bi.can_mortgage("red", 6))
        self.assertFalse(bi.can_mortgage("red", 8))
        self.assertFalse(bi.can_mortgage("red", 9))

        bi.unmortgage("red", 6)
        bi.unmortgage("red", 8)
        bi.unmortgage("red", 9)

        self.assertTrue(bi.can_mortgage("red", 6))
        self.assertTrue(bi.can_mortgage("red", 8))
        self.assertTrue(bi.can_mortgage("red", 9))

    def test_can_unmortgage(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 6)
        bi.purchase("red", 8)
        bi.purchase("red", 9)

        self.assertFalse(bi.can_unmortgage("red", 6))
        self.assertFalse(bi.can_unmortgage("red", 8))
        self.assertFalse(bi.can_unmortgage("red", 9))

        bi.mortgage("red", 6)
        bi.mortgage("red", 8)
        bi.mortgage("red", 9)

        self.assertTrue(bi.can_unmortgage("red", 6))
        self.assertTrue(bi.can_unmortgage("red", 8))
        self.assertTrue(bi.can_unmortgage("red", 9))

        bi.unmortgage("red", 6)
        bi.unmortgage("red", 8)
        bi.unmortgage("red", 9)

        self.assertFalse(bi.can_unmortgage("red", 6))
        self.assertFalse(bi.can_unmortgage("red", 8))
        self.assertFalse(bi.can_unmortgage("red", 9))

    def test_can_upgrade(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 6)
        bi.purchase("red", 8)
        bi.purchase("red", 9)

        self.assertTrue(bi.can_upgrade("red", 6))
        self.assertTrue(bi.can_upgrade("red", 8))
        self.assertTrue(bi.can_upgrade("red", 9))

        bi.mortgage("red", 6)
        bi.mortgage("red", 8)
        bi.mortgage("red", 9)

        self.assertFalse(bi.can_upgrade("red", 6))
        self.assertFalse(bi.can_upgrade("red", 8))
        self.assertFalse(bi.can_upgrade("red", 9))

        bi.unmortgage("red", 6)
        bi.unmortgage("red", 8)
        bi.unmortgage("red", 9)

        self.assertTrue(bi.can_upgrade("red", 6))
        self.assertTrue(bi.can_upgrade("red", 8))
        self.assertTrue(bi.can_upgrade("red", 9))

    def test_can_downgrade(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 6)
        bi.purchase("red", 8)
        bi.purchase("red", 9)

        self.assertFalse(bi.can_downgrade("red", 6))
        self.assertFalse(bi.can_downgrade("red", 8))
        self.assertFalse(bi.can_downgrade("red", 9))

        bi.mortgage("red", 6)
        bi.mortgage("red", 8)
        bi.mortgage("red", 9)

        self.assertFalse(bi.can_downgrade("red", 6))
        self.assertFalse(bi.can_downgrade("red", 8))
        self.assertFalse(bi.can_downgrade("red", 9))

        bi.unmortgage("red", 6)
        bi.unmortgage("red", 8)
        bi.unmortgage("red", 9)

        self.assertFalse(bi.can_downgrade("red", 6))
        self.assertFalse(bi.can_downgrade("red", 8))
        self.assertFalse(bi.can_downgrade("red", 9))

    def test_can_purchase(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 6)
        bi.purchase("red", 8)
        bi.purchase("red", 9)

        self.assertFalse(bi.can_purchase(6))
        self.assertFalse(bi.can_purchase(8))
        self.assertFalse(bi.can_purchase(9))

        bi.mortgage("red", 6)
        bi.mortgage("red", 8)
        bi.mortgage("red", 9)

        self.assertFalse(bi.can_purchase(6))
        self.assertFalse(bi.can_purchase(8))
        self.assertFalse(bi.can_purchase(9))

        bi.unmortgage("red", 6)
        bi.unmortgage("red", 8)
        bi.unmortgage("red", 9)

        self.assertFalse(bi.can_purchase(6))
        self.assertFalse(bi.can_purchase(8))
        self.assertFalse(bi.can_purchase(9))

    def test_other_can_upgrade_when_unmortgaging(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 6)
        bi.purchase("red", 8)
        bi.purchase("red", 9)

        self.assertTrue(bi.can_upgrade("red", 6))
        self.assertTrue(bi.can_upgrade("red", 8))
        self.assertTrue(bi.can_upgrade("red", 9))

        bi.mortgage("red", 6)

        self.assertFalse(bi.can_upgrade("red", 6))
        self.assertFalse(bi.can_upgrade("red", 8))
        self.assertFalse(bi.can_upgrade("red", 9))

        bi.unmortgage("red", 6)

        self.assertTrue(bi.can_upgrade("red", 6))
        self.assertTrue(bi.can_upgrade("red", 8))
        self.assertTrue(bi.can_upgrade("red", 9))

        bi.mortgage("red", 8)

        self.assertFalse(bi.can_upgrade("red", 6))
        self.assertFalse(bi.can_upgrade("red", 8))
        self.assertFalse(bi.can_upgrade("red", 9))

        bi.unmortgage("red", 8)

        self.assertTrue(bi.can_upgrade("red", 6))
        self.assertTrue(bi.can_upgrade("red", 8))
        self.assertTrue(bi.can_upgrade("red", 9))

class TestPurchase(unittest.TestCase):

    def test_unowned_property(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 6)
        self.assertRaises(BoardError, lambda: bi.purchase("blue", 6))

    def test_none_property(self):
        bi = BoardInformation(["red","blue"])
        self.assertRaises(BoardError, lambda: bi.purchase("blue", 10))

    def test_non_player(self):
        bi = BoardInformation(["red","blue"])
        self.assertRaises(BoardError, lambda: bi.purchase("bloo", 1))

    def test_value(self):
        bi = BoardInformation(["red","blue"])
        self.assertEquals(0, bi.get_value(6))
        self.assertEquals(0, bi.get_value(8))
        self.assertEquals(0, bi.get_value(9))

        bi.purchase("red", 6)
        bi.purchase("red", 8)
        bi.purchase("red", 9)

        self.assertEquals(100, bi.get_value(6))
        self.assertEquals(100, bi.get_value(8))
        self.assertEquals(120, bi.get_value(9))

    def test_level(self):
        bi = BoardInformation(["red","blue"])
        self.assertEquals(0, bi.get_level(6))
        self.assertEquals(0, bi.get_level(8))
        self.assertEquals(0, bi.get_level(9))

        bi.purchase("red", 6)
        bi.purchase("red", 8)
        bi.purchase("red", 9)

        self.assertEquals(1, bi.get_level(6))
        self.assertEquals(1, bi.get_level(8))
        self.assertEquals(1, bi.get_level(9))

    def test_rent(self):
        bi = BoardInformation(["red","blue"])
        self.assertEquals(0, bi.get_rent(6, 7))
        self.assertEquals(0, bi.get_rent(8, 7))
        self.assertEquals(0, bi.get_rent(9, 7))

        bi.purchase("red", 6)
        bi.purchase("red", 8)
        bi.purchase("red", 9)

        self.assertEquals(6, bi.get_rent(6, 7))
        self.assertEquals(6, bi.get_rent(8, 7))
        self.assertEquals(8, bi.get_rent(9, 7))

    def test_can_purchase(self):
        bi = BoardInformation(["red","blue"])
        self.assertTrue(bi.can_purchase(6))
        self.assertTrue(bi.can_purchase(8))
        self.assertTrue(bi.can_purchase(9))

        bi.purchase("red", 6)
        bi.purchase("red", 8)
        bi.purchase("red", 9)

        self.assertFalse(bi.can_purchase(6))
        self.assertFalse(bi.can_purchase(8))
        self.assertFalse(bi.can_purchase(9))

class TestGet_total_levels_owned(unittest.TestCase):

    def test_proper_number(self):
        bi = BoardInformation(["red","blue"])
        bi.purchase("red", 6)

        self.assertEquals(1, bi.get_total_levels_owned("red"))
        self.assertEquals(0, bi.get_total_levels_owned("blue"))

        bi.purchase("red", 8)
        bi.purchase("red", 9)

        self.assertEquals(3, bi.get_total_levels_owned("red"))

        bi.upgrade("red", 6)
        bi.upgrade("red", 6)
        bi.upgrade("red", 6)

        self.assertEquals(6, bi.get_total_levels_owned("red"))

        bi.upgrade("red", 8)
        bi.upgrade("red", 8)
        bi.upgrade("red", 8)

        self.assertEquals(9, bi.get_total_levels_owned("red"))


"""

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
