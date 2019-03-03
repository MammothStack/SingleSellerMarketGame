import numpy as np
import pandas as pd
import random
import json
from tensorflow.keras.models import model_from_json
from collections import deque

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
        alive=True,
        cash=1500,
    ):
        for m1 in models:
            for m2 in models:
                if m1.max_cash_limit != m2.max_cash_limit:
                    raise ValueError("Max Cash Limit of the models is incompatible")

        self.max_cash_limit = models[0].max_cash_limit
        self.name = name
        self.models = self.set_models(models)
        self.alive = alive
        self._init_cash = cash
        self.cash = self._init_cash
        self.allowed_to_move = True

    def __repr__(self):
        s = (
            f"{self.__class__.__name__}, "
            f"{self.name!r}, "
            f"{list(self.models.values())!r}"
        )
        return s

    def reset_player(self):
        self.cash = self._init_cash
        self.allowed_to_move = True
        self.alive = True

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

    def add_training_data(self, operation, state, action, reward, next_state, done):
        """Stores data for later learning to the appropriate model

        Parameters
        --------------------
        operation : str
            The operation that corresponds to the model for which the training
            data should be added

        state : np.ndarray
            The state of the game

        action : np.ndarray
            The action taken based on the state

        reward : float
            The reward received based on the action

        next_state : np.ndarray
            The state of the game after the action was carried out

        done : boolean
            if the game is finished

        """
        self.models[operation].remember(state, action, reward, next_state, done)

    def get_training_data(self, operation):
        """Returns all the training data that was appended during the game

        The returned data is in a pandas DataFrame, with the state, action,
        rewards, next_state, done are stored in their respective columns.

        Parameters
        --------------------
        operation : str
            The operation for which the data should be returned

        Returns
        --------------------
        training_data: pd.DataFrame
            The training data for the specified operation.DataFrame, with the
            state, action, rewards, next_state, done are stored


        """
        return pd.DataFrame(list(self.models[operation].memory),
            columns=["state","action","reward","next_state","done"])

    def get_action(self, gamestate, operation):
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
        return self.models[operation].get_action(gamestate)

    def learn(self, batch_size=None):
        """Takes accumulated training data and fits it to the models

        Parameters
        --------------------
        batch_size : int (default=None)
            The size of the batch that should be used for training

        """

        for o in self.models.keys():
            o.replay() if batch_size is None else o.replay(batch_size)

    def save_operation_models(self, destination):
        for model in self.models.values():
            model.save(destination)

class OperationModel():
    """The Agent that carry out a specific operation of the board

    Parameters
    --------------------

    Attributes
    --------------------

    Methods
    --------------------


    """

    def __init__(self, model, optimizer, name, operation, loss,
        true_threshold, single_label, max_cash_limit, metrics=['accuracy'],
        running_reward=0, episode_nb=0, gamma=1.0, epsilon=1.0, epsilon_min=0.01,
        epsilon_decay=0.99, alpha=0.001, alpha_decay=0.001, can_learn=True):

        self.model = model
        self.model_output_dim = self.model.layers[-1].output_shape[1]
        self.name = name
        self.operation = operation
        self.loss = loss
        self.optimizer = optimizer
        self.metrics = metrics
        self.true_threshold = true_threshold
        self.single_label = single_label
        self.max_cash_limit = max_cash_limit
        self.running_reward = running_reward
        self.episode_nb = episode_nb
        self.can_learn = can_learn
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.alpha = alpha
        self.alpha_decay = alpha_decay
        self.memory = deque(maxlen=100000)

    def remember(self, state, action, reward, next_state, done):
        """Stores data for later learning

        Parameters
        --------------------
        state : np.ndarray
            The state of the game

        action : np.ndarray
            The action taken based on the state

        reward : float
            The reward received based on the action

        next_state : np.ndarray
            The state of the game after the action was carried out

        done : boolean
            if the game is finished

        """
        self.memory.append((state, action, reward, next_state, done))

    """
    def get_dynamic_reward(self, cash, level, scalar):
        cash = 0 if cash <= 0 else cash
        return self.reward_equation(cash, level, self.max_cash_limit, scalar)

    """

    def get_action(self, state):
        """Returns the decision of the Operation Model

        Takes the x data and produces an output

        Parameters
        --------------------
        state : numpy.ndarray
            array consisting of gamedata. The shape of the parameter must match
            the input requirement of the model.

        Returns
        --------------------
        decision : numpy.ndarray
            Array with decisions based on the x, that need to be
            interpreted

        """
        if (np.random.random() <= self.epsilon):
            action_raw = np.random.rand(self.model_output_dim)
        else:
            action_raw = self.model.predict(state)[0]
            #return self.model.predict(state)[0]
        action = np.zeros(self.model_output_dim)

        if self.single_label:
            ind = np.argmax(action_raw)
            if action_raw[ind] >= self.true_threshold:
                action[ind] = 1
        else:
            ind = np.argwhere(action_raw >= self.true_threshold).flatten()
            np.put(action, ind, 1)

        return action

    def replay(self, batch_size=32):
        """Uses the given data to fit the model

        Parameters
        --------------------
        batch_size : int
            The size of the batch that should be used for training

        """
        if self.can_learn:
            x_batch, y_batch = [], []
            minibatch = random.sample(
                self.memory, min(len(self.memory), batch_size))

            for state, action, reward, next_state, done in minibatch:
                y_target = self.model.predict(state)
                y_target[0][action] = reward if done else reward + self.gamma * np.max(self.model.predict(next_state)[0])
                x_batch.append(state[0])
                y_batch.append(y_target[0])

            self.model.fit(np.array(x_batch), np.array(y_batch), batch_size=len(x_batch), verbose=0)
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
            self.episode_nb += 1

        """
        if self.can_learn:
            self.model.fit(x, y, sample_weight=sample_weight, verbose=verbose)
            if reward_sum is None: reward_sum = np.sum(sample_weight)
            self.running_reward = (self.running_reward * self.gamma +
                reward_sum * (1-self.gamma))
            self.episode_nb += 1

        """

    def save(self, destination=None):
        if destination is None:
            destination = ""
        else:
            if destination[-1:] != "/": destination += "/"

        config = {
            "name": self.name,
            "operation": self.operation,
            "true_threshold": self.true_threshold,
            "max_cash_limit": self.max_cash_limit,
            "running_reward": self.running_reward,
            "episode_nb": self.episode_nb,
            "h5_path": self.name + "_" + self.operation + ".h5",
            "json_path": self.name + "_" + self.operation + ".json",
            "loss": self.loss,
            "optimizer": self.optimizer,
            "metrics": self.metrics,
            "single_label": self.single_label,
            "can_learn": self.can_learn,
            "gamma": self.gamma,
            "epsilon":self.epsilon,
            "epsilon_min":self.epsilon_min,
            "epsilon_decay":self.epsilon_decay,
            "alpha": self.alpha,
            "alpha_decay":self.alpha_decay
        }

        self.model.save_weights(destination + config["h5_path"])
        model_json = self.model.to_json()

        with open(destination + config["json_path"], "w") as json_file:
            json_file.write(model_json)
        json_file.close()

        with open(destination + self.name + "_" +  self.operation + "_config.json", 'w') as config_file:
            json.dump(config, config_file, indent=4)
        config_file.close()

    def __repr__(self):
        return (f'{self.__class__.__name__}('
            f'{self.name!r}, {self.operation!r},{self.episode_nb!r}, {self.epsilon!r})')

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
        single_label = config["single_label"],
        true_threshold=config["true_threshold"],
        max_cash_limit=config["max_cash_limit"],
        running_reward=config["running_reward"],
        episode_nb=config["episode_nb"],
        can_learn=config["can_learn"],
        optimizer = config["optimizer"],
        metrics = config["metrics"],
        gamma = config["gamma"],
        epsilon=config["epsilon"],
        epsilon_min=config["epsilon_min"],
        epsilon_decay=config["epsilon_decay"],
        alpha=config["alpha"],
        alpha_decay=config["alpha_decay"],
    )
