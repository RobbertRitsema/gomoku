import copy
import time
from collections import defaultdict
import concurrent.futures

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

    def best_move(self, max_time_to_move: int = 1000):
        """
        max_time_to_move: the maximum time until the agent is required to make a move in milliseconds
        """
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            while True:
                future = executor.submit(self.add_node_to_tree)
                node = future.result()
                reward = node.rollout()
                node.backpropagate(reward)

                elapsed_time = (time.time() - start_time) * 1000
                if elapsed_time > max_time_to_move:
                    break

        bestNode = self.children[0]
        for node in self.children:
            qn_ratio = node.win_lose_ratio() / node.number_of_visits()
            if qn_ratio > bestNode.win_lose_ratio() / bestNode.number_of_visits():
                bestNode = node
        return bestNode

    def add_node_to_tree(self):
        """
        if the current node in the tree is not a terminal node, it will expand the tree
        """
        if gomoku.is_game_over(self.state):
            return self

        if not self.is_fully_expanded():
            move = self._untried_moves.pop()
            next_state = gomoku.move(copy.deepcopy(self.state), move)
            if next_state is None:
                return

            child_node = MCTS(next_state, black=self._black, parent=self, move=move)

            self.children.append(child_node)
            return child_node

        return self.best_child()

    def backpropagate(self, result):
        self._number_of_visits += 1
        opponent_at_move = self.state[1] % 2 == self._black
        # TODO: I don't think this works
        if opponent_at_move:
            self._results[result] -= 1
        else:
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

        return self.children[np.argmax(choices_weights)]

    def rollout(self):
        current_rollout_state = copy.deepcopy(self.state)
        action = self.move

        while not gomoku.is_game_over(current_rollout_state):
            possible_moves = gomoku.valid_moves(current_rollout_state)
            action = possible_moves[np.random.randint(len(possible_moves))]
            current_rollout_state = gomoku.move(current_rollout_state, action)

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

