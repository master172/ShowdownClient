import asyncio
from poke_env import ServerConfiguration,AccountConfiguration
from players import ConsolePlayer

async def main():
	player1 = ConsolePlayer.ConsolePlayer(
		battle_format="gen8randombattle",
		account_configuration=AccountConfiguration("Human1","")
	)
	player2 = ConsolePlayer.ConsolePlayer(
		battle_format="gen8randombattle",
		account_configuration=AccountConfiguration("Human2","")
	)

	await player1.battle_against(player2,n_battles=1)
	print("Battle Finsihed")

if __name__ == "__main__":
	asyncio.run(main())