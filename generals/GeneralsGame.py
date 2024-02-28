from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
import numpy as np
import time

def generate_array_with_random_ones(N, M, x):
    # Create an array of zeros
    array = np.zeros((N, M), dtype=int)
    
    # Generate x random indices
    indices = np.random.choice(N*M, x, replace=False)
    
    # Convert indices to 2D coordinates
    row_indices, col_indices = np.unravel_index(indices, (N, M))
    
    # Place ones at random positions
    array[row_indices, col_indices] = 1
    
    return array

def modify_kings(kings):
    # Find the indices of ones in the kings array
    one_indices = np.where(kings == 1)
    
    # Randomly choose one of the ones
    random_index = np.random.choice(len(one_indices[0]))
    row, col = one_indices[0][random_index], one_indices[1][random_index]
    
    # Replace the chosen one with -1
    kings[row, col] = -1
    
    return kings


class GeneralsGame(Game):
    def __init__(self, width=8, height=8, players=2, mountain=1, city=1):
        self.width = width
        self.height = height
        self.players = players
        self.mountain = mountain
        self.city = city

    def getInitBoard(self):
        num_mountains = int(np.ceil((((self.width * self.height) / 4) * self.mountain) / (self.mountain + self.city)))
        num_cities = int(np.ceil((((self.width * self.height) / 6) * self.city) / (self.mountain + self.city)))

        kings = generate_array_with_random_ones(self.width, self.height, self.players)

        metadata = np.zeros((self.width, self.height), dtype=int)

        mountains = generate_array_with_random_ones(self.width, self.height, num_mountains)
        mountains = mountains * (1 - kings)

        cities = generate_array_with_random_ones(self.width, self.height, num_cities)
        cities = cities * (1 - kings) * (1 - mountains) + kings

        kings = modify_kings(kings)
        armies = kings.copy()

        return np.stack([metadata, kings, armies, cities, mountains], axis=2)

    def getBoardSize(self):
        return (self.width, self.height)

    def getActionSize(self):
        # *4 for the 4 possible directions, *2 for splitting the army, and +1 for the pass action
        return self.width * self.height * 4 * 2 + 1

    def getNextState(self, board, player, action):
        metadata, kings, armies, cities, mountains = board[:, :, 0:1], board[:, :, 1:2], board[:, :, 2:3], board[:, :, 3:4], board[:, :, 4:]
        metadata = metadata.copy()
        armies = armies.copy()

        metadata[0][0] += 1
        if metadata[0][0] % 50 == 0:
            armies[armies * player > 0] += player
        else:
            armies[armies * player * cities > 0] += player

        if action == self.getActionSize() - 1:
            return np.concatenate((metadata, kings, armies, cities, mountains), axis=2), -player

        direction = action % 4
        split = action % 8 >= 4
        action = action // 8

        x = action % self.width
        y = action // self.width
        soldiers = armies[x, y, 0] * player
        if split:
            soldiers //= 2
            armies[x, y, 0] = soldiers * player
        else:
            armies[x, y, 0] = player
            soldiers -= 1

        if direction == 0:
            x -= 1
        elif direction == 1:
            x += 1
        elif direction == 2:
            y -= 1
        elif direction == 3:
            y += 1

        armies[x, y, 0] += soldiers * player

        return np.concatenate((metadata, kings, armies, cities, mountains), axis=2), -player

    def getValidMoves(self, board, player):
        armies, mountains = board[:, :, 2:3], board[:, :, 4:]
        valids = np.zeros(self.getActionSize())
        valids[-1] = 1

        indicies = np.argwhere(armies * player > 1)
        x, y, _ = indicies.T
        
        base_indices = (y * self.width + x) * 8

        # Check mountains
        valid_x_minus_1 = (x > 0) & (mountains[x - 1, y, 0] == 0)
        valid_x_plus_1 = (x < self.width - 1) & (mountains[(x + 1) % self.width, y, 0] == 0)
        valid_y_minus_1 = (y > 0) & (mountains[x, y - 1, 0] == 0)
        valid_y_plus_1 = (y < self.height - 1) & (mountains[x, (y + 1) % self.height, 0] == 0)
        
        # Set valids
        valids[base_indices] = valid_x_minus_1
        valids[base_indices + 1] = valid_x_plus_1
        valids[base_indices + 2] = valid_y_minus_1
        valids[base_indices + 3] = valid_y_plus_1
        valids[base_indices + 4] = valid_x_minus_1
        valids[base_indices + 5] = valid_x_plus_1
        valids[base_indices + 6] = valid_y_minus_1
        valids[base_indices + 7] = valid_y_plus_1

        return valids

    def getGameEnded(self, board, player):
        metadata, kings, armies = board[:, :, 0:1], board[:, :, 1:2], board[:, :, 2:3]

        if metadata[0][0] > 1000:
            return 0.5

        if np.any(kings * armies < 0):
            dead = np.argwhere(kings * armies < 0)[0]
            return np.sign(armies[dead[0], dead[1], 0])

        if np.sum(kings * armies) == 0:
            return 0.5

        return 0

    def getCanonicalForm(self, board, player):
        kings_armies = board[:, :, 1:3] * player
        metadata, cities, mountains = board[:, :, [0]], board[:, :, 3:4], board[:, :, 4:]
        return np.concatenate((metadata, kings_armies, cities, mountains), axis=2)

    def getSymmetries(self, board, pi):
        return [(board, pi)]

    def stringRepresentation(self, board):
        return board.tostring()

    def getScore(self, board, player):
        metadata, kings, armies, cities, mountains = np.split(board, 5, axis=2)
        mine = armies * player
        return np.sum(mine) + np.sum(mine > 0) - np.sum(mine < 0)

    @staticmethod
    def display(board):
        metadata, kings, armies, cities, mountains = np.split(board, 5, axis=2)
        print("   ", end="")
        for y in range(len(board)):
            print(y, end="     ")
        print("")
        print("----------------------------------------------------")
        for y in range(len(board[0])):
            print(y, "|", end="")
            for x in range(len(board)):
                if mountains[x][y] > 0:
                    out = "M    "
                elif kings[x][y] != 0:
                    out = "K" + '{:04d}'.format(int(armies[x][y]))
                elif cities[x][y] > 0:
                    out = "C" + '{:04d}'.format(int(armies[x][y]))
                else:
                    out = " " + '{:04d}'.format(int(armies[x][y]))

                print(out, end=" ")
            print("|")

        print("----------------------------------------------------")
