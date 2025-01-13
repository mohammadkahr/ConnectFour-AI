import numpy as np
import pygame
import sys
import math
from threading import Timer
import random

ROWS = 6
COLS = 7

PLAYER_TURN = 0
AI_TURN = 1

PLAYER_PIECE = 1
AI_PIECE = 2

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)


def create_board():
    return np.zeros((ROWS, COLS))


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[0][col] == 0


def get_next_open_row(board, col):
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == 0:
            return r


def winning_move(board, piece):
    for c in range(COLS - 3):
        for r in range(ROWS):
            if all(board[r][c + i] == piece for i in range(4)):
                return True

    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True

    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True

    for c in range(3, COLS):
        for r in range(3, ROWS):
            if all(board[r - i][c - i] == piece for i in range(4)):
                return True


def draw_board(board):
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            color = BLACK if board[r][c] == 0 else (RED if board[r][c] == PLAYER_PIECE else YELLOW)
            pygame.draw.circle(screen, color, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), circle_radius)
    pygame.display.update()


def animate_piece_drop(col, row, piece):
    y_position = 0
    color = RED if piece == PLAYER_PIECE else YELLOW
    while y_position < (row + 1) * SQUARESIZE:
        pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
        pygame.draw.circle(screen, color, (int(col * SQUARESIZE + SQUARESIZE / 2), y_position + circle_radius), circle_radius)
        y_position += 20
        pygame.time.wait(10)
        pygame.display.update()


def get_valid_locations(board):
    return [col for col in range(COLS) if is_valid_location(board, col)]


def end_game(message):
    global game_over
    label = my_font.render(message, 1, WHITE)
    screen.blit(label, (40, 10))
    pygame.display.update()
    pygame.time.wait(3000)
    game_over = True


def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)
    is_terminal = winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(valid_locations) == 0

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return None, 100000
            elif winning_move(board, PLAYER_PIECE):
                return None, -100000
            else:
                return None, 0
        return None, score_position(board, AI_PIECE)

    if maximizing_player:
        value = -math.inf
        best_col = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, AI_PIECE)
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value

    else:
        value = math.inf
        best_col = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, PLAYER_PIECE)
            new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value


def score_position(board, piece):
    score = 0

    center_array = [int(i) for i in list(board[:, COLS // 2])]
    score += center_array.count(piece) * 6

    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLS - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    for c in range(COLS):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROWS - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, piece)

    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    for r in range(3, ROWS):
        for c in range(3, COLS):
            window = [board[r - i][c - i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score


def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 4

    return score

# Initialize the game board
board = create_board()
game_over = False
turn = random.randint(PLAYER_TURN, AI_TURN)

# Initialize Pygame
pygame.init()
SQUARESIZE = 100
width = COLS * SQUARESIZE
height = (ROWS + 1) * SQUARESIZE
circle_radius = int(SQUARESIZE / 2 - 5)
size = (width, height)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Connect 4")
my_font = pygame.font.SysFont("monospace", 75)

draw_board(board)
pygame.display.update()

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            xpos = event.pos[0]
            if turn == PLAYER_TURN:
                pygame.draw.circle(screen, RED, (xpos, int(SQUARESIZE / 2)), circle_radius)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if turn == PLAYER_TURN:
                xpos = event.pos[0]
                col = int(math.floor(xpos / SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    animate_piece_drop(col, row, PLAYER_PIECE)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE):
                        end_game("PLAYER 1 WINS!")

                    turn = (turn + 1) % 2
                    draw_board(board)

    if turn == AI_TURN and not game_over:
        col, _ = minimax(board, 5, -math.inf, math.inf, True)

        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            animate_piece_drop(col, row, AI_PIECE)
            drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
                end_game("PLAYER 2 WINS!")

            turn = (turn + 1) % 2
            draw_board(board)
