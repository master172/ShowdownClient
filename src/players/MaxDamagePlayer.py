from poke_env.player import Player

class MaxDamagePlayer(Player):
	def choose_move(self, battle):
		if battle.available_moves:
			best_move = max(battle.available_moves,key=lambda move: move.base_power)

			if battle.can_tera:
				return self.create_order(best_move,terastallize=True)
			return self.create_order(best_move)
		else:
			return self.choose_random_move(battle)