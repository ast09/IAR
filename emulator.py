from random import randrange
from copy import deepcopy
import api


class Emulator:
    def __init__(self, algorithm):
        self.algorithm = algorithm

        # rewards and transition model under the idea of ((action reward + time reward), probability of success)
        self.empty_battery = {"go_forward_vacuuming": ((-100 + -1), 0.0),
                              "go_forward_no_vacuuming": ((-100 + -1), 0.0),
                              "rotate_left": ((-100 + -1), 0.0),
                              "rotate_right": ((-100 + -1), 0.0),
                              "vacuum": ((-100 + -1), 0.0),
                              "recharge": (0, 1.0)}
        self.critical_battery = {"go_forward_vacuuming": ((-3 + -1), 1.0),
                                 "go_forward_no_vacuuming": ((0 + -1), 1.0),
                                 "rotate_left": ((0 + -1), 1.0),
                                 "rotate_right": ((0 + -1), 1.0),
                                 "vacuum": ((-5 + -1), 1.0),
                                 "recharge": (0, 1.0)}
        self.sufficient_battery = {"go_forward_vacuuming": ((0 + -1), 1.0),
                                   "go_forward_no_vacuuming": ((0 + -1), 1.0),
                                   "rotate_left": ((0 + -1), 1.0),
                                   "rotate_right": ((0 + -1), 1.0),
                                   "vacuum": ((0 + -1), 1.0),
                                   "recharge": (0, 1.0)}
        self.front_wall = {"go_forward_vacuuming": (-10, 0.0),
                           "go_forward_no_vacuuming": (-10, 0.0),
                           "rotate_left": (10, 1.0),
                           "rotate_right": (10, 1.0),
                           "vacuum": (0, 1.0),
                           "recharge": (0, 1.0)}
        self.right_wall = {"go_forward_vacuuming": (0, 1.0),
                           "go_forward_no_vacuuming": (0, 1.0),
                           "rotate_left": (0, 1.0),
                           "rotate_right": (-10, 1.0),
                           "vacuum": (0, 1.0),
                           "recharge": (0, 1.0)}
        self.left_wall = {"go_forward_vacuuming": (0, 1.0),
                          "go_forward_no_vacuuming": (0, 1.0),
                          "rotate_left": (-10, 1.0),
                          "rotate_right": (0, 1.0),
                          "vacuum": (0, 1.0),
                          "recharge": (0, 1.0)}
        self.dirty_cell = {"go_forward_vacuuming": (40, 0.9),
                           "go_forward_no_vacuuming": (-40, 0.8),
                           "rotate_left": (0, 1.0),
                           "rotate_right": (0, 1.0),
                           "vacuum": (40, 1.0),
                           "recharge": (0, 1.0)}
        self.clean_cell = {"go_forward_vacuuming": (-10, 0.9),
                           "go_forward_no_vacuuming": (5, 0.9),
                           "rotate_left": (0, 1.0),
                           "rotate_right": (0, 1.0),
                           "vacuum": (-10, 1.0),
                           "recharge": (0, 1.0)}

    """
    Simulate the model according to the algorithm we're using
    """

    def simulate(self, state, action):
        reward = 0
        probability = 1.0
        newstate = deepcopy(state)

        # Checks that the action exists
        api.ACTIONS.index(action)

        if state.robot is not None and state.mapp is not None:

            if state.is_final_state():
                reward += 100
                return reward, newstate, probability

            # Battery check
            if state.robot.battery == 0:
                reward += self.empty_battery.get(action)[0]
                probability *= self.empty_battery.get(action)[1]
            elif state.robot.battery <= 10:
                reward += self.critical_battery.get(action)[0]
                probability *= self.critical_battery.get(action)[1]
            elif state.robot.battery >= 10:
                reward += self.sufficient_battery.get(action)[0]
                probability *= self.sufficient_battery.get(action)[1]

            # Position check
            if state.robot.orientation == 0:
                if state.robot.x == 0:
                    reward += self.left_wall.get(action)[0]
                    probability *= self.left_wall.get(action)[1]
                if state.robot.y == 0:
                    reward += self.front_wall.get(action)[0]
                    probability *= self.front_wall.get(action)[1]
                if state.robot.x == api.MAPSIZE - 1:
                    reward += self.right_wall.get(action)[0]
                    probability *= self.right_wall.get(action)[1]

            elif state.robot.orientation == 1:
                if state.robot.y == 0:
                    reward += self.left_wall.get(action)[0]
                    probability *= self.left_wall.get(action)[1]
                if state.robot.x == api.MAPSIZE - 1:
                    reward += self.front_wall.get(action)[0]
                    probability *= self.front_wall.get(action)[1]
                if state.robot.y == api.MAPSIZE - 1:
                    reward += self.right_wall.get(action)[0]
                    probability *= self.right_wall.get(action)[1]

            elif state.robot.orientation == 2:
                if state.robot.x == api.MAPSIZE - 1:
                    reward += self.left_wall.get(action)[0]
                    probability *= self.left_wall.get(action)[1]
                if state.robot.y == api.MAPSIZE - 1:
                    reward += self.front_wall.get(action)[0]
                    probability *= self.front_wall.get(action)[1]
                if state.robot.x == 0:
                    reward += self.right_wall.get(action)[0]
                    probability *= self.right_wall.get(action)[1]

            elif state.robot.orientation == 3:
                if state.robot.y == api.MAPSIZE - 1:
                    reward += self.left_wall.get(action)[0]
                    probability *= self.left_wall.get(action)[1]
                if state.robot.x == 0:
                    reward += self.front_wall.get(action)[0]
                    probability *= self.front_wall.get(action)[1]
                if state.robot.y == 0:
                    reward += self.right_wall.get(action)[0]
                    probability *= self.right_wall.get(action)[1]

            # Dirtiness check
            if newstate.mapp[state.robot.x][state.robot.y].dirty == 0:
                reward += self.clean_cell.get(action)[0]
                probability *= self.clean_cell.get(action)[1]
            elif newstate.mapp[state.robot.x][state.robot.y].dirty == 1:
                reward += self.dirty_cell.get(action)[0]
                probability *= self.dirty_cell.get(action)[1]

            if self.algorithm == "DP":
                newstate2 = deepcopy(state)
                # Probability computation and robot parameters update
                if action == "recharge":
                    if state.robot.x == state.base[0] and state.robot.y == state.base[1]:
                        if state.robot.battery == 100:
                            reward = reward - 20
                        else:
                            newstate.robot.battery = 100
                            newstate2.robot.battery = 100
                            reward += 20
                    else:
                        reward = reward - 20
                elif action == "go_forward_vacuuming":
                    newstate.robot.go_forward()
                    newstate.mapp[state.robot.x][state.robot.y].clean()
                    newstate2.mapp[state.robot.x][state.robot.y].clean()
                    newstate.robot.lower_battery()
                    newstate2.robot.lower_battery()
                elif action == "go_forward_no_vacuuming":
                    newstate.robot.go_forward()
                    newstate.robot.lower_battery()
                    newstate2.robot.lower_battery()
                elif action == "rotate_right":
                    newstate.robot.rotate_right()
                elif action == "rotate_left":
                    newstate.robot.rotate_left()
                elif action == "vacuum":
                    newstate.mapp[state.robot.x][state.robot.y].clean()
                    newstate.robot.lower_battery()

                return reward, [newstate, newstate2], probability

            elif self.algorithm == "MC":

                # Probability computation and robot parameters update
                if action == "recharge":
                    if state.robot.x == state.base[0] and state.robot.y == state.base[1]:
                        if state.robot.battery == 100:
                            reward = reward - 20
                        else:
                            newstate.robot.battery = 100
                            reward += 20
                    else:
                        reward = reward - 20
                elif action == "go_forward_vacuuming":
                    dice = randrange(1, 100)
                    if dice <= probability * 100:
                        newstate.robot.go_forward()
                        newstate.mapp[state.robot.x][state.robot.y].clean()
                        newstate.robot.lower_battery()
                elif action == "go_forward_no_vacuuming":
                    dice = randrange(1, 100)
                    if dice <= probability * 100:
                        newstate.robot.go_forward()
                elif action == "rotate_right":
                    newstate.robot.rotate_right()
                elif action == "rotate_left":
                    newstate.robot.rotate_left()
                elif action == "vacuum":
                    newstate.mapp[state.robot.x][state.robot.y].clean()
                    newstate.robot.lower_battery()

                return reward, newstate, probability
        else:
            print("Unrecognized state in function simulate")
            return



