import asyncio
from players import MaxDamagePlayer
from poke_env import AccountConfiguration, ServerConfiguration

async def main():
	bot_player = MaxDamagePlayer.MaxDamagePlayer(
		account_configuration=AccountConfiguration("SMaxDamageBotS","")
	)

	await bot_player.accept_challenges(None,1)

	for battle in bot_player.battles.values():
		print(battle.rating," and ",battle.opponent_rating)

if __name__ == "__main__":
	asyncio.run(main())