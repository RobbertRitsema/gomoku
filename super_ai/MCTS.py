import copy
import time

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
        self.q = 0
        self._untried_moves = gomoku.valid_moves(self.state)
        self._black = black
        self.qn_ratio = 0

    def best_move(self, max_time_to_move: int = 1000) -> "MCTS":
        """
        max_time_to_move: the maximum time until the agent is required to make a move in milliseconds
        """
        start_time = time.time()
        while True:
            node = self._add_node_to_tree()
            reward = node._rollout()
            node._backpropagate(reward)

            elapsed_time = (time.time() - start_time) * 1000
            if elapsed_time > max_time_to_move:
                break

        best_node = self.children[0]
        for child in self.children:
            child.qn_ratio = child.q / child.number_of_visits()
            if best_node.qn_ratio < child.qn_ratio:
                best_node = child

        return best_node

    def _add_node_to_tree(self) -> "MCTS":
        """
        if the current node in the tree is not a terminal node, it will expand the tree
        """
        if not self.is_fully_expanded():
            move = self._untried_moves.pop()
            next_state = gomoku.move(copy.deepcopy(self.state), move)
            assert next_state is not None, "Invalid move!"

            child_node = MCTS(next_state, black=not self._black, parent=self, move=move)

            self.children.append(child_node)
            return child_node

        return self._best_child()

    def _backpropagate(self, reward: int) -> None:
        self._number_of_visits += 1
        self.q += reward

        if self.parent:
            self.parent._backpropagate(reward)

    def _best_child(self, c_param=0.2) -> "MCTS":
        choices_weights = []
        for child in self.children:
            q_value = child.q
            visits = child.number_of_visits()
            parent_visits = self.number_of_visits()
            uct_value = (q_value / visits) + c_param * np.sqrt(
                (2 * np.log(parent_visits) / visits)
            )

            choices_weights.append(uct_value)

        return self.children[np.argmax(choices_weights)]

    def _rollout(self) -> int:
        current_rollout_state = copy.deepcopy(self.state)
        untried_moves = copy.copy(self._untried_moves)
        action = self.move

        while (
            current_rollout_state is not None
            and untried_moves.__len__() != 0
            and not gomoku.is_game_over(current_rollout_state)
        ):
            action = untried_moves.pop(np.random.randint(len(untried_moves)))
            current_rollout_state = gomoku.move(current_rollout_state, action)

        if current_rollout_state is None or action is None:
            return 0

        if not gomoku.check_win(current_rollout_state[0], action):
            return 0

        if gomoku.game_result(current_rollout_state) == 1:
            return 1 if self._black else -1
        else:
            return -1 if self._black else 1

    def is_fully_expanded(self) -> bool:
        return len(self._untried_moves) == 0

    def number_of_visits(self) -> int:
        return self._number_of_visits

    def total_child_visits(self) -> int:
        total_visits = self._number_of_visits
        for child in self.children:
            total_visits += child.total_child_visits()

        return total_visits
