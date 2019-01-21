import numpy as np
from tensorflow import keras

class Player():
    def __init__(
        self,
        name,
        is_ai=True,
        models=None,
        cash=1500,
        position=0,
    ):
        self.name = name
        self.is_ai = is_ai
        self.models = models
        self.init_cash = cash
        self.init_position = position
        self.reset_player()
        self.running_reward = {o:0 for o in self.models.keys()}
        self.episode_nb = 0
        self.gamma = 0.99

    def reset_player(self):
        self.cash = self.init_cash
        self.position = self.init_position
        self.allowed_to_move = True
        if self.is_ai:
            self.x_train = {o:[] for o in self.models.keys()}
            self.y_train = {o:[] for o in self.models.keys()}
            self.rewards = {o:[] for o in self.models.keys()}
            self.rewards_sum = {o:0 for o in self.models.keys()}

    def get_decision(self, gamestate, operation):
        x = np.append([self.cash, self.position], gamestate)
        res = self.models[operation].predict(np.array((x,)))

        ind = np.argmax(res[0])
        y = np.zeros(len(res[0]))
        if res[0][ind] > 0.5:
            y[ind] = 1

        self.x_train[operation].append(x)
        self.y_train[operation].append(y)
        return y


    def give_reward(self, operation, reward):
        self.rewards[operation].append(reward)
        self.rewards_sum[operation] += reward

    def learn(self):
        for o in self.models.keys():
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
