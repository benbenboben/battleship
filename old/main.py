

import numpy as np
import battleship
from battleship import BattleShip
import itertools as it

np.set_printoptions(linewidth=100, precision=3)
bs = BattleShip()

#for i, b in enumerate(bs.possible_ship_configs(bs.enemy_ships)):
#    print(i)
#    print(b)

#for s in bs.enemy_ships[0:3]:
#    print(s.size)

master_freq = np.zeros((battleship.LEN, battleship.LEN), dtype=int)
for pair in it.combinations(bs.enemy_ships, 3):
    sizes = [str(s.size) for s in pair]
    print(' '.join(sizes))
    freq = np.zeros((battleship.LEN, battleship.LEN), dtype=int)
    for i, b in enumerate(bs.possible_ship_configs2(pair, [])):
        freq += b
    master_freq += freq

print(master_freq)
#print(i + 1)
#print(freq / (i + 1) * 100)

#freq = np.zeros((battleship.LEN, battleship.LEN), dtype=int)
#bs.enemy_game_board[5, 5] = -1
#for i, b in enumerate(bs.possible_ship_configs2(bs.enemy_ships[1:4], [], game_board=bs.enemy_game_board)):
#    freq += b

#print(i + 1)
#print(freq / (i + 1) * 100)

#freq = np.zeros((battleship.LEN, battleship.LEN), dtype=int)
#bs.enemy_game_board[4, 4] = -1
#for i, b in enumerate(bs.possible_ship_configs2(bs.enemy_ships[1:4], [], game_board=bs.enemy_game_board)):
#    freq += b

#print(i + 1)
#print(freq / (i + 1) * 100)
