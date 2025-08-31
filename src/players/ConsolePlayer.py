from poke_env import Player

class ConsolePlayer(Player):
	async def choose_move(self, battle):
		print(f"\n{self.username}'s turn in battle vs {battle.opponent_username}")
		print("Active pokeomn:",battle.active_pokemon)
		print("Pokemon Hp:",battle.active_pokemon.current_hp, "out of:",battle.active_pokemon.max_hp)
		if battle.opponent_active_pokemon != None:
			print("Opposing pokemon Hp:",battle.opponent_active_pokemon.current_hp," out of:",battle.opponent_active_pokemon.max_hp)
		print("Availaibel switches:",battle.available_switches)
		for i, mon in enumerate(battle.available_switches):
			print(f"{i}. {mon}")

		print("Availaible moves:",battle.available_moves)
		for i,Move in enumerate(battle.available_moves):
			print(f"{i}. {Move}")
		
		while True:
			choice :str = input("Enter your choice (0, 1, 2... for moves; s0, s1... for switches): ").strip()
			if choice.isdigit() and 0 <= int(choice) < len(battle.available_moves):
				return self.create_order(battle.available_moves[int(choice)])
			elif choice.startswith("s") and choice[1:].isdigit():
				idx = int(choice[1:])
				if 0 <= idx < len(battle.available_switches):
					return self.create_order(battle.available_switches[idx])
			
			print("Invalid Input, try again")
		
		