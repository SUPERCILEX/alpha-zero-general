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

nn = NNet(g)
nn.load_checkpoint('./temp/','best.pth.tar')
args = dotdict({'numMCTSSims': 50, 'cpuct':1.0})
mcts = MCTS(g, nn, args)
nnp = lambda x: np.argmax(mcts.getActionProb(x, temp=0))

from torchinfo import summary
summary(nn.nnet, input_size=(5,g.width,g.height))

arena = Arena.Arena(nnp, gp, g, display=GeneralsGame.display)

print(arena.playGames(2, verbose=True))
