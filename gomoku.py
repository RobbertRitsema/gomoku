# update dec 2021: pretty board displays 1 as x and 2 as o, now,
# just like in the tutorial.

from typing import Tuple, List, Optional

import numpy as np

# Simple Data Types to define the game with
Board = np.array  # two-dimensional (typically 19 by 19)
GameState = Tuple[Board, int]  # The board plus the ply number.
# For example, ply==1 means: the first move on the current board still needs to be done.
# Player "black" alias "X" alias value 1 is allowed to make the first move.

Move = Tuple[int, int]  # location on the board: (row, col)
# NB: Don't worry about the warnings; nested types are still very buggy in Python type checking

SIZE = 7


def starting_state(bsize_: int = SIZE) -> GameState:
    """
    Creates a new game (start state of the game) as a square 2-dimensional numpy array of bytes (int8)
    :param bsize_: the size of the board
    :return: a new empty board, on the first ply (half-move) to make
    """
    return np.zeros((bsize_, bsize_), dtype=np.int8), 1


def valid_moves(state: GameState) -> List[Move]:
    """
    A function to check which moves are available to the agent.
    TIP: it is key to performance to not call this function move often than necessary
    :param state: the state of the game
    :return: a list of valid moves (tuples of 2 integers indicating locations on the board)
    """
    board = state[0]
    ply = state[1]
    if ply == 1:
        middle = np.array(np.shape(board)) // 2
        return [tuple(middle)]
    else:
        return list(zip(*np.where(board == 0)))


def is_game_over(state: GameState) -> bool:
    """
    A function to check whether the game is over or somebody won
    :param board: the current state of the game
    :return: a boolean indicating whether the game is over
    """
    if len(valid_moves(state)) == 0:
        return True

    board = state[0]
    bsize = np.shape(board)[0]

    # Check columns for win
    for col in board.T:
        for i in range(bsize - 4):
            # Check if all elements are the same and non-zero
            if len(set(col[i : i + 5])) == 1 and col[i] != 0:
                return True

    # Check rows for win
    for row in board:
        for i in range(bsize - 4):
            # Check if all elements are the same and non-zero
            if len(set(row[i : i + 5])) == 1 and row[i] != 0:
                return True

    # Check diagonals for win
    diags = [board[::-1, :].diagonal(i) for i in range(-bsize + 1, bsize)]
    diags.extend(board.diagonal(i) for i in range(bsize - 1, -bsize, -1))
    for diag in diags:
        for i in range(len(diag) - 4):
            # Check if all elements are the same and non-zero
            if len(set(diag[i : i + 5])) == 1 and diag[i] != 0:
                return True

    return False


def check_win(board: Board, last_move: Move) -> bool:
    if last_move is None or last_move == ():
        return False

    """This method checks whether the last move played wins the game.
    The rule for winning is: /exactly/ 5 stones line up (so not 6 or more),
    horizontally, vertically, or diagonally."""
    color = board[last_move[0]][last_move[1]]
    bsize = np.shape(board)[0]
    # check up-down
    number_ud = 1
    if last_move[1] < bsize - 1:
        lim1 = last_move[1] + 1
        lim2 = last_move[1] + 6 if last_move[1] + 6 < bsize else bsize
        for i in range(lim1, lim2):
            if board[last_move[0]][i] == color:
                number_ud += 1
            else:
                break
    if last_move[1] > 0:
        lim2 = last_move[1] - 5 if last_move[1] - 5 > 0 else 0
        for i in reversed(range(lim2, last_move[1])):
            if board[last_move[0]][i] == color:
                number_ud += 1
            else:
                break
    if number_ud == 5:
        return True
    # check left - right
    number_lr = 1
    if last_move[0] < bsize - 1:
        lim1 = last_move[0] + 1
        lim2 = last_move[0] + 6 if last_move[0] + 6 < bsize else bsize
        for i in range(lim1, lim2):
            if board[i][last_move[1]] == color:
                number_lr += 1
            else:
                break
    if last_move[0] > 0:
        lim2 = last_move[0] - 5 if last_move[0] - 5 > 0 else 0
        for i in reversed(range(lim2, last_move[0])):
            if board[i][last_move[1]] == color:
                number_lr += 1
            else:
                break
    if number_lr == 5:
        return True
    # check lower left - upper right
    number_diag = 1
    xlim = last_move[0] - 1
    ylim = last_move[1] - 1
    while xlim >= 0 and ylim >= 0:
        if board[xlim][ylim] == color:
            number_diag += 1
        else:
            break
        xlim = xlim - 1
        ylim = ylim - 1
    xlim = last_move[0] + 1
    ylim = last_move[1] + 1
    while xlim < bsize and ylim < bsize:
        if board[xlim][ylim] == color:
            number_diag += 1
        else:
            break
        xlim = xlim + 1
        ylim = ylim + 1
    if number_diag == 5:
        return True
    # check lower right - upper left
    number_diag = 1
    xlim = last_move[0] + 1
    ylim = last_move[1] - 1
    while xlim < bsize and ylim >= 0:
        if board[xlim][ylim] == color:
            number_diag += 1
        else:
            break
        xlim = xlim + 1
        ylim = ylim - 1
    xlim = last_move[0] - 1
    ylim = last_move[1] + 1
    while xlim >= 0 and ylim < bsize:
        if board[xlim][ylim] == color:
            number_diag += 1
        else:
            break
        xlim = xlim - 1
        ylim = ylim + 1
    if number_diag == 5:
        return True
    return False


def move(state: GameState, next_move: Move) -> Optional[GameState]:
    """
    A function to get to a new state when playing a move
    :param state: the current state of the game
    :param next_move: a move (tuple indicating location of stone to place)
    :return: whether the move was valid, whether the move wins the game, and the new game state
    """
    board = state[0]
    ply = state[1]
    colour = 2 if ply % 2 else 1
    if board[next_move[0]][next_move[1]] == 0:
        # for ply>3 it is always allowed to place a stone as long as the square is empty
        board[next_move[0]][next_move[1]] = colour
        return (board, ply + 1)
    else:
        return None


def pretty_board(board: Board):
    """
    Function to print the board to the standard out
    :param board: a d by d list representing the board, 0 being empty, 1 black stone, and 2 a white stone
    """
    for row in board:
        for val in row:
            if val == 0:
                print("- ", end="")
            elif val == 1:
                print("x ", end="")
            else:
                print("o ", end="")
        print()


def game_result(state: GameState):
    if state[1] % 2 == 0:
        return -1
    else:
        return 1
