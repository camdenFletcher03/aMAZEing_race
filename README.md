# aMAZEing_race
 A simple procedurally generated maze game. 

This is a simple maze based game where the player has to beat/race a CPU agent to the white exit circle and get through all 25 levels to win! 
The player's icon is green while the agent's icon is red, the exit icon is white. The game is over if the agent beats you to the exit and you win if you get through all levels without losing the race.
Each maze level is procedurally generated in real time using a back tracking algorithm, and the mazes size is increased by 1 for each continuing level. The agent uses a breadth first search to compute the path to the exit. The agent than plays back each step with a small delay (200-300ms) per cell in order to follow the maze to the exit cell.

