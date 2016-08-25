    def mc_ship_placement2(self):
        """
        monte carlo method for randomly placing ships on game board such that they are not intersecting
        if hits exist, it will still randomly place game pieces, but will 'anchor' ships on known hits
        """
        placement_board = np.zeros((10, 10), dtype=int)
        if len(self.hits) == 0:
            random.shuffle(self.ships)
            for s in self.ships:
                ship_len = s.size
                while True:
                    direction = random.choice([0, 1])
                    if direction == 0:
                        anchor_vec = random.randint(0, 9)
                        anchor_row = random.randint(0, 9 - ship_len + 1)
                        if np.any(self.game_board[anchor_row: anchor_row + ship_len, anchor_vec] == -1) \
                        or np.any(placement_board[anchor_row: anchor_row + ship_len, anchor_vec] == 1):
                            continue
                        else:
                            placement_board[anchor_row: anchor_row + ship_len, anchor_vec] = 1
                            break
                    else:
                        anchor_row = random.randint(0, 9)
                        anchor_vec = random.randint(0, 9 - ship_len + 1)
                        if np.any(self.game_board[anchor_row, anchor_vec: anchor_vec + ship_len] == -1) \
                        or np.any(placement_board[anchor_row, anchor_vec: anchor_vec + ship_len] == 1):
                            continue
                        else:
                            placement_board[anchor_row, anchor_vec: anchor_vec + ship_len] = 1
                            break
            return placement_board
        else:
            while True:
                temp_hits = copy.deepcopy(self.hits)
                num_ships = len(self.ships)
                random.shuffle(self.ships)
                for s in self.ships:
                    ship_len = s.size
                    if len(temp_hits) > 0:
                        anchor_row, anchor_vec = random.choice(temp_hits)
                        #temp_hits.remove((anchor_row, anchor_vec))
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
                if num_ships == 0 and len(temp_hits) == 0:
                    return placement_board
                else:
                    placement_board = np.zeros((10, 10), dtype=int)
