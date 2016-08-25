

import numpy as np
from battleship_classes import BattleShip


np.set_printoptions(linewidth=100, precision=3)
bs = BattleShip()

while len(bs.ships) > 0:
    bs.find_best_move(refine=False)
    #bs.show_freq_board()
    print(bs.freq_board)
    print('optimal move: {}'.format(bs.show_move()))
    bs.get_move()
    print('chosen move: {}'.format(bs.show_move()))
    bs.shot_result()
