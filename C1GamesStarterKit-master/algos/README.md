Idea
==

## Reward calculation

> utility = current_reward + \gamma * winning_chances

>> current_reward = \Delta(my_health) - \Delta(enemy_health)

or

>> current_reward = (d(my_health) + d(my_stationary_units_stability)) - (d(enemy_health) + d(enemy_stationary_units_stability))

`winning_chances` can be calculated either in a simple but inaccurate way, or in the traditional DQL method:
1. **Simple method**: 
>> winning_chances = $my\_health_{t}$ - $enemy_health_t$

or 
>> winning_chances = (my_health + my_cores_on_board) - (enemy_health - enemy_cores_on_board)
2. **DQL method**: 
Based on a lot of matches, learn what states lead to a win and what states lead to a loss.

## Memory

The idea is to be able to store all the experiences in one place not having to play the whole games again and again for retraining

According to [this link](https://keon.io/deep-q-learning/), I should be storing the following in memory:
    memory = [(state, action, reward, next_state, done), ...]

Using a `remember` function to save this set after playing it each time, and using a `replay` method to retrain on the remember function

## Model weights

Inside the folder for each algorithm, there is a folder called `model_vars` which contains three files:
1. model_parameters: For just storing or altering hyperparameters of the model
2. model_weights: For storing the current model weights
3. prev_game_state: To store the last state that the algorithm has observed.

These files are stored because the algorithm is called by the game engine only on its turn. 
Another problem is that the code *does not live to see the outcome of the action it takes*. This means that we do not even know the
next state after an action is taken. Note that the next state is highly dependent on the opponent's strategy as well.\
Hence the learning (i.e. updating of the model weights) will occur for the previous time step at the beginning of every turn of the player.

The following order is following in the lifecycle of the player's turn:
1. Load saved weights and parameters
2. Load previous state
3. Calculate `utility` (after calculating `reward`) for *(s<sub>t-1</sub>, a, s<sub>t</sub>)*, where *s<sub>t-1</sub>* is the previous game state, based on which the action *a* was taken
4. Update the weights 
5. Calculate the next action (part of the `play` function in the `framework.py` files)
6. Save the current game state and updated weights
7. Submit the moves 