from poke_env.player import Player

from poke_env.battle import AbstractBattle
from Utils import battleData
import json
import asyncio

class RelayPlayer(Player):
	def __init__(self,web_socket,input_queue,**kwargs):
		super().__init__(**kwargs)
		self.input_queue = input_queue
		self.web_socket = web_socket
		self.last_turn = -1
		self._watchers = {}

	async def watch_turns(self,battle, web_socket):
		last_turn = battle.turn
		while not battle.finished:
			if battle.turn != last_turn:
				# turn has ended → send update
				await web_socket.send(json.dumps({
					"type": "turn_end",
					"turn": battle.turn,
					"state": battleData.battle_to_dict(battle),
					"available_moves": [m.id for m in battle.available_moves],
					"available_switches": [p.species for p in battle.available_switches],
				}))
				last_turn = battle.turn
			await asyncio.sleep(0.1)

	async def choose_move(self, battle):
		if battle not in self._watchers:
			asyncio.create_task(self.watch_turns(battle=battle,web_socket=self.web_socket))
			self._watchers[battle] = True

		await self.web_socket.send(json.dumps(
			{
				"type": "request",
				"turn": battle.turn,
				"state": battleData.battle_to_dict(battle),
				"available_moves": [m.id for m in battle.available_moves],
				"available_switches": [p.species for p in battle.available_switches],
			}
		))
		battle.battle_tag
		action = await self.input_queue.get()
		idx = action["index"]

		if action["type"] == "move":
			
			if 0 <= idx < len(battle.available_moves):
				return self.create_order(battle.available_moves[idx])
			else:
				return self.choose_random_move(battle)
		
		elif action["type"] == "switch":
			if 0 <= idx < len(battle.available_switches):
				return self.create_order(battle.available_switches[idx])
			else:
				return self.choose_random_move(battle)
		else:
			return self.choose_random_move(battle)



	def _battle_finished_callback(self, battle):
		asyncio.create_task(self.web_socket.send(json.dumps({
			"type": "battle_end",
			"won": battle.won,
			"state": battleData.battle_to_dict(battle),
		})))
	
