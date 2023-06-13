# -*- coding: utf-8 -*-
"""Blackjack Env 1 Monte Carlo.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10YPGi86JCeozzEnQt_aw4Yy-M4gGdWtk

# Imports
"""

import gym
import math 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import copy
from collections import defaultdict
from itertools import filterfalse, islice

from BlackJackUtility import get_total, game_result, plot_value_function, plot_policy_blackjack, average_wins

"""# Method"""

# Using OpenAI gym blackjack environemnt
environment = gym.make('Blackjack-v1')
new_step_api = True

# play (takes input)
episodes = 1
your_return = 0
for episode in range(episodes):
    state = environment.reset()
    done = False

    print("_______________________________________________")
    print(f"episode {episode}")
    print("You are the agent!")
    print(f"player has {environment.player}")
    print(f"dealer's up card: {state[1]}")
    print(f"the players current sum: {state[0]}, usable ace: {state[2]}")

    while not done:
    
        action = int(input("Press 1 to hit and 0 to stay: "))
        if action:
            print("hit")

        else:
            print("stay")
        
        print("action:", action)

        state, reward, done, info = environment.step(action)
        print(f"the players current sum: {state[0]}, usable ace: {state[2]}")

    result = game_result(environment, state) # how to fix spacing
    your_return += reward

print(f"your return is {your_return}")

# this is a helper function we need for the mote_carlo_ES function
def ES_Greedy(action ,epsilon=0.3 ,n_actions=2):
    ''' 
    This function takes the best estimated action, eplsilon, and action space 
    and returns some action. 
    '''
    n = np.random.rand(1) # generate a random number from 0 to 1.

    if n >= 1-epsilon: # take random action in this case, otherwise take the suggested
      action = np.random.randint(n_actions)
    return action

def monte_carlo_ES(environment, N_episodes=100000, discount_factor=1, epsilon=0.1, theta=0.0001):
    '''
    Monte Carlo Control using Epsilon-Greedy policies.
    Finds an optimal epsilon-greedy policy.
    Args:
        environment: OpenAI gym environment.
        N_episodes: Number of episodes. Integer value.
        discount_factor: Gamma discount factor. Float betwen 0 and 1.
        epsilon: Chance the sample a random action. Float betwen 0 and 1.
        theta: stoping threshold
    Returns:
        policy: a dictionary of estimated policy for blackjack 
        V: a dictionary of estimated values for blackjack 
        Q: a dictionary of estimated action function
        DELTA: list of deltas for each episode 
    '''
    # initializations (defaultdict to avoid potential key error)
    policy = defaultdict(float) 
    V = defaultdict(float) # estimated values for blackjack 
    Q = defaultdict(float) # estimated action function for blackjack
    Counter_Visits= defaultdict(float) # number of visits to action function
    Counter_VisitsValue = defaultdict(float) # number of visits to the action function (increment mean)
    DELTA = [] # list of max difference between value functions per iteration 

    for i in range(N_episodes):

        delta = 0 # item in DELTA (i.e. max difference between value functions)  
        episode = [] # stores each state and reward for each episode   

        # reset each episode
        state = environment.reset()   
        reward = 0.0
        done = False 
        action = np.random.randint(2) # action for the first state 
        episode.append({'state':state , 'reward':reward, 'action':action}) # append first state, reward and action
        # Past states for signal visit Monte Carlo 
        state_action = [(state,action)]
        # enumerate for each episode 
        while not done:

            # take action and find next state, reward and check if the episode is done (True)
            (state, reward, done, prob) = environment.step(action)

            # check if a policy for the state exists  
            if isinstance(policy[state], np.int64):
                # obtain action from policy
                action = ES_Greedy(round(policy[state]), epsilon, 2) # call ES_Greedy function
            else:
                # if no policy for the state exists select a random action  
                action = np.random.randint(2)

            # add state reward and action to list 
            episode.append({'state':state, 'reward':reward, 'action':action})
            # add states action this is for first visit only 
            state_action.append((state,action))

        episode.reverse() # reverse list as the return is calculated from the last state
        state_action.reverse() # append the state-action pairs to a list 

        # initialize the expected total discount reward
        G = 0

        for t,step in enumerate(episode):

            # check flag for first visit
            G = discount_factor*G + step['reward']

            # check flag for first visit
            Counter_Visits[step['state'], step['action']] += 1 # increment counter for action 
            Counter_VisitsValue[step['state']] += 1  # increment counter for value function 

            # if the action function value does not exist, create an array to store them 
            if not isinstance(Q[step['state']],np.ndarray):
                Q[step['state']]= np.zeros(2) 

            # calculate mean of action function Q Value functions V using the recursive definition of mean 
            Q_s_t = Q[step['state']][step['action']]
            Q[step['state']][step['action']] += (Counter_Visits[step['state'], step['action']]**-1)*(G-Q_s_t)
            
            # record the old value of the value function 
            v = V[step['state']]
            V[step['state']] += (Counter_VisitsValue[step['state']]**-1)*(G-v)
            
            # update the policy to select the action fuciton argment with the largest value 
            policy[step['state']] = np.random.choice(np.where(Q[step['state']] == Q[step['state']].max())[0])

            # find max difference between all value functions per iteration 
            delta = max(delta,abs(v-V[step['state']]))
              
        DELTA.append(delta)
        
        if delta < theta:
            break

    return policy, V, Q, DELTA

# test
policy, V, Q, DELTA = monte_carlo_ES( environment, N_episodes=50000, discount_factor= 0.9, epsilon = 0.3, theta=-1) # force this to run all episodes

# See outputs
print("====================== DELTA ======================")
print(DELTA[10000: 10005])
print("\n======================== V ========================")
for state, value in islice(V.items(), 5):
    print(f"State: {state}, Value: {value}")
print("\n======================== Q ========================")
for state, value in islice(Q.items(), 5):
    print(f"State: {state}, Value: {value}")
print("\n===================== Policy ======================")
for state, value in islice(policy.items(), 5):
    print(f"State: {state}, Value: {value}")

average, std_win = average_wins(environment, policy, episodes=50000)
print("average wins:", average, std_win)

plt.plot(DELTA)
plt.xlabel("episodes")
plt.ylabel("delta")
plt.show()

# tuning hyperparameters
## episode length
accuracy1 = [] 
episodes = []

for n_episode in [1,50,100,500,1000,5000,10000,50000,100000]:
    print("n_episode: ", str(n_episode))
    policy, V, Q, DELTA = monte_carlo_ES(environment, N_episodes=n_episode, discount_factor=1, theta = 0)  
    average, std_win = average_wins(environment, policy, episodes=100000)
    print("n_episode: ", str(n_episode), " average: ", str(average))
    accuracy1.append(average)
    episodes.append(n_episode)

## discount factor
accuracy2=[] 
discounts=[]

for discount in [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]:
    policy, V, Q, delta = monte_carlo_ES(environment, N_episodes=100000, discount_factor=discount, epsilon=0.5, theta=-1)  
    average, std_win=average_wins(environment, policy, episodes=100000)
    print("discount: ", str(discount), " average: ", str(average))
    discounts.append(discount)
    accuracy2.append(average)

## epsilon
accuracy3=[] 
epsilons=[]

for es in [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]:
    policy, V, Q, delta = monte_carlo_ES(environment, N_episodes=100000, discount_factor=1, epsilon=es, theta=-1)  
    average, std_win = average_wins(environment, policy, episodes=100000)
    print("epsilon: ", str(es), " average: ", str(average))
    epsilons.append(es)
    accuracy3.append(average)

# visualize tuning
fig, ax = plt.subplots(1, 3, figsize = (12, 3))
ax[0].scatter(episodes, accuracy1)
ax[1].scatter(discounts, accuracy2)
ax[2].scatter(epsilons, accuracy3)

ax[0].set(xlabel = "Episode", 
          ylabel = "accuracy")
ax[1].set(title = "Model Tuning", 
          xlabel = "discount factor")
ax[2].set(xlabel = "Epsilon")

plt.tight_layout()

# tuned model result
policy, V, Q, DELTA = monte_carlo_ES(environment, N_episodes=100000, discount_factor=1.0, epsilon = 0.1, theta=-1)
average ,std_win = average_wins(environment,policy,episodes=100000)

print("average wins:",average, std_win)

## Visualizations
# Policy
plot_policy_blackjack(policy)

# Q-function value
plot_value_function(V)