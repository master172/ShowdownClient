import asyncio
import websockets
import json
from poke_env import RandomPlayer
import RelayPlayer

async def handler(ws):

	print("Client connected! Starting battle...")

	queue = asyncio.Queue()
	client_player = RelayPlayer.RelayPlayer(username="Godot Player",web_socket = ws,input_queue=queue,battle_format="gen8randombattle")
	opponent = RandomPlayer(battle_format="gen8randombattle")

	
	asyncio.create_task(client_player.battle_against(opponent,n_battles=1))
	
	#asyncio.create_task(client_player.watch_turns(web_socket=ws))
	#asyncio.create_task(watcher.watch_battle(player=client_player,ws=ws))

	try:
		async for raw in ws:
			data = json.loads(raw)
			print(f"Got data from Godot: {data}")

			if data["type"] == "move" or data["type"] == "switch":
				print("vaild input received")
				await queue.put(data)

	except websockets.exceptions.ConnectionClosed:
		print("Client disconnected")

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()


asyncio.run(main())