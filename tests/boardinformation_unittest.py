from src import board_information

class TestInit(unittest.TestCase):
    def test_list(self):
        self.assertRaises(ValueError, BoardInformation("red", 10000)


if __name__ == "__main__":
    unittest.main()
