import time
from collections import defaultdict
from copy import deepcopy

import numpy as np

import gomoku
from gomoku import GameState


class MCTS:
    def __init__(self, state: GameState, black, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self._number_of_visits = 0
        self._results = defaultdict(int)
        self._results[1] = 0
        self._results[-1] = 0
        self._untried_moves = gomoku.valid_moves(self.state)
        self._black = black
        self.uct_value = None

    def best_move(self, max_time_to_move: int = 10000):
        """
        max_time_to_move: the maximum time until the agent is required to make a move in milliseconds
        """
        max_time_to_move = 10000
        start_time = time.time()  # record the start time
        while True:
            node = self.add_node_to_tree()
            reward = node.rollout()
            node.backpropagate(reward)

            elapsed_time = (
                time.time() - start_time
            ) * 1000  # calculate elapsed time in milliseconds
            if elapsed_time > max_time_to_move:
                break  # if elapsed time exceeds max_time_to_move, break the loop

        best_child = self.best_child()
        return best_child

    def add_node_to_tree(self):
        """
        if the current node in the tree is not a terminal node, it will expand the tree
        """
        current_node = self

        while not gomoku.is_game_over(current_node.state):
            if current_node.is_fully_expanded():
                current_node = current_node.best_child()
            else:
                return current_node.expand()

        return current_node

    def expand(self):
        move = self._untried_moves.pop()
        next_state = gomoku.move(deepcopy(self.state), move)
        if next_state is None:
            return

        child_node = MCTS(next_state, black=self._black, parent=self, move=move)

        self.children.append(child_node)
        return child_node

    def backpropagate(self, result):
        self._number_of_visits += 1
        self._results[result] += 1
        if self.parent:
            self.parent.backpropagate(result)

    def best_child(self, c_param=0.2):
        choices_weights = []
        for child in self.children:
            q_value = child.win_lose_ratio()
            visits = child.number_of_visits()
            parent_visits = self.number_of_visits()
            uct_value = (q_value / visits) + c_param * np.sqrt(
                (2 * np.log(parent_visits) / visits)
            )
            child.uct_value = uct_value

            choices_weights.append(uct_value)

        best_child = self.children[np.argmax(choices_weights)]

        return best_child

    def rollout(self):
        current_rollout_state = deepcopy(self.state)
        action = self.move

        while not gomoku.is_game_over(current_rollout_state):
            possible_moves = gomoku.valid_moves(current_rollout_state)

            action = possible_moves[np.random.randint(len(possible_moves))]
            current_rollout_state = gomoku.move(current_rollout_state, action)

        # TODO: should this check which player plays?
        result = gomoku.check_win(current_rollout_state[0], action)
        if result:
            return 1
        else:
            return -1

    def is_fully_expanded(self):
        return len(self._untried_moves) == 0

    def win_lose_ratio(self):
        wins = self._results[1]
        loses = self._results[-1]
        return wins - loses

    def number_of_visits(self):
        return self._number_of_visits
