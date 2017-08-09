RL baseline (RL as X against AntiMinMax)
=================
In this baseline, we train an RL strategy w/ learning rate 0.1, explore rate 0.1
against AntiMinMax strategy, which is a variant of DefensiveStrat1 that always ties
with our (non-randomized) MinMax strategy.

As you can see from the training log, RL quickly learns to defeat AntiMinMax with
winning rate approaching 90%: 

10000 runs: (X win, X lose, tie) = [0.462, 0.4799, 0.0581]
q_table size, #updates =  (607, 26766)
10000 runs: (X win, X lose, tie) = [0.5599, 0.3837, 0.0564]
q_table size, #updates =  (751, 55262)
10000 runs: (X win, X lose, tie) = [0.5733, 0.3589, 0.0678]
q_table size, #updates =  (825, 84805)
10000 runs: (X win, X lose, tie) = [0.5812, 0.3526, 0.0662]
q_table size, #updates =  (898, 114273)
10000 runs: (X win, X lose, tie) = [0.797, 0.1379, 0.0651]
q_table size, #updates =  (1076, 142940)
10000 runs: (X win, X lose, tie) = [0.8685, 0.0809, 0.0506]
q_table size, #updates =  (1101, 171159)
10000 runs: (X win, X lose, tie) = [0.8875, 0.0637, 0.0488]
q_table size, #updates =  (1113, 199375)
10000 runs: (X win, X lose, tie) = [0.8819, 0.0672, 0.0509]
q_table size, #updates =  (1117, 227672)
10000 runs: (X win, X lose, tie) = [0.8901, 0.0631, 0.0468]
q_table size, #updates =  (1120, 255941)
INFO:rl:saving qtable to /tmp/rl.pickle
10000 runs: (X win, X lose, tie) = [0.8916, 0.0583, 0.0501]
q_table size, #updates =  (1120, 284237)

But if you look at one of the games, RL really exploits the defensive nature of 
its opponent. When there are already two Os in a row, RL proceeds to get two Xs
line up, knowing that AntiMinMax would always prioritize for defensive moves.


RL against WeakenedMinMax
=============================
