import asyncio
from players import MaxDamagePlayer
from data import teams
from poke_env import RandomPlayer

# The RandomPlayer is a basic agent that makes decisions randomly,
# serving as a starting point for more complex agent development.

first_player = None
second_player = None

def create_players():
	global first_player
	global second_player
	first_player = RandomPlayer(battle_format = "gen8ou",team=teams.team_1)
	second_player = MaxDamagePlayer.MaxDamagePlayer(battle_format = "gen8ou",team=teams.team_2)

create_players()

def log_messages():
	print(
		f"Player {first_player.username} won {first_player.n_won_battles} out of {first_player.n_finished_battles} played"
	)
	print(
		f"Player {second_player.username} won {second_player.n_won_battles} out of {second_player.n_finished_battles} played"
	)

	# Looping over battles

	for battle_tag, battle in first_player.battles.items():
		print(battle_tag, battle.won)

async def battle_player():
	

	# The battle_against method initiates a battle between two players.
	# Here we are using asynchronous programming (await) to start the battle.
	await first_player.battle_against(second_player, n_battles=10)

asyncio.run(battle_player())

	
log_messages()