import Arena
from MCTS import MCTS
from generals.GeneralsGame import GeneralsGame
from generals.GeneralsPlayers import *
from generals.pytorch.NNet import NNetWrapper as NNet


import numpy as np
from utils import *

g = GeneralsGame()

# all players
rp = RandomPlayer(g).play
gp = GreedyPlayer(g).play
hp = HumanPlayer(g).play

arena = Arena.Arena(hp, gp, g, display=GeneralsGame.display)

print(arena.playGames(2, verbose=True))
