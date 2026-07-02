import time

import pygame as pg
import sys
import math
import random
from config import *
from board import Board

class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Connect 4 Game")

        self.width = COLUMNS * DISC_SIZE
        self.height = (ROWS + 1) * DISC_SIZE
        self.screen = pg.display.set_mode((self.width, self.height))
        self.font = pg.font.SysFont("Calibri", 60)

        self.board = Board()
        self.turn = random.randint(REAL_PLAYER, AI_PLAYER)
        self.game_over = False

    def draw(self):
        for c in range(COLUMNS):
            for r in range(ROWS):
                pg.draw.rect(self.screen, BLUE, (c * DISC_SIZE, r * DISC_SIZE + DISC_SIZE, DISC_SIZE, DISC_SIZE))
                pg.draw.circle(self.screen, WHITE,
                               (int(c * DISC_SIZE + DISC_SIZE / 2), int(r * DISC_SIZE + DISC_SIZE + DISC_SIZE / 2)),
                               DISC_RADIUS)

        for c in range(COLUMNS):
            for r in range(ROWS):
                if self.board.board[r][c] == REAL_PLAYER_PIECE:
                    pg.draw.circle(self.screen, RED, (int(c * DISC_SIZE + DISC_SIZE / 2),
                                                      self.height - int(r * DISC_SIZE + DISC_SIZE / 2)), DISC_RADIUS)
                elif self.board.board[r][c] == AI_PLAYER_PIECE:
                    pg.draw.circle(self.screen, YELLOW, (int(c * DISC_SIZE + DISC_SIZE / 2),
                                                         self.height - int(r * DISC_SIZE + DISC_SIZE / 2)), DISC_RADIUS)
        pg.display.update()

    def display_winner(self, message, color):
        label = self.font.render(message, True, color)
        self.screen.blit(label, (10, 10))
        self.game_over = True
        self.draw()

    def play_again(self, message, color):
        self.screen.fill(WHITE)
        label = self.font.render(message, True, color)
        self.screen.blit(label, (140, 140))
        pg.display.update()
        self.game_over = True

    @staticmethod
    def evaluate_window(window, piece):
        score = 0
        opp_piece = REAL_PLAYER_PIECE if piece == AI_PLAYER_PIECE else AI_PLAYER_PIECE

        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(EMPTY) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(EMPTY) == 2:
            score += 2

        if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
            score -= 4

        return score

    def get_total_score(self, board_obj, piece):
        score = 0
        grid = board_obj.board

        # оценка за фишки в центральной линии
        center_array = [int(i) for i in list(grid[:, COLUMNS//2])]
        score += center_array.count(piece) * 3

        # оценка комбинаций по горизонтали
        for r in range(ROWS):
            row_array = [int(i) for i in list(grid[r, :])]
            for c in range(COLUMNS-3):
                window = row_array[c:c+4]
                score += self.evaluate_window(window, piece)

        # оценка комбинаций по вертикали
        for c in range(COLUMNS):
            col_array = [int(i) for i in list(grid[:, c])]
            for r in range(ROWS-3):
                window = col_array[r:r+4]
                score += self.evaluate_window(window, piece)

        # оценка комбинаций по диагонали вверх-вправо
        for r in range(ROWS - 3):
            for c in range(COLUMNS-3):
                window = [grid[r+i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        # оценка комбинаций по диагонали вниз-вправо
        for r in range(ROWS - 3):
            for c in range(COLUMNS-3):
                window = [grid[r+3-i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        return score

    def minimax(self, current_board: Board, depth, alpha, beta, max_player):
        valid_moves = current_board.get_valid_pos()
        game_over = current_board.is_over()

        if depth == 0:
            if game_over:
                if current_board.check_win(REAL_PLAYER_PIECE):
                    return None, -10 ** 13
                elif current_board.check_win(AI_PLAYER_PIECE):
                    return None, 10 ** 14
                else:
                    return None, 0
            else:
                return None, self.get_total_score(current_board, AI_PLAYER_PIECE)

        if max_player:
            value = -math.inf
            column = random.choice(valid_moves)

            for col in valid_moves:
                row = current_board.get_next_free_row(col)
                board_copy = current_board.clone()

                board_copy.drop_piece(row, col, AI_PLAYER_PIECE)

                new_score = self.minimax(board_copy, depth-1, alpha, beta, False)[1]

                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break

            return column, value
        else:
            value = math.inf
            column = random.choice(valid_moves)

            for col in valid_moves:
                row = current_board.get_next_free_row(col)
                board_copy = current_board.clone()
                board_copy.drop_piece(row, col, REAL_PLAYER_PIECE)

                new_score = self.minimax(board_copy, depth-1, alpha, beta, True)[1]

                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break

            return column, value

    def play(self):
        self.draw()
        while not self.game_over:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    sys.exit()

                if event.type == pg.MOUSEMOTION:
                    pg.draw.rect(self.screen, WHITE, (0, 0, self.width, DISC_SIZE))
                    pos_x = event.pos[0]
                    if self.turn == REAL_PLAYER:
                        pg.draw.circle(self.screen, RED, (pos_x, int(DISC_SIZE / 2)), DISC_RADIUS)
                    pg.display.update()

                if event.type == pg.MOUSEBUTTONDOWN:
                    pg.draw.rect(self.screen, WHITE, (0, 0, self.width, DISC_SIZE))

                    if self.turn == REAL_PLAYER:
                        pos_x = event.pos[0]
                        col = int(pos_x / DISC_SIZE)

                        if self.board.is_valid_pos(col):
                            row = self.board.get_next_free_row(col)
                            self.board.drop_piece(row, col, REAL_PLAYER_PIECE)

                            if self.board.check_win(REAL_PLAYER_PIECE):
                                self.display_winner("Вы победили!", RED)
                                time.sleep(3)

                            self.draw()
                            self.turn = (self.turn + 1) % 2

            if self.turn == AI_PLAYER and not self.game_over:
                col, minimax_score = self.minimax(self.board, 5, -math.inf, math.inf, True)
                if self.board.is_valid_pos(col):
                    pg.time.wait(300)
                    row = self.board.get_next_free_row(col)
                    self.board.drop_piece(row, col, AI_PLAYER_PIECE)

                    if self.board.check_win(AI_PLAYER_PIECE):
                        self.display_winner("Машина победила!", BLACK)
                        time.sleep(3)

                    self.draw()
                    self.turn = (self.turn + 1) % 2

            if self.game_over:
                self.play_again("Play again?", BLACK)
                waiting = True
                while waiting:
                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            pg.quit()
                            sys.exit()
                        if event.type == pg.KEYDOWN:
                            if event.key == pg.K_RETURN:
                                waiting = False
                                self.board = Board()
                                self.turn = random.randint(REAL_PLAYER, AI_PLAYER)
                                self.game_over = False
                                self.play()
                            elif event.key == pg.K_ESCAPE:
                                pg.quit()
                                sys.exit()

if __name__ == "__main__":
    game = Game()
    game.play()
    pg.quit()