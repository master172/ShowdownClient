def battle_to_dict(battle):
	def pokemon_view(poke):
		if poke is None:
			return None
		return {
			"species": poke.species,
			"current_hp": poke.current_hp,
			"max_hp": poke.max_hp,
			"fainted": poke.fainted,
			"status": str(poke.status) if poke.status else None,
			"last_move_used": poke.last_request if poke.last_request else None,
		}

	return {
		"turn": battle.turn,
		"finished": battle.finished,
		"won": battle.won,
		"my_team": {
			sid: pokemon_view(p) for sid, p in battle.team.items()
		},
		"opponent_team": {
			sid: pokemon_view(p) for sid, p in battle.opponent_team.items()
		},
		"active_pokemon": pokemon_view(battle.active_pokemon),
		"opponent_active": pokemon_view(battle.opponent_active_pokemon),
	}
