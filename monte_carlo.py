import copy
from emulator import Emulator
from state import State
from robot import Robot
import random
import api


class MC:
    emulator = Emulator("MC")
    epsilon = 0.1
    alpha = 0.001
    gamma = 0.9
    Q_function = {}

    def argmax_q_function(self, state):
        """
        Calculate argmax(a) of Q(s, a)
        :return: a ( the action that maximizez Q(s,a) ), max_q (the maximal value)
        """
        a = api.ACTIONS[random.randrange(len(api.ACTIONS))]
        if (state, a) not in self.Q_function.keys():
            self.Q_function[(state, a)] = 0
        max_q = self.Q_function[(state, a)]
        for action in api.ACTIONS:
            if (state, action) not in self.Q_function.keys():
                self.Q_function[(state, action)] = 0
            if self.Q_function[(state, action)] > max_q:
                max_q = self.Q_function[(state, action)]
                a = action
        return a, max_q

    def generate_episode(self, length):
        """
        Generate an episode
        :param length: number of (s, a, r) sequences
        :return: list of (s, a, r) sequences
        """

        episode = []
        index_episode = 0

        # (s0, a0, r0) generation

        s = State(Robot(0, 0, api.MAPSIZE, api.MAPSIZE, 1, 100), api.INITIAL_MAP, (0, 0))
        id_s = s.to_string()

        # epsilon-greedy choice of a0

        dice = random.uniform(0, 1)
        if dice > self.epsilon:
            a = self.argmax_q_function(id_s)[0]
        else:
            a = copy.copy(api.ACTIONS[random.randrange(len(api.ACTIONS))])

        r = self.emulator.simulate(s, a)[0]

        episode.append([id_s, a, r])

        # Generation of the nex length-1 sequences

        while index_episode < length and s.robot.battery >= 0 and not s.is_final_state():
            index_episode += 1
            s = self.emulator.simulate(s, a)[1]
            id_s = s.to_string()

            # epsilon-greedy choice of a0

            dice = random.uniform(0, 1)
            if dice > self.epsilon:
                a = self.argmax_q_function(id_s)[0]
            else:
                a = copy.copy(api.ACTIONS[random.randrange(len(api.ACTIONS))])

            r = self.emulator.simulate(s, a)[0]

            episode.append([id_s, a, r])
        return episode

    def run(self, limit, T):
        """
        Run Monte Carlo algorithm
        :param limit: when to stop algorithm ( limit -> infinity)
        :param T: episodes length
        :return: max Q(s0, a)
        """
        i = 0
        G = {}

        while i < limit:
            i += 1
            episode = self.generate_episode(T)
            ep_length = len(episode)
            for t in range(0, ep_length):
                G[t] = 0
                for k in range(t, ep_length):
                    G[t] += episode[k][2] * (self.gamma ** k)
                if (episode[t][0], episode[t][1]) in self.Q_function.keys():
                    self.Q_function[(episode[t][0], episode[t][1])] = self.Q_function[(episode[t][0], episode[t][1])] + self.alpha * (G[t] - self.Q_function[(episode[t][0], episode[t][1])])
                else:
                    self.Q_function[(episode[t][0], episode[t][1])] = self.alpha * G[t]
        return self.argmax_q_function(api.INITIAL_STATE.to_string())[1]
