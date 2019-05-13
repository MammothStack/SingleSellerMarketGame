from src import OperationModel
import unittest
import pandas as pd
import numpy as np
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.models import Sequential, Model


def get_keras_model(simple=True):
    if simple:
        model = Sequential(name="test_model")
        model.add(Dense(input_shape=(4,), units=4, activation="relu"))
        model.add(Dropout(0.35))
        model.add(Dense(units=2, activation="sigmoid"))
        return model
    else:
        inp = Input((4,), name="Input")
        x = Dense(4, activation="relu")(inp)
        x = Dropout(0.25)(x)
        x = Dense(2, activation="relu")(x)

        y = Dense(4, activation="relu")(inp)
        y = Dropout(0.25)(y)
        y = Dense(2, activation="sigmoid")(y)

        model = Model(inp, [x, y], name="complex")
        return model


def remember(operation_model):
    if len(operation_model.output_dimensions) > 1:
        for i in range(len(x_train)):
            operation_model.remember(
                state=np.array((x_train[i],)),
                action=[y_train[i], y_train[i]],
                reward=reward_train[i],
                next_state=np.array((x_next_train[i],)),
                done=testing_done[i],
            )
    else:
        for i in range(len(x_train)):
            operation_model.remember(
                state=np.array((x_train[i],)),
                action=y_train[i],
                reward=reward_train[i],
                next_state=np.array((x_next_train[i],)),
                done=testing_done[i],
            )


def get_simple_operation_model():
    k_model = get_keras_model()
    k_model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])
    om_simple = OperationModel(
        model=k_model,
        name="test_simple",
        operation="purchase",
        true_threshold=0.5,
        single_label=False,
        optimizer="adam",
        loss="binary_crossentropy",
        input_dimensions=[4],
        output_dimensions=[2],
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
    )

    return om_simple


def get_complex_operation_model():
    c_model = get_keras_model(simple=False)
    c_model.compile(
        loss=["binary_crossentropy", "binary_crossentropy"],
        optimizer="adam",
        metrics=["accuracy"],
    )
    om_complex = OperationModel(
        model=c_model,
        name="test_complex",
        operation="purchase",
        true_threshold=0.5,
        single_label=False,
        optimizer="adam",
        loss=["binary_crossentropy", "binary_crossentropy"],
        input_dimensions=[4],
        output_dimensions=[2, 2],
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
    )

    return om_complex


x_train = pd.read_csv("tests/testing_x.csv", header=None).values
y_train = pd.read_csv("tests/testing_y.csv", header=None).values
x_next_train = pd.read_csv("tests/testing_x_next.csv", header=None).values
reward_train = pd.read_csv("tests/testing_reward.csv", header=None).values
testing_done = pd.read_csv("tests/testing_done.csv", header=None).values


class TestRemember(unittest.TestCase):
    def test_can_remember(self):
        om_complex = get_complex_operation_model()
        om_simple = get_simple_operation_model()

        remember(om_complex)
        remember(om_simple)

        self.assertEquals(20000, len(om_complex.memory))

    def test_cant_remember(self):
        om_complex = get_complex_operation_model()
        om_simple = get_simple_operation_model()

        with self.assertRaises(ValueError):
            om_complex.remember(None, None, None, None, None)

        with self.assertRaises(ValueError):
            om_simple.remember(None, None, None, None, None)


class TestGetAction(unittest.TestCase):
    def test_dimension(self):
        om_complex = get_complex_operation_model()
        om_simple = get_simple_operation_model()
        self.assertEquals(2, len(om_complex.get_action(x_train[0])))
        self.assertEquals(2, len(om_simple.get_action(x_train[0])))

    def test_type(self):
        om_complex = get_complex_operation_model()
        om_simple = get_simple_operation_model()
        self.assertEquals(list, type(om_complex.get_action(x_train[0])))
        # self.assertEquals(list)
