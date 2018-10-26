import sys
import numpy as np
import pandas as pd

class Model():

    '''
    Attributes:
        weights_initialized: Flag to check if weights have been loaded
        weights: the set of learnt parameters

    '''
    def __init__(self):
        self.weights = dict()
        self.weights_initialized = False

    def set_weights(self, model_weights):
        self.weights_initialized = True
        self.weights = model_weights

    def get_weights(self):
        return self.weights

    '''
        purpose value-dictionary:
            0   :   Default (does not remove any columns)
            1   :   Firewall learning (preserves stability, damage, {range})
            2   :   Information learning (preserves stability, max_stability, {range, damage, heal})
    '''
    def extract_features(self, current_game_state, purpose = 0):
        features = current_game_state['game_map']
        if purpose == 1:
            features = [ [stability, damage] for team, max_stability, stability, urange, damage, heal in features]
        elif purpose == 2:
            features = [ [stability, max_stability] for team, max_stability, stability, urange, damage, heal in features]
        elif purpose == 0:
            pass
        else:
            sys.stderr.write("[model] [extract_features] WARNING: Unsupported value for 'purpose'. Please choose between 0, 1 and 2.\n")
        features = np.array(features).flatten()
        features = np.append(
            np.array([current_game_state['bits'], current_game_state['cores'], current_game_state['my_health'], current_game_state['enemy_health']]), 
            features
        )
        return features

    def get_firewall_strategy(self, current_game_state, friendly_locations):
        features = self.extract_features(current_game_state, purpose=1)
        # print(features.shape)
        if not self.weights_initialized:
            '''
                Adding 1 as bias (to not force decisions if it wants to assign low importance to all locations)
            '''
            self.weights['firewall'] = {
                'FF': np.random.uniform(size=(len(features), 1 + len(friendly_locations))),
                'EF': np.random.uniform(size=(len(features), 1 + len(friendly_locations))),
                'DF': np.random.uniform(size=(len(features), 1 + len(friendly_locations)))
            }

        firewall_prob_df = {}
        for key in self.weights['firewall'].keys():
            firewall_prob_df[key] = np.dot(features, self.weights['firewall'][key])
        firewall_prob_df = self.normalize(pd.DataFrame(firewall_prob_df))
        '''
            Note that by min-max normalizing the dataframe, we are forcing the algorithm to 
            move at least something as long as it has cores left (even if it thinks that not moving
            anything is the best strategy and wants to save cores for future). 
            We should allow the algorithm to not move if it does not want to.
            TODO: Find a formula to apply appropriate threshold without forcing implicit decisions
                Done: note the comment in initialization conditional block earlier in this function
        '''
        return firewall_prob_df

    def get_information_strategy(self, current_game_state, friendly_locations):
        features = self.extract_features(current_game_state, purpose=2)
        if not self.weights_initialized:
            '''
                Adding 1 as bias (to not force decisions if it wants to assign low importance to all locations)
            '''
            self.weights['information'] = {
                'PI': np.random.uniform(size=(len(features), 1 + len(friendly_locations))),
                'EI': np.random.uniform(size=(len(features), 1 + len(friendly_locations))),
                'SI': np.random.uniform(size=(len(features), 1 + len(friendly_locations)))
            }
        information_prob_df = {}
        for key in self.weights['information'].keys():
            information_prob_df[key] = np.dot(features, self.weights['information'][key])
        information_prob_df = pd.DataFrame(information_prob_df)
        information_prob_df = self.normalize(information_prob_df)
        return information_prob_df

    def normalize(self, df):
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        new_df = df.select_dtypes(include=numerics)
        df_matrix = []
        for i in new_df.columns:
            df_matrix.append(np.array(new_df[i]))
        df_matrix = np.array(df_matrix)
        # print("MIN: ", np.unravel_index(np.argmin(df_matrix, axis=None), df_matrix.shape), df_matrix.min())
        # print("MAX: ", np.unravel_index(np.argmax(df_matrix, axis=None), df_matrix.shape), df_matrix.max())
        df_matrix = (df_matrix - df_matrix.min()) / (df_matrix.max() + 1 - df_matrix.min()) # denominator is never zero
        for i in range(0, len(new_df.columns)):
            df[new_df.columns[i]] = df_matrix[i]

        return df

        # norm = np.linalg.norm(self.weights) # We want to add this to the optimization formula


if __name__ == '__main__':
    md = Model()