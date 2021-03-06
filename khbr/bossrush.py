import time

supported_games = ["kh2"]

class bossrush:
    def __init__(self, game, options, seed=None):
        if game not in supported_games:
            raise Exception("Game not supported")
        self.game = game
        self.options = options
        if not seed:
            self.seed = int(time.time())