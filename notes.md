RL baseline (RL as X against AntiMinMax)
=================
In this baseline, we train an RL strategy w/ learning rate 0.1, explore rate 0.1
against AntiMinMax strategy, which is a variant of DefensiveStrat1 that always ties
with our (non-randomized) MinMax strategy.

As you can see from the training log, RL quickly learns to defeat AntiMinMax with
winning rate approaching 90%: 

```
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
```

But if you look at one of the games, RL really exploits the defensive nature of 
its opponent. When there are already two Os in a row, RL proceeds to get two Xs
line up, knowing that AntiMinMax would always prioritize for defensive moves.

Next, we explore a more worth opponent: weakened MinMax.


To Weaken MinMax, I end up improve it first
=============================
I weaken minmax in exactly one state. In the opening move, X chose 2 (top right). 
minmax (playing O) has to pick 4 (center of the board). I changed it to pick 1 
instead -- which would lead to a loss.

```
+--------------------------+
|       0|  (O)  1|   X   2|
|--------------------------|
|       3|       4|       5|
|--------------------------|
|       6|       7|       8|
----------------------------
```

If X moves next on 4, minmax strangely picks 0. Very bad. Why? 
```
+--------------------------+
|  (O)  0|   O   1|   X   2|
|--------------------------|
|       3|   X   4|       5|
|--------------------------|
|       6|       7|       8|
----------------------------
```

My hunch is that minmax simply sees no way to win/draw. Since all moves leads to defeat,
it just picks a random move. We need a fine-grained evaluation of moves: minimum number 
of moves to win or maximum number of moves to avoid loss. The old MinMax strategy is 
renamed to MinMaxCrude, the new MinMax is much more reasonable!


RL (X) against WeakenedMinMax (O)
=============================

Below is the training log of RL against WeakenedMinMax. Once it discovers the hole, 
the tide is turned. Nonetheless, it does take a while, more than 50k games, to 
discover the loop-hole!

```
10000 runs: (X win, X lose, tie) = [0.0, 0.9947, 0.0053]
q_table size, #updates =  (333, 18551)
10000 runs: (X win, X lose, tie) = [0.0, 0.9974, 0.0026]
q_table size, #updates =  (359, 37101)
10000 runs: (X win, X lose, tie) = [0.0, 0.9966, 0.0034]
q_table size, #updates =  (372, 55553)
10000 runs: (X win, X lose, tie) = [0.0, 0.9974, 0.0026]
q_table size, #updates =  (396, 74059)
10000 runs: (X win, X lose, tie) = [0.0, 0.9969, 0.0031]
q_table size, #updates =  (396, 92660)
10000 runs: (X win, X lose, tie) = [0.0001, 0.9971, 0.0028]
q_table size, #updates =  (400, 111180)
10000 runs: (X win, X lose, tie) = [0.4416, 0.5447, 0.0137]
q_table size, #updates =  (417, 134337)
10000 runs: (X win, X lose, tie) = [0.7809, 0.199, 0.0201]
q_table size, #updates =  (431, 160836)
10000 runs: (X win, X lose, tie) = [0.7871, 0.191, 0.0219]
q_table size, #updates =  (433, 187394)
INFO:utils:saving qtable to /tmp/rl.pickle
10000 runs: (X win, X lose, tie) = [0.7887, 0.1871, 0.0242]
q_table size, #updates =  (433, 214113)
```

Side note: I intentionally tried to make the loop hole hard to stumble upon 
by requiring the first move to be at top-right. Well, that may not be completely
true, but I did observe RL likes to explore the first move at top-left. Maybe it's
something with our randomization. The real difficulty is that even when RL stumbles
on the designed configuration, it needs to play a while to figure out a way to win
in this setup. It's playing against MinMax after all.

Once the winning setup is revealed, RL exploits the trap all the time.


RL (X) against MinMax (O)
============================

RL cannot seem to learn anything against MinMax:
```
10000 runs: (X win, X lose, tie) = [0.0, 0.995, 0.005]
q_table size, #updates =  (326, 18473)

...

10000 runs: (X win, X lose, tie) = [0.0, 0.9964, 0.0036]
q_table size, #updates =  (393, 184906)
```
After 100k games, it still lost mostly. The issue is the RL value function
treats draw the same as loss.

Let's change the reward function:
```
win: 1.0
loss: 0 -> -1
draw: 0
unfinished: 0.5 -> 0
```
Still no progress. Bug? Indeed, we are missing one update from strat.end_game().
With this fix RL ties most of the time with MinMax!