from poke_env import Player

class ConsolePlayer(Player):
	async def choose_move(self, battle):
		print(f"\n{self.username}'s turn in battle vs {battle.opponent_username}")
		print("Acrive")