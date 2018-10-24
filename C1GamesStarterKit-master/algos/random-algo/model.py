import sys
import gamelib
import math

import random

class Model():

    """

    Attributes:
        features: contains the game-map features to be given to training model
    """

    def __init__(self):
        self.game_state = None
        self.features = []
        self.features_df = None
        self.strategy = {}

    def game_state_to_vector(self, game_state):
        # Just storing the game-state for future reference
        self.game_state = game_state
        
        # arena_size = game_state.game_map.ARENA_SIZE
        all_locations = []
        for i in range(game_state.ARENA_SIZE):
            for j in range(math.floor(game_state.ARENA_SIZE)):
                if (game_state.game_map.in_arena_bounds([i, j])):
                    all_locations.append([i, j])
        
        for location in all_locations:
            item = game_state.game_map.__getitem__(location)
            if len(item) > 0:
                for i in item:
                    if i.stationary:
                        self.features.append([i.player_index, i.max_stability, i.stability, i.range, i.damage if i.unit_type != 'EF' else 0, i.damage if i.unit_type == 'EF' else 0])
                    else:
                        sys.stderr.write("[model] [game_state_to_vector] Found item which is not stationary")
            elif item == []:
                self.features.append([0 if location[1] < 14 else 1, 0, 0, 0, 0, 0])
            else:
                sys.stderr.write("[model] [game_state_to_vector] Unknown object encountered")

        # self.features_df = pd.DataFrame(np.array(self.features), columns=['team', 'max_stability', 'stability', 'range', 'damage', 'heal'])
        # print(self.features_df[features_df.heal != 0])

    def get_firewall_strategy(self):
        friendly_locations = []
        for i in range(self.game_state.ARENA_SIZE):
            for j in range(math.floor(self.game_state.ARENA_SIZE / 2)):
                if (self.game_state.game_map.in_arena_bounds([i, j])):
                    friendly_locations.append([i, j])

        firewall_df = self.decide_firewall(friendly_locations)

        self.ff_locations = [friendly_locations[loc] for loc in range(0, len(firewall_df['FF'])) if firewall_df['FF'][loc]]
        self.ef_locations = [friendly_locations[loc] for loc in range(0, len(firewall_df['EF'])) if firewall_df['EF'][loc]]
        self.df_locations = [friendly_locations[loc] for loc in range(0, len(firewall_df['DF'])) if firewall_df['DF'][loc]]

        # print(self.ff_locations, self.ef_locations, self.df_locations)
        return {
            "FF": self.ff_locations,
            "EF": self.ef_locations,
            "DF": self.df_locations
        }

    def get_information_strategy(self):
        # information_df = pd.DataFrame(0, index=np.arange(self.game_state.ARENA_SIZE), columns=['PI', 'EI', 'SI'])
        friendly_edges = self.game_state.game_map.get_edge_locations(self.game_state.game_map.BOTTOM_LEFT) + self.game_state.game_map.get_edge_locations(self.game_state.game_map.BOTTOM_RIGHT)

        information_df = self.decide_information(friendly_edges)
        # print(information_df)

        self.pi_locations = [[friendly_edges[loc], information_df['PI'][loc]] for loc in range(0, len(information_df['PI'])) if information_df['PI'][loc]]
        self.ei_locations = [[friendly_edges[loc], information_df['EI'][loc]] for loc in range(0, len(information_df['EI'])) if information_df['EI'][loc]]
        self.si_locations = [[friendly_edges[loc], information_df['SI'][loc]] for loc in range(0, len(information_df['SI'])) if information_df['SI'][loc]]

        # print(self.pi_locations, self.ei_locations, self.si_locations)
        return { 
            "PI":self.pi_locations, 
            "EI": self.ei_locations, 
            "SI": self.si_locations 
        }

    def decide_firewall(self, friendly_locations):
        firewall_df = {
            'FF': [0] * len(friendly_locations),
            'EF': [0] * len(friendly_locations),
            'DF': [0] * len(friendly_locations)
        }
        firewall_df['FF'][random.randint(0, len(friendly_locations) - 1)] = random.randint(0, 1)
        firewall_df['EF'][random.randint(0, len(friendly_locations) - 1)] = random.randint(0, 1)
        firewall_df['DF'][random.randint(0, len(friendly_locations) - 1)] = random.randint(0, 1)
        return firewall_df

    def decide_information(self, friendly_locations):
        information_df = {
            'PI': [0] * len(friendly_locations),
            'EI': [0] * len(friendly_locations),
            'SI': [0] * len(friendly_locations)
        }
        information_df['PI'][random.randint(0, len(friendly_locations) - 1)] = random.randint(0, 3)
        information_df['EI'][random.randint(0, len(friendly_locations) - 1)] = random.randint(0, 1)
        information_df['SI'][random.randint(0, len(friendly_locations) - 1)] = random.randint(0, 3)
        return information_df

    def play(self, game_state):
        # print("My health", game_state.my_health)
        # print(game_state.game_map[0,13])
        # print(game_state.game_map[0,14])
        # print(game_state.game_map[2,13])
        # print("Arena size", game_state.ARENA_SIZE)

        self.game_state_to_vector(game_state)
        self.strategy['firewall'] = self.get_firewall_strategy()
        self.strategy['information'] = self.get_information_strategy()
        # print(self.strategy)
        return self.strategy

if __name__ == '__main__':
    md = Model()

    turn_state = '{"p2Units": [[[27, 14, 60.0, "14"], [20, 15, 60.0, "18"], [12, 20, 60.0, "24"], [13, 15, 48.0, "208"], [0, 14, 33.0, "274"]], [[24, 16, 30.0, "50"], [23, 16, 30.0, "54"], [22, 16, 30.0, "74"], [17, 16, 30.0, "84"], [18, 17, 30.0, "108"], [14, 22, 30.0, "114"], [10, 23, 30.0, "118"], [4, 17, 22.0, "140"], [25, 15, 30.0, "148"], [17, 20, 30.0, "152"], [16, 16, 30.0, "180"], [9, 19, 30.0, "188"], [5, 17, 30.0, "212"], [15, 20, 30.0, "214"], [8, 18, 30.0, "222"], [10, 17, 30.0, "244"], [23, 14, 30.0, "250"], [8, 20, 30.0, "284"], [20, 19, 30.0, "306"], [17, 14, 30.0, "312"], [12, 18, 30.0, "334"], [12, 14, 30.0, "336"], [22, 18, 30.0, "344"]], [[26, 15, 75.0, "2"], [20, 16, 75.0, "6"], [13, 16, 72.0, "8"], [12, 21, 75.0, "12"], [1, 15, 3.0, "270"], [6, 16, 51.0, "272"]], [], [], [], []], "turnInfo": [0, 24, -1], "p1Stats": [1.0, 9.0, 7.0, 1], "p1Units": [[[0, 13, 60.0, "38"], [7, 12, 60.0, "42"], [14, 12, 42.0, "44"], [15, 7, 60.0, "48"], [27, 13, 9.0, "216"], [21, 12, 15.0, "340"]], [[3, 11, 30.0, "52"], [4, 11, 30.0, "56"], [5, 11, 30.0, "78"], [12, 8, 30.0, "82"], [9, 7, 30.0, "86"], [9, 8, 30.0, "112"], [6, 13, 30.0, "116"], [7, 9, 30.0, "120"], [16, 2, 30.0, "146"], [9, 13, 30.0, "150"], [12, 4, 30.0, "154"], [13, 3, 30.0, "190"], [14, 6, 30.0, "220"], [16, 6, 30.0, "246"], [14, 10, 30.0, "248"], [14, 4, 30.0, "252"], [15, 3, 30.0, "286"], [17, 3, 30.0, "314"], [8, 9, 30.0, "342"], [12, 7, 30.0, "346"]], [[1, 12, 75.0, "26"], [7, 11, 75.0, "30"], [14, 11, 75.0, "32"], [15, 6, 75.0, "36"], [26, 12, 41.0, "278"], [21, 11, 75.0, "338"]], [], [], [], []], "p2Stats": [2.0, 8.0, 7.0, 4], "events": {"selfDestruct": [], "breach": [], "damage": [], "shield": [], "move": [], "spawn": [], "death": [], "attack": [], "melee": []}}'
    config = {'debug': {'printMapString': False, 'printTStrings': False, 'printActStrings': False, 'printHitStrings': False, 'printPlayerInputStrings': True, 'printBotErrors': True, 'printPlayerGetHitStrings': False}, 'unitInformation': [{'damage': 0.0, 'cost': 1.0, 'getHitRadius': 0.51, 'display': 'Filter', 'range': 0.0, 'shorthand': 'FF', 'stability': 60.0}, {'damage': 0.0, 'cost': 4.0, 'getHitRadius': 0.51, 'shieldAmount': 10.0, 'display': 'Encryptor', 'range': 3.0, 'shorthand': 'EF', 'stability': 30.0}, {'damage': 4.0, 'cost': 3.0, 'getHitRadius': 0.51, 'display': 'Destructor', 'range': 3.0, 'shorthand': 'DF', 'stability': 75.0}, {'damageI': 1.0, 'damageToPlayer': 1.0, 'cost': 1.0, 'getHitRadius': 0.51, 'damageF': 1.0, 'display': 'Ping', 'range': 3.0, 'shorthand': 'PI', 'stability': 15.0, 'speed': 0.5}, {'damageI': 3.0, 'damageToPlayer': 1.0, 'cost': 3.0, 'getHitRadius': 0.51, 'damageF': 3.0, 'display': 'EMP', 'range': 5.0, 'shorthand': 'EI', 'stability': 5.0, 'speed': 0.25}, {'damageI': 10.0, 'damageToPlayer': 1.0, 'cost': 1.0, 'getHitRadius': 0.51, 'damageF': 0.0, 'display': 'Scrambler', 'range': 3.0, 'shorthand': 'SI', 'stability': 40.0, 'speed': 0.25}, {'display': 'Remove', 'shorthand': 'RM'}], 'timingAndReplay': {'waitTimeBotMax': 50000.0, 'playWaitTimeBotMax': 70000.0, 'waitTimeManual': 1820000.0, 'waitForever': False, 'waitTimeBotSoft': 20000.0, 'playWaitTimeBotSoft': 40000.0, 'replaySave': 1.0, 'playReplaySave': 0.0, 'storeBotTimes': True}, 'resources': {'turnIntervalForBitCapSchedule': 10.0, 'turnIntervalForBitSchedule': 10.0, 'bitRampBitCapGrowthRate': 5.0, 'roundStartBitRamp': 10.0, 'bitGrowthRate': 1.0, 'startingHP': 30.0, 'maxBits': 999999.0, 'bitsPerRound': 5.0, 'coresPerRound': 4.0, 'coresForPlayerDamage': 1.0, 'startingBits': 5.0, 'bitDecayPerRound': 0.33333, 'startingCores': 25.0}, 'mechanics': {'basePlayerHealthDamage': 1.0, 'damageGrowthBasedOnY': 0.0, 'bitsCanStackOnDeployment': True, 'destroyOwnUnitRefund': 0.5, 'destroyOwnUnitsEnabled': True, 'stepsRequiredSelfDestruct': 5.0, 'selfDestructRadius': 1.5, 'shieldDecayPerFrame': 0.15, 'meleeMultiplier': 0.0, 'destroyOwnUnitDelay': 1.0, 'rerouteMidRound': True, 'firewallBuildTime': 0.0}}
    game_state = gamelib.GameState(config, turn_state)

    md.play(game_state)