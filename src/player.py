import numpy as np
import pandas as pd
import random
import json
from random import shuffle
from tensorflow.keras.models import model_from_json
from tensorflow.keras.optimizers import Adam
import tensorflowjs as tfjs
from collections import deque
import warnings


class Agent:
    """The Agent that is capable of all the functions required by the Board

    The Agent class is a container that houses the OperationModels that make the
    decisions on the board.

    Parameters
    --------------------
    name : str
        The name of the agent

    models : args
        Individual models are stored here with their operation as the keys to
        the dictionary

    alive : boolean (default=True)
        If the player is alive and can play in the game

    cash : int (default=1500)
        The amount of cash that player has throughout the game

    Attributes
    --------------------


    Methods
    --------------------


    """

    def __init__(self, name, *models):
        self.name = name
        self.can_purchase = False
        self.can_up_down_grade = False
        self.can_trade_offer = False
        self.can_trade_decision = False
        self.models = {}
        self.set_models(models)

    def __repr__(self):
        s = (
            f"{self.__class__.__name__}, "
            f"{self.name!r}, "
            f"{list(self.models.values())!r}"
        )
        return s

    def set_models(self, models):
        """Sets the models of the player for the various operations

        Parameters
        --------------------
        models : args
            All the operation models that should be set as the models.

        """
        for model in models:
            self.set_model(model)

    def set_model(self, model):
        """Sets a model of the player for the specific model operation

        Sets the flag that this player can perform a certain operation
        based on the operation attribute of the model

        Parameters
        --------------------
        model : OperationModel
            The operation model that should be set

        Raises
        --------------------
        ValueError
            When the given OperationModel is not correct

        """
        if model.operation == "purchase":
            self.can_purchase = True
        elif model.operation == "up_down_grade":
            self.can_up_down_grade = True
        elif model.operation == "trade_offer":
            self.can_trade_offer = True
        elif model.operation == "trade_decision":
            self.can_trade_decision = True
        else:
            raise ValueError("Model could not be set")
        self.models.update({model.operation: model})

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
        return pd.DataFrame(
            list(self.models[operation].memory),
            columns=["state", "action", "reward", "next_state", "done"],
        )

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

    def get_reward_scalars(self, operation):
        """Returns the reward scalars of the Operation model"""
        return (self.models[operation].rho, self.models[operation].rho_mode)

    def learn(self, batch_size=None):
        """Takes accumulated training data and fits it to the models

        Parameters
        --------------------
        batch_size : int (default=None)
            The size of the batch that should be used for training

        """

        for o in self.models.values():
            o.replay() if batch_size is None else o.replay(batch_size)

    def save(self, destination, type="py"):
        for model in self.models.values():
            model.save(destination, type)


class OperationModel:
    """The Model that carry out a specific operation of the board

    The Operation Model is the Agent that makes the decisions and controls what
    and how the Keras model learns.

    Parameters
    --------------------
    model : keras.model
        Keras model that is used to train and predict

    name : str
        The name of the Operation model

    operation : str
        The operation that the operation model predicts and trains on

    true_threshold : float
        float between 0 and 1 to determine when a value constitutes a true value

    single_label : boolean
        If the model predicts a single label

    optimizer : str
        the keras.optimizer as string value used to optimize the model

    loss : str
        the keras.losses as string value used to train the model

    metrics : list (default=['accuracy'])
        the keras.metrics as list of strings used to train the model

    running_reward : int (default=0)
        The total reward aquired throughout its training cycles

    episode_nb : int (default=0)
        The total number of trainings that the model underwent

    gamma : float (default=1.0)
        The scalar used to weigh the next decision

    epsilon : float (default=1.0)
        The probability of the decision take being a random choice

    epsilon_min : float (default=0.01)
        The minimum epsilon value that at which it wont decay

    epsilon_decay : float (default=0.99)
        The rate at which the epsilon decays

    alpha : float (default=0.001)
        The learning rate of the model

    alpha_decay : float(default=0.001)
        The rate at which the learning rate decays

    rho : int (default=3)
        The risk level on a scale of (1-5) for the calculated reward

    rho_mode : int(default=1)
        The mode of calculating risk level (1-2)

    can_learn : boolean(default=True)
        If the model can learn or not

    Attributes
    --------------------
    memory : deque
        The store of the agents memories

    Methods
    --------------------
    remember(state, action, reward, next_state, done)
        Store the data in the Agents memory

    get_action(state)
        Returns the decision of the Operation Model based on the given state

    replay(batch_size)
        Uses the Agent's memory to fit the model

    save(destination)
        Saves the the Operation Model and all of its configurations at the given destination

    """

    def __init__(
        self,
        model,
        name,
        operation,
        true_threshold,
        single_label,
        optimizer,
        loss,
        metrics=["accuracy"],
        running_reward=0,
        episode_nb=0,
        gamma=1.0,
        epsilon=1.0,
        epsilon_min=0.01,
        epsilon_decay=0.99,
        alpha=0.001,
        alpha_decay=0.001,
        rho=3,
        rho_mode=1,
        can_learn=True,
    ):

        self.model = model
        self.model_output_dim = self.model.layers[-1].output_shape[1]
        self.name = name
        self.operation = operation
        self.loss = loss
        self.optimizer = optimizer
        self.metrics = metrics
        self.true_threshold = true_threshold
        self.single_label = single_label
        self.running_reward = running_reward
        self.episode_nb = episode_nb
        self.can_learn = can_learn
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.alpha = alpha
        self.alpha_decay = alpha_decay
        self.rho = rho
        self.rho_mode = rho_mode
        self.memory = deque(maxlen=100000)

    def remember(self, state, action, reward, next_state, done):
        """Stores the data in the Agents Memory

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

    def get_action(self, state):
        """Returns the decision of the Operation Model based on the given state

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
        if np.random.random() <= self.epsilon:
            action_raw = np.random.rand(self.model_output_dim)
        else:
            action_raw = self.model.predict(state)[0]
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
        """Uses the Agent's memory to fit the model

        Parameters
        --------------------
        batch_size : int
            The size of the batch that should be used for training

        """
        if self.can_learn and self.memory:
            x_batch, y_batch = [], []
            minibatch = random.sample(self.memory, min(len(self.memory), batch_size))

            for (state, action, reward, next_state, done) in minibatch:
                y_target = self.model.predict(state)
                y_target[0][action] = (
                    reward
                    if done
                    else reward + self.gamma * np.max(self.model.predict(next_state)[0])
                )
                x_batch.append(state[0])
                y_batch.append(y_target[0])
            self.model.fit(
                np.array(x_batch), np.array(y_batch), batch_size=len(x_batch), verbose=0
            )
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
            self.episode_nb += 1

    def save(self, destination=None, type="py"):
        """Saves the the Operation Model and all of its configurations at the given destination"""

        if destination is None:
            destination = "/"

        if destination[-1:] != "/":
            destination += "/"

        destination = destination + self.operation + "/"

        if type == "py":

            config = {
                "name": self.name,
                "operation": self.operation,
                "true_threshold": self.true_threshold,
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
                "epsilon": self.epsilon,
                "epsilon_min": self.epsilon_min,
                "epsilon_decay": self.epsilon_decay,
                "alpha": self.alpha,
                "alpha_decay": self.alpha_decay,
                "rho": self.rho,
                "rho_mode": self.rho_mode,
            }

            self.model.save_weights(destination + config["h5_path"])
            model_json = self.model.to_json()

            with open(destination + config["json_path"], "w") as json_file:
                json_file.write(model_json)
            json_file.close()

            with open(
                destination + self.name + "_" + self.operation + "_config.json", "w"
            ) as config_file:
                json.dump(config, config_file, indent=4)
            config_file.close()
        elif type == "js":
            tfjs.converters.save_keras_model(self.model, destination)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"{self.name!r}, {self.operation!r}, {self.episode_nb!r}, {self.epsilon!r}, {self.running_reward!r})"
        )


def load_operation_model(file_path):
    config_file_name = None
    for file in os.listdir(file_path):
        if "config.json" in file:
            config_file_name = file
            break

    if config_file_name is None:
        raise ValueError(f"No config file found in {filepath}")

    if file_path[-1:] != "/":
        file_path += "/"
    with open(file_path + config_file_name) as config_file:
        config = json.load(config_file)
    config_file.close()

    json_file = open(file_path + config["json_path"], "r")
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.load_weights(file_path + config["h5_path"])
    try:
        model.name = config["name"]
    except:
        warnings.warn("Could not set name")

    if config["optimizer"] == "adam":
        opt = Adam(lr=config["alpha"], decay=config["alpha_decay"])
    else:
        ValueError("cannot resolve Optimizer")

    model.compile(loss=config["loss"], optimizer=opt, metrics=config["metrics"])

    return OperationModel(model=model, **config)


def load_agent(file_path):
    if file_path[-1:] != "/":
        file_path += "/"
    operation_model_directories = [
        dI for dI in os.listdir(file_path) if os.path.isdir(os.path.join(file_path, dI))
    ]

    operation_models = [
        load_operation_model(file_path + fp) for fp in operation_model_directories
    ]
    if len(operation_models) == 0:
        raise ValueError(f"No models could be found at {file_path}")

    return Agent(name=operation_models[0].name, *operation_models)


def load_pool(file_path="SingleSellerMarketGame/models/py/", limit=None):
    if file_path[-1:] != "/":
        file_path += "/"

    agent_directories = [
        dI for dI in os.listdir(file_path) if os.path.isdir(os.path.join(file_path, dI))
    ]

    if limit is not None and limit < len(agent_directories):
        shuffle(agent_directories)
        agent_directories = agent_directories[:limit]

    pool = [load_agent(file_path + fp) for fp in agent_directories]
    return pool
