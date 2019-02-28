import numpy as np
import pandas as pd
import json
from tensorflow.keras.models import model_from_json

class Player():
    """The player to that plays on the Board

    Parameters
    --------------------

    Attributes
    --------------------

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
        for m1 in models:
            for m2 in models:
                if m1.max_cash_limit != m2.max_cash_limit:
                    raise ValueError("Max Cash Limit of the models is incompatible")

        self.max_cash_limit = models[0].max_cash_limit
        self.name = name
        self.models = self.set_models(models)
        self._init_cash = cash
        self._init_position = position
        self.reset_player()

    def __repr__(self):
        return (f'{self.__class__.__name__}('
            f'{self.name!r}, {list(self.models.keys())!r})')

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
        based on the presence of a model within the list.

        Parameters
        --------------------
        models : list
            A list of all the operation models that should be set as the models.

        """
        if type(models) != list:
            raise ValueError("The given models must be in a list")

        for model in models:
            if model.operation == "purchase":
                self.can_purchase = True
            if model.operation == "up_down_grade":
                self.can_up_down_grade = True
            if model.operation == "trade_offer":
                self.can_trade_offer = True
            if model.operation == "trade_decision":
                self.can_trade_decision = True

        return {m.operation: m for m in models}

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
        return self.models[operation].get_decision(gamestate)

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
                self.models[o].learn_training_data(
                    x=np.array(self.x_train[o]),
                    y=np.array(self.y_train[o]),
                    sample_weight=np.array(self.rewards[o]),
                    verbose=0,
                    reward_sum=self.rewards_sum[o]
                )

    def save_operation_models(self, destination):
        for model in self.models.values():
            model.save(destination)

class OperationModel():
    """The player to that plays on the Board

    Parameters
    --------------------

    Attributes
    --------------------

    Methods
    --------------------


    """

    def __init__(
        self,
        model,
        name,
        operation,
        loss,
        reward_dict,
        true_threshold,
        max_cash_limit,
        reward_equation_str,
        running_reward=0,
        episode_nb=0,
        gamma=0.99,
        can_learn=True,
        optimizer="adam",
        metrics=['accuracy']):

        self.model = model
        self.name = name
        self.operation = operation
        self.loss = loss
        self.optimizer = optimizer
        self.metrics = metrics
        self.reward_dict = reward_dict
        self.true_threshold = true_threshold
        self.max_cash_limit = max_cash_limit
        self.reward_equation_str = reward_equation_str
        self.reward_equation = eval(reward_equation_str)
        self.running_reward = running_reward
        self.episode_nb = episode_nb
        self.can_learn = can_learn
        self.gamma = gamma

    def get_dynamic_reward(self, cash, level, scalar):
        cash = 0 if cash <= 0 else cash
        return self.reward_equation(cash, level, self.max_cash_limit, scalar)

    def get_decision(self, x):
        """Returns the decision of the Operation Model

        Takes the x data and produces an output

        Parameters
        --------------------
        x : numpy.ndarray
            array consisting of gamedata. The shape of the parameter must match
            the input requirement of the model.

        Returns
        --------------------
        decision : numpy.ndarray
            Array with decisions based on the x, that need to be
            interpreted

        """
        res = self.model.predict(np.array((x,)))
        return res[0]

    def learn_training_data(self, x, y, sample_weight, reward_sum=None, verbose=0):
        """Uses the given data to fit the model

        Parameters
        --------------------
        x : ndarray
            X training data that corresponds to the given x parameter

        y : ndarray
            y training data that corresponds to the given y parameter

        sample_weights : ndarray
            Sample weights that should be applied to the training

        reward_sum : float
            The sum of all the rewards received during the execution phase

        verbose : int
            Level of verbosity during training

        """
        if self.can_learn:
            self.model.fit(x, y, sample_weight=sample_weight, verbose=verbose)
            if reward_sum is None: reward_sum = np.sum(sample_weight)
            self.running_reward = (self.running_reward * self.gamma +
                reward_sum * (1-self.gamma))
            self.episode_nb += 1

    def save(self, destination=None):
        if destination is None:
            destination = ""
        else:
            if destination[-1:] != "/": destination += "/"

        config = {
            "name": self.name,
            "operation": self.operation,
            "reward_dict": self.reward_dict,
            "true_threshold": self.true_threshold,
            "max_cash_limit": self.max_cash_limit,
            "reward_equation_str": self.reward_equation_str,
            "running_reward": self.running_reward,
            "episode_nb": self.episode_nb,
            "h5_path": self.name + "_" + self.operation + ".h5",
            "json_path": self.name + "_" + self.operation + ".json",
            "loss": self.loss,
            "optimizer": self.optimizer,
            "metrics": self.metrics,
            "can_learn": self.can_learn,
            "gamma": self.gamma,
        }

        self.model.save_weights(destination + config["h5_path"])
        model_json = self.model.to_json()

        with open(destination + config["json_path"], "w") as json_file:
            json_file.write(model_json)
        json_file.close()

        with open(destination + self.name + "_config.json", 'w') as config_file:
            json.dump(config, config_file, indent=4)
        config_file.close()

    def __repr__(self):
        return (f'{self.__class__.__name__}('
            f'{self.name!r}, {self.operation!r},{self.episode_nb!r}, {self.running_reward!r})')

def load_operation_model(file_path, config_file_name):
    if file_path[-1:] != "/":
        file_path += "/"
    with open(file_path + config_file_name) as config_file:
        config = json.load(config_file)
    config_file.close()

    json_file = open(file_path + config["json_path"], 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.load_weights(file_path + config["h5_path"])
    #model.name = config["name"]
    model.compile(
        loss=config["loss"],
        optimizer=config["optimizer"],
        metrics=config["metrics"]
    )

    return OperationModel(
        model=model,
        name=config["name"],
        operation=config["operation"],
        loss=config["loss"],
        reward_dict=config["reward_dict"],
        true_threshold=config["true_threshold"],
        max_cash_limit=config["max_cash_limit"],
        reward_equation_str=config["reward_equation_str"],
        running_reward=config["running_reward"],
        episode_nb=config["episode_nb"],
        can_learn=config["can_learn"],
        optimizer = config["optimizer"],
        metrics = config["metrics"],
        gamma = config["gamma"]
    )
