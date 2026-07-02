import numpy as np
from config import *

class Board:
    def __init__(self, board=None):
        if board is not None:
            self.board = board
        else:
            self.board = np.zeros((ROWS, COLUMNS))

    # Проверяем свободна ли ячейка для фишки
    def is_valid_pos(self, col):
        return self.board[ROWS - 1][col] == 0

    # Получаем список всех доступных ячеек для фишек
    def get_valid_pos(self):
        return [col for col in range(COLUMNS) if self.is_valid_pos(col)]

    # Ищет свободную строку для фишки в одной колонке
    def get_next_free_row(self, col):
        for row in range(ROWS):
            if self.board[row][col] == 0:
                return row
        return None

    # Размещение фишки в матрице
    def drop_piece(self, row, col, piece):
        self.board[row][col] = piece

    # Копирование доски для ИИ
    def clone(self):
        return Board(self.board.copy())

    # Проверка победы
    def check_win(self, piece):
        # Горизонталь
        for c in range(COLUMNS - 3):
            for r in range(ROWS):
                if self.board[r][c] == piece and self.board[r][c+1] == piece \
                and self.board[r][c+2] == piece and self.board[r][c+3] == piece:
                    return True

        # Вертикаль
        for c in range(COLUMNS):
            for r in range(ROWS - 3):
                if self.board[r][c] == piece and self.board[r+1][c] == piece \
                and self.board[r+2][c] == piece and self.board[r+3][c] == piece:
                    return True

        # Диагональ вверх-вправо
        for c in range(COLUMNS - 3):
            for r in range(ROWS - 3):
                if self.board[r][c] == piece and self.board[r+1][c+1] == piece \
                and self.board[r+2][c+2] == piece and self.board[r+3][c+3] == piece:
                    return True

        # Диагональ вниз-вправо
        for c in range(COLUMNS - 3):
            for r in range(3, ROWS):
                if self.board[r][c] == piece and self.board[r-1][c+1] == piece \
                and self.board[r-2][c+2] == piece and self.board[r-3][c+3] == piece:
                    return True

        return False

    # Проверка окончания партии
    def is_over(self):
        return self.check_win(REAL_PLAYER_PIECE) or self.check_win(AI_PLAYER_PIECE) \
            or len(self.get_valid_pos()) == 0