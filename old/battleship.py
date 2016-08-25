

import numpy as np
import random
import copy

#board
LEN = 10

class BattleShip(object):

    def __init__(self):
        """
        initialize enemy pieces and enemy game board
        """
        carrier = np.ones((5, ), dtype=int)
        battleship = np.ones((4, ), dtype=int)
        submarine = np.ones((3, ), dtype=int)
        cruiser = np.ones((3, ), dtype=int)
        destroyer = np.ones((2, ), dtype=int)
        self.enemy_ships = [carrier, battleship, submarine, cruiser, destroyer]
        #self.enemy_ships=[carrier]
        self.enemy_game_board = np.zeros((LEN, LEN), dtype=int)
        self.prob_board = np.zeros((LEN, LEN), dtype=float)

    @staticmethod
    def possible_ship_configs(ships, board=np.zeros((LEN, LEN), dtype=int)):
        if len(ships) == 0:
            yield board
            #print(board)
            #tmp = input('hit enger')
            #yield board
        else:
            ship = ships[0]
            max_idx = board.shape[0] - ship.shape[0] + 1
            ## if hits exist place ship on hit
            for ix in range(max_idx):
                for iy in range(board.shape[1]):
                    if np.count_nonzero(board[ix: ix + ship.shape[0], iy]) == 0:
                        #count += 1
                        board[ix: ix + ship.shape[0], iy] = 1
                        #aggregate_board[ix: ix + ship.shape[0], iy] += 1
                        yield from BattleShip.possible_ship_configs(ships[1:], board)
                        board[ix: ix + ship.shape[0], iy] = 0
            for ix in range(board.shape[0]):
                for iy in range(max_idx):
                    if np.count_nonzero(board[ix, iy: iy + ship.shape[0]]) == 0:
                        #count += 1
                        board[ix, iy: iy + ship.shape[0]] = 1
                        #aggregate_board[ix, iy: iy + ship.shape[0]] += 1
                        yield from BattleShip.possible_ship_configs(ships[1:], board)
                        board[ix, iy: iy + ship.shape[0]] = 0

    @staticmethod
    def possible_ship_configs2(ships, hits, board=np.zeros((LEN, LEN), dtype=int), game_board=np.zeros((LEN, LEN), dtype=int)):
        if len(ships) == 0:
            yield board
        else:
            empty_hits = False
            for hit in hits:
                if board[hit[0], hit[1]] != 1:
                    empty_hits = True
            ship = ships[0]
            if empty_hits:
                for hit in hits:
                    if board[hit[0], hit[1]] != 1:
                        min_x = max(0, hit[0] - ship.shape[0] + 1)
                        for ix in range(min_x, hit[0] + 1):
                            if np.count_nonzero(board[ix: ix + ship.shape[0], hit[1]]) == 0 \
                            and np.count_nonzero(game_board[ix: ix + ship.shape[0], hit[1]]) == 0 \
                            and ix + ship.shape[0] < LEN:
                                board[ix: ix + ship.shape[0], hit[1]] = 1
                                yield from BattleShip.possible_ship_configs2(ships[1:], hits, board, game_board)
                                board[ix: ix + ship.shape[0], hit[1]] = 0
                        min_y = max(0, hit[1] - ship.shape[0] + 1)
                        for iy in range(min_y, hit[1] + 1):
                            if np.count_nonzero(board[hit[0], iy: iy + ship.shape[0]]) == 0 \
                            and np.count_nonzero(game_board[hit[0], iy: iy + ship.shape[0]]) == 0 \
                            and iy + ship.shape[0] < LEN:
                                board[hit[0], iy: iy + ship.shape[0]] = 1
                                yield from BattleShip.possible_ship_configs2(ships[1:], hits, board, game_board)
                                board[hit[0], iy: iy + ship.shape[0]] = 0
            else:
                max_idx = board.shape[0] - ship.shape[0] + 1
                for ix in range(max_idx):
                    for iy in range(board.shape[1]):
                        if np.count_nonzero(board[ix: ix + ship.shape[0], iy]) == 0 \
                        and np.count_nonzero(game_board[ix: ix + ship.shape[0], iy]) == 0:
                            board[ix: ix + ship.shape[0], iy] = 1
                            yield from BattleShip.possible_ship_configs2(ships[1:], hits, board, game_board)
                            board[ix: ix + ship.shape[0], iy] = 0
                for ix in range(board.shape[0]):
                    for iy in range(max_idx):
                        if np.count_nonzero(board[ix, iy: iy + ship.shape[0]]) == 0 \
                        and np.count_nonzero(game_board[ix, iy: iy + ship.shape[0]]) == 0:
                            board[ix, iy: iy + ship.shape[0]] = 1
                            yield from BattleShip.possible_ship_configs2(ships[1:], hits, board, game_board)
                            board[ix, iy: iy + ship.shape[0]] = 0

#    @staticmethod
#    def mc_ship_placement(ships, game_board):
#        prob_board = np.zeros((LEN, LEN), dtype=int)
#        for s in ships:
#            ship_is_set = False
#            ship_len = s.shape[0]
#            while not ship_is_set:
#                row, vec = np.random.randint(LEN, size=2)
#                directions = np.asarray(['u', 'r', 'd', 'l'], dtype=str)
#                np.random.shuffle(directions)
#                for direction in directions:
#                    if direction == 'u':
#                        if row - ship_len >= 0 and np.count_nonzero(game_board[row - ship_len: row + 1, vec]) == 0:
#                            prob_board[row - ship_len: row + 1, vec] = 1
#                            ship_is_set = True
#                            break
#                    if direction == 'r':
#                        if vec + ship_len <= 9 and np.count_nonzero(game_board[row, vec: vec + ship_len + 1]) == 0:
#                            prob_board[row, vec: vec + ship_len + 1] = 1
#                            ship_is_set = True
#                            break
#                    if direction == 'd':
#                        if row + ship_len <= 9 and np.count_nonzero(game_board[row: row + ship_len + 1, vec]) == 0:
#                            prob_board[row: row + ship_len + 1, vec] = 1
#                            ship_is_set = True
#                            break
#                    if direction == 'l':
#                        if vec - ship_len >= 0 and np.count_nonzero(game_board[row, vec - ship_len: vec + 1]) == 0:
#                            prob_board[row, vec - ship_len: vec + 1] = 1
#                            ship_is_set = True
#                            break
#        return prob_board

    @staticmethod
    def mc_prob_distribution(ships, board, hits, ntrials=25000):
        agg_board = np.zeros((LEN, LEN), dtype=int)
        for _ in range(ntrials):
            new_dist = BattleShip.mc_ship_placement2(ships, board, hits)
            #print(new_dist)
            agg_board += new_dist
        if len(hits) > 0:
            for h in hits:
                row, vec = h
                agg_board[row, vec] = 0.0e0
        return agg_board / ntrials * 100

    @staticmethod
    def mc_ship_placement2(ships, game_board, hits):
        #prob_board = np.zeros((LEN, LEN), dtype=int)
        prob_board = np.zeros((LEN, LEN), dtype=int)
        if len(hits) == 0:
            #print('no hits')
            random.shuffle(ships)
            for s in ships:
                ship_len = s.shape[0]
                while True:
                    direction = random.choice([0, 1])
                    if direction == 0:
                        anchor_vec = random.randint(0, 9)
                        anchor_row = random.randint(0, 9 - ship_len + 1)
                        if np.any(game_board[anchor_row: anchor_row + ship_len, anchor_vec] == -1) \
                        or np.any(prob_board[anchor_row: anchor_row + ship_len, anchor_vec] == 1):
                            continue
                        else:
                            prob_board[anchor_row: anchor_row + ship_len, anchor_vec] = 1
                            break
                    else:
                        anchor_row = random.randint(0, 9)
                        anchor_vec = random.randint(0, 9 - ship_len + 1)
                        if np.any(game_board[anchor_row, anchor_vec: anchor_vec + ship_len] == -1) \
                        or np.any(prob_board[anchor_row, anchor_vec: anchor_vec + ship_len] == 1):
                            continue
                        else:
                            prob_board[anchor_row, anchor_vec: anchor_vec + ship_len] = 1
                            break
            return prob_board
        else:
            #print('hits')
            #all_ships_set = False
            ntrial = 0
            while True:
                ntrial += 1
                #print(ntrial)
                temp_hits = copy.deepcopy(hits)
                num_ships = len(ships)
                random.shuffle(ships)
                for s in ships:
                    ship_len = s.shape[0]
                    if len(temp_hits) > 0:
                        anchor_row, anchor_vec = random.choice(temp_hits)
                        temp_hits.remove((anchor_row, anchor_vec))
                    else:
                        anchor_row, anchor_vec = None, None
                    direction = random.choice([0, 1])
                    if direction == 0:
                        #print('direction {}'.format(direction))
                        #print('anchor_row, anchor_vec {}  {}'.format(anchor_row, anchor_vec))
                        if anchor_row == None or anchor_vec == None:
                            anchor_row = random.randint(0, LEN - 1 - ship_len + 1)
                            anchor_vec = random.randint(0, LEN - 1)
                        else:
                            anchor_row = random.randint(max(0, anchor_row - ship_len + 1), anchor_row)
                            #print('new anchor_row, anchor_vec {}  {}'.format(anchor_row, anchor_vec))
                        if np.any(game_board[anchor_row: anchor_row + ship_len, anchor_vec] == -1) \
                        or np.any(prob_board[anchor_row: anchor_row + ship_len, anchor_vec] == 1):
                            continue
                        else:
                            prob_board[anchor_row: anchor_row + ship_len, anchor_vec] = 1
                            #print(prob_board)
                            num_ships -= 1
                            #break
                    else:
                        if anchor_row == None or anchor_vec == None:
                            anchor_row = random.randint(0, LEN - 1)
                            anchor_vec = random.randint(0, LEN - 1 - ship_len + 1)
                        else:
                            anchor_vec = random.randint(max(0, anchor_vec - ship_len + 1), anchor_vec)
                        if np.any(game_board[anchor_row, anchor_vec: anchor_vec + ship_len] == -1) \
                        or np.any(prob_board[anchor_row, anchor_vec: anchor_vec + ship_len] == 1):
                            continue
                        else:
                            prob_board[anchor_row, anchor_vec: anchor_vec + ship_len] = 1
                            num_ships -= 1
                            #break
                #tmp = input('hit enter')
                if num_ships == 0 and len(temp_hits) == 0:
                    #print('return prob_board')
                    return prob_board
                else:
                    #num_ships = len(ships)
                    prob_board = np.zeros((LEN, LEN), dtype=int)
