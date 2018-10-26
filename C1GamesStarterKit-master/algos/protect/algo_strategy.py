import gamelib
import random
import math
import warnings
from sys import maxsize

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

Additional functions are made available by importing the AdvancedGameState 
class from gamelib/advanced.py as a replcement for the regular GameState class 
in game.py.

You can analyze action frames by modifying algocore.py.

The GameState.map object can be manually manipulated to create hypothetical 
board states. Though, we recommended making a copy of the map to preserve 
the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]


    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        if game_state.turn_number == 0:
            self.starter_strategy(game_state)
        else:
            self.subsequent_strategy(game_state)

        game_state.submit_turn()

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safey be replaced for your custom algo.
    """
    def starter_strategy(self, game_state):
        """
        Then build defenses.
        """
        self.build_starter_defences(game_state)

        """
        Finally deploy our information units to attack.
        """
        self.deploy_starter_attackers(game_state)

    def subsequent_strategy(self, game_state):
        """
        Then build defenses.
        """
        self.build_defences(game_state)

        """
        Finally deploy our information units to attack.
        """
        self.deploy_attackers(game_state)

    def build_starter_defences(self, game_state):
        """
        First lets protect ourselves a little with destructors:
        """
        firewall_locations = [[4, 12], [23, 12], [9, 11], [18, 11]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)

        firewall_locations = [[0, 13], [27, 13], [10, 11], [11, 11], [12, 11], [13, 11], [14, 11], [15, 11], [16, 11], [17, 11]]
        for location in firewall_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)

        """
        Then lets boost our offense by building some encryptors to shield 
        our information units. Lets put them near the front because the 
        shields decay over time, so shields closer to the action 
        are more effective.
        """
        firewall_locations = [[26, 12], [21, 12], [25, 11], [24, 13]]
        for location in firewall_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)

    def deploy_starter_attackers(self, game_state):
        """
        First lets check if we have 10 bits, if we don't we lets wait for 
        a turn where we do.
        """
        if (game_state.get_resource(game_state.BITS) < 10):
            return
        
        """
        First lets deploy an EMP long range unit to destroy firewalls for us.
        """
        if game_state.can_spawn(EMP, [3, 10]):
            game_state.attempt_spawn(EMP, [3, 10])

        """
        Now lets send out 3 Pings to hopefully score, we can spawn multiple 
        information units in the same location.
        """
        if game_state.can_spawn(PING, [14, 0], 3):
            game_state.attempt_spawn(PING, [14,0], 3)


    def build_defences(self, game_state):
        """
        First lets protect ourselves a little with destructors:
        """
        firewall_locations = [[4, 12], [23, 12], [9, 11], [18, 11]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)

        firewall_locations = [[0, 13], [27, 13], [10, 11], [11, 11], [12, 11], [13, 11], [14, 11], [15, 11], [16, 11], [17, 11], 
        [1, 13], [2, 13], [3, 13]]
        for location in firewall_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)

        """
        Then lets boost our offense by building some encryptors to shield 
        our information units. Lets put them near the front because the 
        shields decay over time, so shields closer to the action 
        are more effective.
        """
        firewall_locations = [[23,11], [26, 12], [21, 12], [25, 11], [24, 13]]
        for location in firewall_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)

        firewall_locations = [[5, 11], [6, 11], [7, 11], [8, 11], [9,11], [10,11], [11,11],
        [16,11], [17,11], [18,11], [19,11], [20,11]]
        for location in firewall_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)

        firewall_locations = [[26, 13], [12, 10], [15, 10]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
        
        firewall_locations = [[1,12], [2,12], [3, 12]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)

        firewall_locations = [[13, 1], [14, 2], [15, 3], [16, 4], [17, 5], [18, 6], [19, 7], [20, 8], [21, 9], [22, 10]]
        for location in firewall_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)

        firewall_locations = [[5, 13], [7, 13], [9, 13], [11, 13], [13, 13], [15, 13], [17, 13], [19, 13], [21, 13]]
        for location in firewall_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)

        firewall_locations = [[6, 12], [8, 12], [10, 12], [12, 12], [14, 12], [16, 12], [18, 12], [20, 12]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)

        firewall_locations = [[3, 11], [4, 11], [7, 9], [19, 9]]
        for location in firewall_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)




    def deploy_attackers(self, game_state):
        
        """
        First lets deploy an EMP long range unit to destroy firewalls for us.
        """
        if game_state.turn_number > 35:
            if game_state.can_spawn(EMP, [4, 9], 7):
                game_state.attempt_spawn(EMP, [4, 9], 7)
                game_state.attempt_spawn(SCRAMBLER, [19, 5], 2)
            else:
                game_state.attempt_spawn(SCRAMBLER, [4,9])
        elif game_state.turn_number > 15:
            if game_state.turn_number % 10 == 0:
                if game_state.can_spawn(EMP, [4, 9], 4):
                    game_state.attempt_spawn(EMP, [4, 9], 4)
                    game_state.attempt_spawn(SCRAMBLER, [4, 9], 1)
            elif game_state.turn_number % 3 == 0:
                if game_state.can_spawn(SCRAMBLER, [14, 0], 1):
                    game_state.attempt_spawn(SCRAMBLER, [14, 0], 1)
            if game_state.can_spawn(PING, [13, 0], ):
                game_state.attempt_spawn(PING, [13, 0], 15)
            else:
                game_state.attempt_spawn(SCRAMBLER, [13,0])
        else:
            if game_state.turn_number % 4 == 0:
                pass
            elif game_state.turn_number % 4 == 1:
                if game_state.can_spawn(EMP, [13, 0], 2):
                    game_state.attempt_spawn(EMP, [13, 0], 2)
                    game_state.attempt_spawn(SCRAMBLER, [4, 9], 1)
            elif game_state.turn_number % 4 == 2:
                if game_state.can_spawn(EMP, [4, 9], 2):
                    game_state.attempt_spawn(EMP, [4, 9], 2)
                    game_state.attempt_spawn(SCRAMBLER, [4, 9], 1)
            elif game_state.turn_number % 4 == 3:
                if game_state.can_spawn(EMP, [25, 11], 2):
                    game_state.attempt_spawn(EMP, [25, 11], 2)

            """
            Now lets send out 3 Pings to hopefully score, we can spawn multiple 
            information units in the same location.
            """
            while game_state.can_spawn(PING, [13, 0], 1):
                game_state.attempt_spawn(PING, [13,0], 1)
       
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
