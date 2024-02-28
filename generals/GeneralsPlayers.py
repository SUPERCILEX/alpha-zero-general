import numpy as np


class RandomPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        a = np.random.randint(self.game.getActionSize())
        valids = self.game.getValidMoves(board, 1)
        while valids[a]!=1:
            a = np.random.randint(self.game.getActionSize())
        return a


class HumanPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        valid = self.game.getValidMoves(board, 1)
        for i in range(len(valid) - 1):
            if valid[i]:
                print("[", int(i/8 % self.game.width), int(i/8 / self.game.width), i % 8, end="] ")
        print("[PASS]")

        while True: 
            a = input().lower()

            if a == "pass" or a == "":
                a = self.game.getActionSize() - 1
            else:
                try:
                    y,x,dir = [int(x) for x in a.split(' ')]
                    a = 8 * self.game.width * x + 8 * y + dir
                except:
                    print('Bad input')
                    continue

            if valid[a]:
                break
            else:
                print('Invalid')

        return a


class GreedyPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        candidates = []
        for a in np.argwhere(self.game.getValidMoves(board, 1) == 1):
            nextBoard, _ = self.game.getNextState(board, 1, a)
            nextBoard, _ = self.game.getNextState(nextBoard, 1, self.game.getActionSize() - 1)
            nextBoard, _ = self.game.getNextState(nextBoard, -1, self.game.getActionSize() - 1)
            score = self.game.getScore(nextBoard, 1)
            candidates += [(-score, np.random.randint(np.iinfo(np.int64).max), a)]
        candidates.sort()
        return candidates[0][2]
