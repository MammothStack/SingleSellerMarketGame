import numpy as np
import pandas as pd
from tensorflow.keras.models import model_from_json

def _load_model_from_file(h5_weights_file_path, json_file_path, name):
    """Loads the model from the file paths and returns the compiled model

    The two files paths are converted into .h5 and .json files respectively.
    The name parameter also sets the name of the model that is read from
    the file paths.

    Parameters
    --------------------
    h5_weights_file_path : str
        The file path of the .h5 file

    json_file_path : str
        The file path of the .json file

    name : str
        The name that is to be given to the model


    """
    json_file = open(json_file_path, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.load_weights(h5_weights_file_path)
    model.name = name

    return model

def load_player_from_file(
    name,
    purchase=None,
    up_down_grade=None,
    trade_offer=None,
    trade_decision=None):
    """Loads the player from the given file paths and returns the Player

    The model file paths are first checked that they are in the correct
    format. The models are then individually loaded from the .h5 and .json
    files. The loaded models are then also compiled with the proper compile
    configuration. The given name and compiled models are initialized in a
    Player object.

    Parameters
    --------------------
    name : str
        The name which is given to the loaded player and models

    purchase : tuple or list
        The .h5 and .json file locations for the purchase model. Needs to be
        of length 2

    up_down_grade : tuple or list
        The .h5 and .json file locations for the upgrade/downgrade model.
        Needs to be of length 2

    trade_offer : tuple or list
        The .h5 and .json file locations for the trade model. Needs to be
        of length 2

    trade_decision : tuple or list
        The .h5 and .json file locations for the trade model. Needs to be
        of length 2

    """
    def good_input(inp):
        if type(inp) != tuple and type(inp) != list:
            return False
        else:
            if len(inp) != 2:
                return False
            else:
                return type(inp[0]) == str and type(inp[1]) == str

    def get_h5_json_file(inp):
        if inp[0][-3:] == ".h5" and inp[1][-5:] == ".json":
            return inp[0], inp[1]
        elif inp[0][-5:] == ".json" and inp[1][-3:] == ".h5":
            return inp[1], inp[0]
        else:
            raise ValueError("h5/json filepath incorrect")

    def get_model(inp, name):
        if inp is not None:
            if good_input(inp):
                h5_filepath, json_filepath = get_h5_json_file(inp)
                return _load_model_from_file(h5_filepath, json_filepath, name)
        else:
            return None

    models = {
        "purchase": get_model(purchase, name + "_purchase"),
        "up_down_grade": get_model(up_down_grade, name + "_up_down_grade"),
        "trade_offer": get_model(trade_offer, name + "_trade_offer"),
        "trade_decision": get_model(trade_decision, name + "_trade_decision")
    }

    models["purchase"].compile(
        loss='binary_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
    )

    models["up_down_grade"].compile(
        loss="categorical_crossentropy",
        optimizer="adam",
        metrics=["accuracy"]
    )

    models["trade_offer"].compile(
        loss="binary_crossentropy",
        optimizer="adam",
        metrics=["accuracy"]
    )

    models["trade_decision"].compile(
        loss="binary_crossentropy",
        optimizer="adam",
        metrics=["accuracy"]
    )

    return Player(name, models)

class Player():
    """The player to that plays on the Board

    Contains the ML models that make the decisions about the actions/operations
    that can be made in the BoardController. It stores the models in a
    dictionary where the keys refer to the operation. It also stores information
    relating to the current game such as the cash that the player has, as well
    as the position of the player on the board.

    In addition it also collects the training data for the models that can be
    learned by the models. This information includes the X, y, and sample
    weight information

    Parameters
    --------------------
    name : str
        The name of the player

    models : dict
        The model dictionary where the keys refer to the operation that the
        model decides and the values are the models themselves:
        {
            "purchase": model,
            "up_down_grade": model,
            "trade_offer": model,
            "trade_decision": model
        }

    cash : int (default=1500)
        The cash that the player has during the game

    position : int (default=0)
        The position of the player on the board during the game

    Attributes
    --------------------

    allowed_to_move : boolean
        If this player is allowed to make a move on the Board

    x_train : dict
        Dictionary containing all the X array training data collected during
        the game for each operation possible. The operations are the keys to
        the data in the dictionary

    y_train : dict
        Dictionary containing all the y array training data collected during
        the game for each operation possible. The operations are the keys to
        the data in the dictionary

    rewards : dict
        Dictionary containing all the rewards array training data collected during
        the game for each operation possible. The operations are the keys to
        the data in the dictionary

    rewards_sum : dict
        Dictionary containing all the sum of the rewards in training data
        collected during the game for each operation possible. The operations
        are the keys to the data in the dictionary

    running_reward : dict
        Dictionary containing all the running reward in the training data
        collected during the game for each operation possible. The operations
        are the keys to the data in the dictionary

    episode_nb : int
        Count of how often the models were trained

    gamma : float (default=0.99)
        Used to calculate the running reward

    Methods
    --------------------


    """
    def __init__(
        self,
        name,
        models,
        cash=1500,
        position=0,
    ):
        self.name = name
        self.models = self.set_models(models)
        self._init_cash = cash
        self._init_position = position
        self.reset_player()
        self.running_reward = {o:0 for o in self.models.keys()}
        self.episode_nb = 0
        self.gamma = 0.99
        
    def __repr__(self):
        return (f'{self.__class__.__name__}('
            f'{self.name!r}, {self.models!r}, {self.episode_nb!r})')

    def reset_player(self):
        self.cash = self._init_cash
        self.position = self._init_position
        self.allowed_to_move = True
        self.x_train = {o:[] for o in self.models.keys()}
        self.y_train = {o:[] for o in self.models.keys()}
        self.rewards = {o:[] for o in self.models.keys()}
        self.rewards_sum = {o:0 for o in self.models.keys()}

    def set_models(self, models):
        """Sets the models of the player for the various operations

        Sets the flag that this player can perform a certain operation
        based on the presence of a model within the dictionary values. All
        keys must be present in order for this function to work.

        Parameters
        --------------------
        models : dict
            The dictionary that should be set as the models. Must have all the
            operations as keys.

        Raises
        --------------------
        ValueError
            If the dictionary does not contain all the operations as keys or
            the given models is not in a dictionary

        """
        if type(models) != dict:
            raise ValueError("The given model is not in dictionary form")

        if "purchase" in models.keys():
            self.can_purchase = models["purchase"] is not None
        else:
            raise ValueError("Purchase key not found in dictionary")

        if "up_down_grade" in models.keys():
            self.can_up_down_grade = models["up_down_grade"] is not None
        else:
            raise ValueError("up_down_grade key not found in dictionary")

        if "trade_offer" in models.keys():
            self.can_trade_offer = models["trade_offer"] is not None
        else:
            raise ValueError("trade_offer key not found in dictionary")

        if "trade_decision" in models.keys():
            self.can_trade_decision = models["trade_decision"] is not None
        else:
            raise ValueError("trade_decision key not found in dictionary")

        return models

    def add_training_data(self, operation, x, y, reward):
        """Adds an instance of training data

        Adds an x, y, and reward values for later training. This is added for a
        specific operation given by the operation parameter

        Parameters
        --------------------
        operation : str
            The operation for which the training data should be added to

        x : ndarray
            X training data that corresponds to the given x parameter

        y : ndarray
            y training data that corresponds to the given y parameter

        reward : ndarray
            reward training data that corresponds to the y and x values given

        """
        if(operation not in self.x_train.keys() or
            operation not in self.y_train.keys() or
            operation not in self.rewards.keys() or
            operation not in self.rewards_sum.keys()):
            raise ValueError("Given Operation is not in the data set")
        self.x_train[operation].append(x)
        self.y_train[operation].append(y)
        self.rewards[operation].append(reward)
        self.rewards_sum[operation] += reward

    def get_training_data(self, operation):
        """Returns all the training data that was appended during the game

        The returned data is in a pandas DataFrame, with the x_train, y_train,
        and rewards are stored in their respective columns.

        Parameters
        --------------------
        operation : str
            The operation for which the data should be returned

        Returns
        --------------------
        training_data: pd.DataFrame
            The training data for the specified operation.DataFrame, with the
            x_train, y_train, and rewards are stored

        Raises
        --------------------
        ValueError
            When the length of the X, y, rewards do not align, meaning gaps
            in information,

        """
        if len(self.x_train[operation]) != len(self.y_train[operation]):
            raise ValueError("x and y train arrays are not the same length for " + operation)
        if len(self.x_train[operation]) != len(self.rewards[operation]):
            raise ValueError("x and rewards arrays are not the same length for " + operation)
        return pd.DataFrame(
            [self.x_train[operation],
             self.y_train[operation],
             self.rewards[operation]],
            index=["x_train","y_train","rewards"]).T

    def get_decision(self, gamestate, operation):
        """Returns the decision of the player for the given operation

        Takes the gamestate and produces an output for the given operation and
        returns it.

        Parameters
        --------------------
        gamestate : numpy.ndarray
            Shape of (rows, columns, channel) consisting of gamedata. The shape
            of the parameter must match the input requirement of the model.

        operation : str
            The operation for which the decision should be made

        Returns
        --------------------
        decision : numpy.ndarray
            Array with decisions based on the gamedata, that need to be
            interpreted

        """
        res = self.models[operation].predict(np.array((gamestate,)))
        return res[0]

    def get_models(self):
        """Returns the models of the player"""
        return self.models.values()

    def learn(self):
        """Takes accumulated training data and fits it to the models

        Raises
        --------------------
        ValueError
            When the lengths of the training data are not aligned

        """

        for o in self.models.keys():
            if len(self.x_train[o]) != len(self.y_train[o]):
                raise ValueError("x and y train arrays are not the same length for " + o)
            if len(self.x_train[o]) != len(self.rewards[o]):
                raise ValueError("x and rewards arrays are not the same length for " + o)
            if self.x_train[o] != []:
                self.models[o].fit(
                    x=np.array(self.x_train[o]),
                    y=np.array(self.y_train[o]),
                    sample_weight=np.array(self.rewards[o]),
                    verbose=0
                )
                if self.running_reward is None:
                    self.running_reward[o] = self.reward_sum[o]
                else:
                    r = self.running_reward[o] * 0.99
                    s = self.rewards_sum[o] * 0.01
                    self.running_reward[o] = r + s
        self.episode_nb += 1

    def learn_training_data(self, operation, x_train, y_train, sample_weights):
        """Uses the given data to fit the model of the given operation

        Parameters
        --------------------
        operation : str
            The operation for which the training data should be added to

        x_train : ndarray
            X training data that corresponds to the given x parameter

        y_train : ndarray
            y training data that corresponds to the given y parameter

        sample_weights : ndarray
            Reward training data that corresponds to the x and y data given
            in the "add_training_data" method.

        """

        self.models[operation].fit(x_train, y_train, sample_weight, verbose=0)

    def save_models(self, destination=None):
        """Saves the models in the given destination

        Parameters
        --------------------
        destination : str (default=None)
            The destination where the files should be saved

        """
        if destination is None: destination = ""

        for m in self.models.values():
            m.save_weights(destination + m.name + '.h5')
            model_json = m.to_json()

            with open(destination + m.name + '.json', "w") as json_file:
                json_file.write(model_json)
            json_file.close()
