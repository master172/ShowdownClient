import asyncio
import websockets
import json
from poke_env import RandomPlayer
import RelayPlayer
from poke_env import AccountConfiguration

waiting_players = []

async def handler(ws):

	print("Client connected! Starting battle...")

	queue = asyncio.Queue()
	client_player = RelayPlayer.RelayPlayer(
		account_configuration = AccountConfiguration(f"Godot Player {len(waiting_players)+1}",""),
		web_socket = ws,
		input_queue=queue,
		battle_format="gen8randombattle")

	waiting_players.append((client_player,queue))
	
	
	if len(waiting_players) >= 2:
		while len(waiting_players) >= 2:
			(p1,q1),(p2,q2) = waiting_players.pop(0),waiting_players.pop(0)
			print(f"pairing players {p1} with {p2}")
			asyncio.create_task(start_battle(p1,q1,p2,q2))

	try:
		async for raw in ws:
			data = json.loads(raw)
			print(f"Got data from Godot: {data}")

			if data["type"] == "move" or data["type"] == "switch":
				print("vaild input received")
				await queue.put(data)

	except websockets.exceptions.ConnectionClosed:
		print("Client disconnected")

async def start_battle(p1, q1, p2, q2):
    await p1.battle_against(p2, n_battles=1)

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()


asyncio.run(main())