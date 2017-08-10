Reinforcement Learning in Tic-Tac-Toe
=====================================

My excursion into RL, as described in Sutton and Barto book. Several strategies are implemented:
MinMax (which you cannot beat), a couple hand-crafted strats with deficiencies that RL can hopefully
learn and exploit, and of course, RL strategy.

To Play
-------
Run game_play.py. You can try run_manual() to play a game yourself, against any of the five strategies!

Fun things to try:
- train RL from scratch against some more intelligent strategies, see how fast it improves the winning odds
- train RL against MinMax: could it achieve expert-level performance? how long?
- RL could be better than MinMax as it can discover and exploit weakness in its opponent, while MinMax would
 not even try as it assumes its opponent plays optimally. Demonstrate this!
- The current RL agent learns a single role (either X or O). Is this easy to relax?

Theory
-------
We follow this update rule per Wes:

    V(s) <- V(s) + alpha * [ V(s') - V(s) ]
    
which seems way too simple relative to Q-learning:

    Q(s,a) <- Q(s,a) + alpha * [ r + max_a' Q(s',a') - Q(s,a) ]

- r, the immediate reward, is 0 most of the time.
- discount factor is 1 for chess, i.e. no discount.

In chess, Q(s,a) is really the board configuration after our move (deterministic).
Then, the opponent makes his move (environment, stochastic), leading to s'.

For clarity, s is the state (the board we are facing), (s,a) is the Q-state, and 
(s,a,s') is the transition. Simply knowing the value function V doesn't give us a policy.
But (s,a) is the board state after our move, if we denote 

    t = (s,a)
    V(t) = Q(s,a)
    
i.e. t is the Q-state, V(t) being the q-value (abuse of notation), from which we can 
derive a policy, then Q-learning becomes:

    V(t) <- V(t) + alpha * [ V(s') - V(t) ]
    V(s') = max_a' Q(s',a')
    
In the code, we only store V(t) in Q-table. V(s) is calculated on the fly
during exploitation.

License
-------
Created by Hua Yu with contributions from Robert Yu

Inspired by: https://github.com/tansey/rl-tictactoe.git

9/4/2016

Code released under the GPL license.