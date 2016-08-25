

import random
import copy
import itertools as it
import numpy as np
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

#ROWS = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10}
#VECS = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J'}
ROWS = [str(i) for i in range(1, 11)]
VECS = 'abcdefghij'

XLIM = 10
YLIM = 10


class Ship(object):
    """
    simple class that holds a ships name, size, and an array of 1's that is the 'game piece'
    """
    def __init__(self, name, length):
        self._name = name
        self._size = length
        #self._ship = np.ones((length, ), dtype=int)

    @property
    def name(self):
        return self._name

    #@property
    #def ship(self):
    #    return self._ship

    @property
    def size(self):
        return self._size


class BattleShip(object):
    """
    class that will handle battleship ai.  will have information of where it
    has taken shots and will calculate probabilities of where ships are based on that
    also holds information of what enemy ships remain in play
    """
    def __init__(self):
        """
        initialize enemy pieces and enemy game board
        """
        carrier = Ship('carrier', 5)
        battleship = Ship('battleship', 4)
        submarine = Ship('submarine', 3)
        cruiser = Ship('cruiser', 3)
        destroyer = Ship('destroyer', 2)
        self.ships = [carrier, battleship, submarine, cruiser, destroyer]
        self.game_board = np.zeros((10, 10), dtype=int)
        self.freq_board = np.zeros((10, 10), dtype=int)
        self.hits = []
        self.move = None
        self.past_hits = []

    def get_move(self):
        while True:
            inp = input('Enter coordinates of move (separated by a space): ')
            inp = inp.strip().split()
            #print(inp)
            vec = None
            row = None
            for i in inp:
                if i in VECS:
                    #print('in vecs')
                    vec = i
                if i in ROWS:
                    #print('in rows')
                    row = i
            if vec is not None and row is not None:
                vec = VECS.index(vec)
                row = ROWS.index(row)
                #print(vec, row)
                if self.game_board[row, vec] == 0 and (row, vec) not in self.past_hits:
                    self.move = (row, vec)
                    return self
            else:
                print('invalid move... trying again...')


    def show_move(self):
        row = ROWS[self.move[0]]
        vec = VECS[self.move[1]]
        return '{}    {}'.format(row, vec)

    def mc_prob_distribution(self, ntrials):
        """
        will randomy place all present ships ntrials number of times on the game board
        using the mc_ship_placement() function
        these placements will be aggr
        once ntrials is reached, the probability board (member variable) will be updated
        to be
        """
        self.freq_board = np.zeros((10, 10), dtype=int)
        for _ in range(ntrials):
            self.freq_board += self.mc_ship_placement()
        if len(self.hits) > 0:
            for h in self.hits:
                row, vec = h
                self.freq_board[row, vec] = 0
        return self

    def find_best_move(self, method='deterministic', combination_size=2, mc_trials=2500, refine=False):
        """
        populate self.prob_distribution matrix and return the index of the maximum value
        """
        assert method in ['deterministic', 'monte carlo']
        self.freq_board = np.zeros((XLIM, YLIM), dtype=int)
        if method == 'deterministic':
            for pair in it.combinations(self.ships, min(combination_size, len(self.ships))):
                for i, b in enumerate(self.deterministic_ship_config(ships=pair)):
                    self.freq_board += b
            if len(self.past_hits) > 0:
                for h in self.past_hits:
                    row, vec = h
                    self.freq_board[row, vec] = 0
            i, j = np.unravel_index(self.freq_board.argmax(), self.freq_board.shape)
            self.freq_board = self.freq_board / self.freq_board[i, j]
        elif method == 'monte carlo':
            for _ in range(mc_trials):
                self.freq_board += self.mc_ship_placement()
            if len(self.past_hits) > 0:
                for h in self.past_hits:
                    row, vec = h
                    self.freq_board[row, vec] = 0
            i, j = np.unravel_index(self.freq_board.argmax(), self.freq_board.shape)
            self.freq_board = self.freq_board / self.freq_board[i, j]
        #if len(self.past_hits) > 0:
        #    for h in self.past_hits:
        #        row, vec = h
        #        self.freq_board[row, vec] = 0
        #if refine:
        #    self.refine_board()
        self.move = np.unravel_index(self.freq_board.argmax(), self.freq_board.shape)
        return self

    def refine_board(self):
        max_len = max([s.size for s in self.ships])
        max_len = 3
        new_freq_board = np.zeros((10, 10), dtype=float)
        for ix in range(10):
            for iy in range(10):
                new_freq_board[ix, iy] = self.freq_board[ix, iy]
                if new_freq_board[ix, iy] == 0:
                    continue
                if ix - max_len + 1 >= 0:
                    if np.all(self.freq_board[ix - max_len + 1: ix, iy] != 0):
                        #print(range(ix - max_len + 1, ix))
                        new_freq_board[ix, iy] += self.freq_board[ix - max_len + 1: ix - 1, iy].mean()
                if ix + max_len <= self.game_board.shape[0]:
                    if np.all(self.freq_board[ix: ix + max_len, iy] != 0):
                        #print(range(ix, ix + max_len))
                        new_freq_board[ix, iy] += self.freq_board[ix + 1: ix + max_len, iy].mean()
                if iy - max_len + 1 >= 0:
                    if np.all(self.freq_board[ix, iy - max_len: iy] != 0):
                        #print(range(iy - max_len + 1, iy))
                        new_freq_board[ix, iy] += self.freq_board[ix, iy - max_len + 1: iy - 1].mean()
                if iy + max_len <= self.game_board.shape[1]:
                    if np.all(self.freq_board[ix, iy: iy + max_len] != 0):
                        new_freq_board[ix, iy] += self.freq_board[ix, iy + 1: iy + max_len].mean()
        self.freq_board = new_freq_board
        return self

    def show_freq_board(self):
        """
        plot the prob_board
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        mask = np.zeros((10, 10), dtype=bool)
        for h in self.past_hits:
            mask[h[0], h[1]] = True
        sns.heatmap(self.freq_board, mask=mask, square=True, cmap='YlOrRd', linewidth=.025, annot=False, annot_kws={'size': 14},
                    xticklabels=[i for i in VECS], yticklabels=[i for i in ROWS])
        sns.plt.show()

    def shot_result(self):
        while True:
            hit = input('was last shot a hit (type "y" or "n")? ')
            if hit not in ['y', 'n']:
                print('inavlid response... trying again...')
            elif hit == 'y':
                hit = True
                sunk = False
                self.hits.append(self.move)
                self.past_hits.append(self.move)
                break
            else:
                hit = False
                sunk = False
                break
        if hit:
            if len(self.hits) >= min([s.size for s in self.ships]):
                while True:
                    sunk = input('was the ship sunk (type "y" or "n")? ')
                    if sunk not in ['y', 'n']:
                        print('inavlid response... trying again...')
                    elif sunk == 'y':
                        sunk = True
                        break
                    else:
                        sunk = False
                        break
        else:
            self.game_board[self.move] = -1
        if sunk:
            while True:
                size = input('how large was the ship ({})? '.format(', '.join([str(s.size) for s in self.ships])))
                size = int(size)
                if size not in [s.size for s in self.ships]:
                    print('inavlid response... trying again...')
                else:
                    break
            for grouping in it.combinations(self.hits, size):
                if self.move not in grouping:
                    continue
                if BattleShip.calc_distance(grouping, size):
                    for g in grouping:
                        if g in self.hits:
                            self.game_board[g[0], g[1]] = -1
                            self.hits.remove(g)
            new_ships = []
            num_ships_removed = 0
            for s in self.ships:
                if s.size != size:
                    new_ships.append(s)
                else:
                    if num_ships_removed == 0:
                        num_ships_removed += 1
                    else:
                        new_ships.append(s)
            self.ships = copy.deepcopy(new_ships)
        return self

    @staticmethod
    def calc_distance(grouping, distance):
        rows = [g[0] for g in grouping]
        vecs = [g[1] for g in grouping]
        row_dist = abs(max(rows) - min(rows))
        vec_dist = abs(max(vecs) - min(vecs))
        if max(row_dist, vec_dist) + 1 == distance and min(row_dist, vec_dist) == 0:
            return True
        else:
            return False

    def mc_ship_placement(self):
        """
        monte carlo method for randomly placing ships on game board such that they are not intersecting
        if hits exist, it will still randomly place game pieces, but will 'anchor' ships on known hits
        """
        placement_board = np.zeros((10, 10), dtype=int)
        while True:
            temp_hits = copy.deepcopy(self.hits)
            num_ships = len(self.ships)
            temp_ships = copy.deepcopy(self.ships)
            random.shuffle(temp_ships)
            for s in temp_ships:
                start_num = num_ships
                ship_len = s.size
                if len(temp_hits) > 0:
                    anchor_row, anchor_vec = random.choice(temp_hits)
                else:
                    anchor_row, anchor_vec = None, None
                direction = random.choice([0, 1])
                if direction == 0:
                    if anchor_row is None or anchor_vec is None:
                        anchor_row = random.randint(0, 9 - ship_len + 1)
                        anchor_vec = random.randint(0, 9)
                    else:
                        anchor_row = random.randint(max(0, anchor_row - ship_len + 1), anchor_row)
                    if np.any(self.game_board[anchor_row: anchor_row + ship_len, anchor_vec] == -1) \
                    or np.any(placement_board[anchor_row: anchor_row + ship_len, anchor_vec] == 1):
                        continue
                    else:
                        placement_board[anchor_row: anchor_row + ship_len, anchor_vec] = 1
                        indices = list(zip(range(anchor_row, anchor_row + ship_len + 1), it.repeat(anchor_vec)))
                        temp_hits = [i for i in temp_hits if i not in indices]
                        num_ships -= 1
                else:
                    if anchor_row is None or anchor_vec is None:
                        anchor_row = random.randint(0, 9)
                        anchor_vec = random.randint(0, 9 - ship_len + 1)
                    else:
                        anchor_vec = random.randint(max(0, anchor_vec - ship_len + 1), anchor_vec)
                    if np.any(self.game_board[anchor_row, anchor_vec: anchor_vec + ship_len] == -1) \
                    or np.any(placement_board[anchor_row, anchor_vec: anchor_vec + ship_len] == 1):
                        continue
                    else:
                        placement_board[anchor_row, anchor_vec: anchor_vec + ship_len] = 1
                        indices = list(zip(it.repeat(anchor_row), range(anchor_vec, anchor_vec + ship_len + 1)))
                        temp_hits = [i for i in temp_hits if i not in indices]
                        num_ships -= 1
                if num_ships == start_num:
                    break
            if num_ships == 0 and len(temp_hits) == 0:
                return placement_board
            else:
                placement_board = np.zeros((10, 10), dtype=int)

    def deterministic_ship_config(self, hits=None, ships=None, board=np.zeros((XLIM, YLIM), dtype=int)):
        if ships is None:
            ships = self.ships
        if hits is None:
            hits = copy.deepcopy(self.hits)
        if len(ships) == 0:
            to_yield = True
            for hit in self.hits:
                if board[hit[0], hit[1]] != 1:
                    to_yield = False
                    break
            if to_yield:
                yield board
        else:
            ship = ships[0]
            if len(hits) > 0:
                #print('no empty hits for ', ship.size)
                for hit in hits:
                    if board[hit[0], hit[1]] != 1:
                        min_x = max(0, hit[0] - ship.size + 1)
                        for ix in range(min_x, hit[0] + 1):
                            if np.count_nonzero(board[ix: ix + ship.size, hit[1]]) == 0 \
                            and np.count_nonzero(self.game_board[ix: ix + ship.size, hit[1]]) == 0 \
                            and ix + ship.size <= self.game_board.shape[0]:
                                board[ix: ix + ship.size, hit[1]] = 1
                                x_range = range(ix, ix + ship.size)
                                y_range = hit[1]
                                temp_hits = list(zip(x_range, it.repeat(y_range)))
                                temp_hits = [x for x in hits if x not in temp_hits]
                                yield from self.deterministic_ship_config(hits=temp_hits, ships=ships[1:], board=board)
                                board[ix: ix + ship.size, hit[1]] = 0
                        min_y = max(0, hit[1] - ship.size + 1)
                        for iy in range(min_y, hit[1] + 1):
                            if np.count_nonzero(board[hit[0], iy: iy + ship.size]) == 0 \
                            and np.count_nonzero(self.game_board[hit[0], iy: iy + ship.size]) == 0 \
                            and iy + ship.size <= self.game_board.shape[1]:
                                board[hit[0], iy: iy + ship.size] = 1
                                x_range = hit[0]
                                y_range = range(iy, iy + ship.size)
                                temp_hits = list(zip(it.repeat(x_range), y_range))
                                temp_hits = [x for x in hits if x not in temp_hits]
                                yield from self.deterministic_ship_config(hits=temp_hits, ships=ships[1:], board=board)
                                board[hit[0], iy: iy + ship.size] = 0
            max_idx = board.shape[0] - ship.size + 1
            for ix in range(max_idx):
                for iy in range(board.shape[1]):
                    if np.count_nonzero(board[ix: ix + ship.size, iy]) == 0 \
                    and np.count_nonzero(self.game_board[ix: ix + ship.size, iy]) == 0:
                        board[ix: ix + ship.size, iy] = 1
                        yield from self.deterministic_ship_config(hits=hits, ships=ships[1:], board=board)
                        board[ix: ix + ship.size, iy] = 0
            for ix in range(board.shape[0]):
                for iy in range(max_idx):
                    if np.count_nonzero(board[ix, iy: iy + ship.size]) == 0 \
                    and np.count_nonzero(self.game_board[ix, iy: iy + ship.size]) == 0:
                        board[ix, iy: iy + ship.size] = 1
                        yield from self.deterministic_ship_config(hits=hits, ships=ships[1:], board=board)
                        board[ix, iy: iy + ship.size] = 0

    def deterministic_ship_config_orig(self, ships=None, board=np.zeros((XLIM, YLIM), dtype=int)):
        if ships is None:
            ships = self.ships
        if len(ships) == 0:
            yield board
        else:
            empty_hits = False
            for hit in self.hits:
                if board[hit[0], hit[1]] != 1:
                    empty_hits = True
            ship = ships[0]
            #print(ship.size)
            if empty_hits:
                #print('empty hits exist for ', ship.size)
                for hit in self.hits:
                    if board[hit[0], hit[1]] != 1:
                        min_x = max(0, hit[0] - ship.size + 1)
                        for ix in range(min_x, hit[0] + 1):
                            if np.count_nonzero(board[ix: ix + ship.size, hit[1]]) == 0 \
                            and np.count_nonzero(self.game_board[ix: ix + ship.size, hit[1]]) == 0 \
                            and ix + ship.size <= self.game_board.shape[0]:
                                board[ix: ix + ship.size, hit[1]] = 1
                                yield from self.deterministic_ship_config(ships=ships[1:], board=board)
                                board[ix: ix + ship.size, hit[1]] = 0
                        min_y = max(0, hit[1] - ship.size + 1)
                        for iy in range(min_y, hit[1] + 1):
                            if np.count_nonzero(board[hit[0], iy: iy + ship.size]) == 0 \
                            and np.count_nonzero(self.game_board[hit[0], iy: iy + ship.size]) == 0 \
                            and iy + ship.size <= self.game_board.shape[1]:
                                board[hit[0], iy: iy + ship.size] = 1
                                yield from self.deterministic_ship_config(ships[1:], board)
                                board[hit[0], iy: iy + ship.size] = 0
            else:
                max_idx = board.shape[0] - ship.size + 1
                for ix in range(max_idx):
                    for iy in range(board.shape[1]):
                        if np.count_nonzero(board[ix: ix + ship.size, iy]) == 0 \
                        and np.count_nonzero(self.game_board[ix: ix + ship.size, iy]) == 0:
                            board[ix: ix + ship.size, iy] = 1
                            yield from self.deterministic_ship_config(ships=ships[1:], board=board)
                            board[ix: ix + ship.size, iy] = 0
                for ix in range(board.shape[0]):
                    for iy in range(max_idx):
                        if np.count_nonzero(board[ix, iy: iy + ship.size]) == 0 \
                        and np.count_nonzero(self.game_board[ix, iy: iy + ship.size]) == 0:
                            board[ix, iy: iy + ship.size] = 1
                            yield from self.deterministic_ship_config(ships=ships[1:], board=board)
                            board[ix, iy: iy + ship.size] = 0
