import os
import sys
import gamelib
import random
import json
import math

import model

try:
    import pip
except:
    os.system("apt-get install pip")
    os.system("easy_install pip")

def install(package):
    # sys.stderr.write("Installing package:" + package)
    # if hasattr(pip, 'main'):
    #     pip.main(['install', package])
    # else:
    #     pip._internal.main(['install', package])
    os.system("pip install " + package)
    os.system("sudo pip install " + package)

try:
    import numpy as np
except:
    install('numpy')
    import numpy as np

try:
    import pandas as pd
except:
    install('pandas')
    import pandas as pd


class FrameWork():

    """
    Attributes:
        strategy: return object to algo_strategy file based on which action will be taken
        game_state: game state variable as provided by algo_strategy file
        features: contains the game-map features to be given to training model
        features_df: DataFrame form of features
        current_game_state: game_state in the current run
        model_parameters: hyper-parameters of the model
        model_parameters_file: file which stores model_parameters
        model_weights: learned parameters of the model
        model_weights_file: file which stores model_weights
        prev_game_state: game_state in the last turn
        prev_game_state_file: file which stores prev_game_state

        information_locations: all information units' spawn locations
        firewall_locations: all firewall locations

    """

    def __init__(self, game_state):
        
        self.strategy = {}

        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = game_state.config["unitInformation"][0]
        ENCRYPTOR = game_state.config["unitInformation"][1]
        DESTRUCTOR = game_state.config["unitInformation"][2]
        PING = game_state.config["unitInformation"][3]
        EMP = game_state.config["unitInformation"][4]
        SCRAMBLER = game_state.config["unitInformation"][5]
        
        # Just storing the game-state for future reference
        self.game_state = game_state
        self.features = self.game_state_to_vector(self.game_state)
        self.features_df = pd.DataFrame(np.array(self.features), columns=['team', 'max_stability', 'stability', 'range', 'damage', 'heal'])
        self.current_game_state = self.create_storage_game_state(self.game_state)
        # print(self.features_df[features_df.heal != 0])

        self.load_model_vars()

        self.modelObj = model.Model()
        if self.model_weights:
            self.modelObj.set_weights(self.model_weights)

    def load_model_vars(self):
        model_vars_folder = os.path.dirname(os.path.abspath(__file__))+"/model_vars/"
        self.model_parameters_file = model_vars_folder + "model_parameters.txt"
        self.model_weights_file = model_vars_folder + "model_weights.txt"
        self.prev_game_state_file = model_vars_folder + "prev_game_state.txt"

        try:
            with open(self.model_parameters_file, 'r') as f:
                self.model_parameters = json.loads(f.read())
        except FileNotFoundError:
            self.model_parameters = self.initialize_model_parameters()

        try:
            with open(self.model_weights_file, 'r') as f:
                self.model_weights = json.loads(f.read())
                for phase in self.model_weights:
                    for unit in self.model_weights[phase]:
                        self.model_weights[phase][unit] = np.array(self.model_weights[phase][unit])
        except FileNotFoundError:
            self.model_weights = self.initialize_model_weights()

        try:
            with open(self.prev_game_state_file, 'r') as f:
                self.prev_game_state = f.read()
                self.prev_game_state = json.loads(self.prev_game_state)
        except FileNotFoundError:
            self.prev_game_state = self.initialize_prev_game_state()

    def save_state(self):
        with open(self.model_parameters_file, 'w+') as f:
            f.write(json.dumps(self.model_parameters))
        with open(self.model_weights_file, 'w+') as f:
            self.model_weights = self.modelObj.weights
            for phase in self.modelObj.weights:
                for unit in self.modelObj.weights[phase]:
                    self.modelObj.weights[phase][unit] = self.modelObj.weights[phase][unit].tolist()
            f.write(json.dumps(self.model_weights))
        with open(self.prev_game_state_file, 'w+') as f:
            f.write(json.dumps(self.current_game_state))

    def initialize_model_parameters(self):
        '''
            gamma: discount factor for the reward function
        '''
        value = {
            'gamma': 0.7,
            'ff_threshold': 0.5,
            'ef_threshold': 0.5,
            'df_threshold': 0.5,
            'pi_log_base': 2.0,
            'ei_log_base': 2.0,
            'si_log_base': 2.0
        }
        return value

    def initialize_model_weights(self):
        return None

    def initialize_prev_game_state(self):
        all_locations = []
        features = []
        for i in range(self.game_state.ARENA_SIZE):
            for j in range(math.floor(self.game_state.ARENA_SIZE)):
                if (self.game_state.game_map.in_arena_bounds([i, j])):
                    all_locations.append([i, j])
        
        for location in all_locations:
            features.append([0 if location[1] < 14 else 1, 0, 0, 0, 0, 0])
        return features

    def game_state_to_vector(self, game_state):
        features = []
        
        # arena_size = game_state.game_map.ARENA_SIZE
        df1 = pd.DataFrame(game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT), columns=['l_x', 'y'])
        df2 = pd.DataFrame(game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT), columns=['r_x', 'y'])
        friend_df = pd.merge(df1, df2, on='y')
        df1 = pd.DataFrame(game_state.game_map.get_edge_locations(game_state.game_map.TOP_LEFT), columns=['l_x', 'y'])
        df2 = pd.DataFrame(game_state.game_map.get_edge_locations(game_state.game_map.TOP_RIGHT), columns=['r_x', 'y'])
        enemy_df = pd.merge(df1, df2, on='y')
        arena_bounds_df = pd.concat([friend_df, enemy_df.sort_values('y')], axis=0, ignore_index=True)
        
        arena_array = []
        for y in np.array(arena_bounds_df):
            arena_array += [[x, y[1]] for x in range(y[0], 1+y[2])]

        # arena_df = pd.DataFrame(np.array(arena_array), columns=['x', 'y'])
        # print(arena_df)
        # arena_df['item'] = arena_df.apply(game_state.game_map.__getitem__)

        for location in arena_array:
            item = game_state.game_map.__getitem__(location)
            if len(item) > 0:
                for i in item:
                    if i.stationary:
                        features.append([i.player_index, i.max_stability, i.stability, i.range, i.damage if i.unit_type != 'EF' else 0, i.damage if i.unit_type == 'EF' else 0])
                    else:
                        sys.stderr.write("[model] [game_state_to_vector] Found item which is not stationary")
            elif item == []:
                features.append([0 if location[1] < 14 else 1, 0, 0, 0, 0, 0])
            else:
                sys.stderr.write("[model] [game_state_to_vector] Unknown object encountered")
        return features

    def create_storage_game_state(self, game_state):
        storage_game_state = {
            'bits': game_state.BITS,
            'cores': game_state.CORES,
            'turn_number': game_state.turn_number,
            'my_health': game_state.my_health,
            'my_time': game_state.my_time,
            'enemy_health': game_state.enemy_health,
            'enemy_time': game_state.enemy_time,
            'game_map': self.game_state_to_vector(game_state)
        }
        return storage_game_state

    '''
        The current definition of the utility function is very basic.
        The simplicity is supposed to reduce the computational complexity of the problem

        TODO: Ideally, we would like to learn the utility from the (s, a, s') set (from a training
        set)
    '''
    def calculate_utility(self, prev_game_state, current_game_state):
        delta_my_health = current_game_state.my_health - prev_game_state.my_health
        delta_enemy_health = current_game_state.enemy_health - prev_game_state.enemy_health
        reward = delta_my_health - delta_enemy_health

        future_promise = current_game_state.my_health - current_game_state.enemy_health

        return (reward + (self.model_parameters['gamma'] * future_promise))

    def get_firewall_strategy(self):
        df1 = pd.DataFrame(self.game_state.game_map.get_edge_locations(self.game_state.game_map.BOTTOM_LEFT), columns=['l_x', 'y'])
        df2 = pd.DataFrame(self.game_state.game_map.get_edge_locations(self.game_state.game_map.BOTTOM_RIGHT), columns=['r_x', 'y'])
        friend_df = pd.merge(df1, df2, on='y')

        friendly_locations = []
        for y in np.array(friend_df):
            friendly_locations += [[x, y[1]] for x in range(y[0], 1+y[2])]

        firewall_df = self.decide_firewall(friendly_locations)
        self.firewall_locations = firewall_df.T.to_dict().values()

        return self.firewall_locations

    def get_information_strategy(self):
        # information_df = pd.DataFrame(0, index=np.arange(self.game_state.ARENA_SIZE), columns=['PI', 'EI', 'SI'])
        friendly_edges = self.game_state.game_map.get_edge_locations(self.game_state.game_map.BOTTOM_LEFT) + self.game_state.game_map.get_edge_locations(self.game_state.game_map.BOTTOM_RIGHT)

        information_df = self.decide_information(friendly_edges)
        information_df['intensity'] = np.floor(-np.log2( 1 - information_df['intensity'])) # This assumes: intensity \in [0,1)
        information_df['intensity'] = information_df['intensity'].astype(int)
        information_df = information_df[information_df['intensity'] > 0]
        
        self.information_locations = information_df.T.to_dict().values()

        return self.information_locations

    def decide_firewall(self, friendly_locations):
        firewall_df = self.modelObj.get_firewall_strategy(self.current_game_state, friendly_locations)
        firewall_df['location'] = firewall_df.index
        firewall_df = pd.melt(firewall_df, id_vars=['location'], value_vars=['FF', 'EF', 'DF'], var_name="type", value_name="importance")
        firewall_df = firewall_df.sort_values(by=['importance'], ascending=False)
        firewall_df['location'] = firewall_df['location'].apply(lambda i: friendly_locations[i] if i < len(friendly_locations) else np.nan)
        firewall_df.dropna(inplace=True) # To drop the rows corresponding to biases
        return firewall_df

    def decide_information(self, friendly_locations):
        # information_df = pd.DataFrame(0, index=np.arange(len(friendly_locations)), columns=['PI', 'EI', 'SI'])
        information_df = self.modelObj.get_information_strategy(self.current_game_state, friendly_locations)
        information_df['location'] = information_df.index
        information_df = pd.melt(information_df, id_vars=['location'], value_vars=['EI', 'PI', 'SI'], var_name="type", value_name="intensity")
        information_df = information_df.sort_values(by=['intensity'], ascending=False)
        information_df['location'] = information_df['location'].apply(lambda i: friendly_locations[i] if i < len(friendly_locations) else np.nan)
        information_df.dropna(inplace=True) # To drop the rows corresponding to biases
        return information_df

    def play(self):
        # print("My health", game_state.my_health)
        # print(game_state.game_map[0,13])
        # print(game_state.game_map[0,14])
        # print(game_state.game_map[2,13])
        # print("Arena size", game_state.ARENA_SIZE)

        self.strategy['firewall'] = self.get_firewall_strategy()
        self.strategy['information'] = self.get_information_strategy()
        # print(self.strategy)

        self.save_state()
        return self.strategy

if __name__ == '__main__':
    turn_state = '{"p2Units": [[[27, 14, 60.0, "14"], [20, 15, 60.0, "18"], [12, 20, 60.0, "24"], [13, 15, 48.0, "208"], [0, 14, 33.0, "274"]], [[24, 16, 30.0, "50"], [23, 16, 30.0, "54"], [22, 16, 30.0, "74"], [17, 16, 30.0, "84"], [18, 17, 30.0, "108"], [14, 22, 30.0, "114"], [10, 23, 30.0, "118"], [4, 17, 22.0, "140"], [25, 15, 30.0, "148"], [17, 20, 30.0, "152"], [16, 16, 30.0, "180"], [9, 19, 30.0, "188"], [5, 17, 30.0, "212"], [15, 20, 30.0, "214"], [8, 18, 30.0, "222"], [10, 17, 30.0, "244"], [23, 14, 30.0, "250"], [8, 20, 30.0, "284"], [20, 19, 30.0, "306"], [17, 14, 30.0, "312"], [12, 18, 30.0, "334"], [12, 14, 30.0, "336"], [22, 18, 30.0, "344"]], [[26, 15, 75.0, "2"], [20, 16, 75.0, "6"], [13, 16, 72.0, "8"], [12, 21, 75.0, "12"], [1, 15, 3.0, "270"], [6, 16, 51.0, "272"]], [], [], [], []], "turnInfo": [0, 24, -1], "p1Stats": [1.0, 9.0, 7.0, 1], "p1Units": [[[0, 13, 60.0, "38"], [7, 12, 60.0, "42"], [14, 12, 42.0, "44"], [15, 7, 60.0, "48"], [27, 13, 9.0, "216"], [21, 12, 15.0, "340"]], [[3, 11, 30.0, "52"], [4, 11, 30.0, "56"], [5, 11, 30.0, "78"], [12, 8, 30.0, "82"], [9, 7, 30.0, "86"], [9, 8, 30.0, "112"], [6, 13, 30.0, "116"], [7, 9, 30.0, "120"], [16, 2, 30.0, "146"], [9, 13, 30.0, "150"], [12, 4, 30.0, "154"], [13, 3, 30.0, "190"], [14, 6, 30.0, "220"], [16, 6, 30.0, "246"], [14, 10, 30.0, "248"], [14, 4, 30.0, "252"], [15, 3, 30.0, "286"], [17, 3, 30.0, "314"], [8, 9, 30.0, "342"], [12, 7, 30.0, "346"]], [[1, 12, 75.0, "26"], [7, 11, 75.0, "30"], [14, 11, 75.0, "32"], [15, 6, 75.0, "36"], [26, 12, 41.0, "278"], [21, 11, 75.0, "338"]], [], [], [], []], "p2Stats": [2.0, 8.0, 7.0, 4], "events": {"selfDestruct": [], "breach": [], "damage": [], "shield": [], "move": [], "spawn": [], "death": [], "attack": [], "melee": []}}'
    config = {'debug': {'printMapString': False, 'printTStrings': False, 'printActStrings': False, 'printHitStrings': False, 'printPlayerInputStrings': True, 'printBotErrors': True, 'printPlayerGetHitStrings': False}, 'unitInformation': [{'damage': 0.0, 'cost': 1.0, 'getHitRadius': 0.51, 'display': 'Filter', 'range': 0.0, 'shorthand': 'FF', 'stability': 60.0}, {'damage': 0.0, 'cost': 4.0, 'getHitRadius': 0.51, 'shieldAmount': 10.0, 'display': 'Encryptor', 'range': 3.0, 'shorthand': 'EF', 'stability': 30.0}, {'damage': 4.0, 'cost': 3.0, 'getHitRadius': 0.51, 'display': 'Destructor', 'range': 3.0, 'shorthand': 'DF', 'stability': 75.0}, {'damageI': 1.0, 'damageToPlayer': 1.0, 'cost': 1.0, 'getHitRadius': 0.51, 'damageF': 1.0, 'display': 'Ping', 'range': 3.0, 'shorthand': 'PI', 'stability': 15.0, 'speed': 0.5}, {'damageI': 3.0, 'damageToPlayer': 1.0, 'cost': 3.0, 'getHitRadius': 0.51, 'damageF': 3.0, 'display': 'EMP', 'range': 5.0, 'shorthand': 'EI', 'stability': 5.0, 'speed': 0.25}, {'damageI': 10.0, 'damageToPlayer': 1.0, 'cost': 1.0, 'getHitRadius': 0.51, 'damageF': 0.0, 'display': 'Scrambler', 'range': 3.0, 'shorthand': 'SI', 'stability': 40.0, 'speed': 0.25}, {'display': 'Remove', 'shorthand': 'RM'}], 'timingAndReplay': {'waitTimeBotMax': 50000.0, 'playWaitTimeBotMax': 70000.0, 'waitTimeManual': 1820000.0, 'waitForever': False, 'waitTimeBotSoft': 20000.0, 'playWaitTimeBotSoft': 40000.0, 'replaySave': 1.0, 'playReplaySave': 0.0, 'storeBotTimes': True}, 'resources': {'turnIntervalForBitCapSchedule': 10.0, 'turnIntervalForBitSchedule': 10.0, 'bitRampBitCapGrowthRate': 5.0, 'roundStartBitRamp': 10.0, 'bitGrowthRate': 1.0, 'startingHP': 30.0, 'maxBits': 999999.0, 'bitsPerRound': 5.0, 'coresPerRound': 4.0, 'coresForPlayerDamage': 1.0, 'startingBits': 5.0, 'bitDecayPerRound': 0.33333, 'startingCores': 25.0}, 'mechanics': {'basePlayerHealthDamage': 1.0, 'damageGrowthBasedOnY': 0.0, 'bitsCanStackOnDeployment': True, 'destroyOwnUnitRefund': 0.5, 'destroyOwnUnitsEnabled': True, 'stepsRequiredSelfDestruct': 5.0, 'selfDestructRadius': 1.5, 'shieldDecayPerFrame': 0.15, 'meleeMultiplier': 0.0, 'destroyOwnUnitDelay': 1.0, 'rerouteMidRound': True, 'firewallBuildTime': 0.0}}
    game_state = gamelib.GameState(config, turn_state)

    fw = FrameWork(game_state)
    fw.play()