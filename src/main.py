import asyncio
import websockets
import json
from poke_env import RandomPlayer
import RelayPlayer
from poke_env import AccountConfiguration
import data.teams as teams

waiting_players = []
joined_player:int = 0
format = "gen9ou"
tournament_running:bool = False
total_players_at_start:int = 0
running_players:int = 0

pair_event = asyncio.Event()

async def handler(ws):
	global joined_player
	joined_player += 1
	print("Client connected!")

	queue = asyncio.Queue()
	client_player = RelayPlayer.RelayPlayer(
		account_configuration = AccountConfiguration(f"Godot Player {joined_player}",""),
		web_socket = ws,
		input_queue=queue,
		battle_format=format,
		team=teams.quick_teams[joined_player-1],
		message_handler=handle_relay_message)

	waiting_players.append((client_player,queue))
	
	try:
		async for raw in ws:
			data = json.loads(raw)
			print(f"Got data from Godot: {data}")

			if data["type"] == "move" or data["type"] == "switch":
				print("vaild input received")
				await queue.put(data)

	except websockets.exceptions.ConnectionClosed:
		
		print("Client disconnected")

def handle_relay_message(player_id,payload):
	print(f"[Relay->Handler] {player_id}: {payload}")

	if payload["message"] == "battle_won":
		waiting_players.append((payload["payload"]["player"],payload["payload"]["ws"]))
		pair_event.set()

async def pair_players():
	global tournament_running
	while True:
		await pair_event.wait()
		pair_event.clear()

		while tournament_running and len(waiting_players) >= 2:
			print("two players availaible")
			print(p for p in waiting_players)
			(p1,q1),(p2,q2) = waiting_players.pop(0),waiting_players.pop(0)
			print(f"pairing players {p1.username} with {p2.username}")
			asyncio.create_task(start_battle(p1,q1,p2,q2))


async def admin_cli():
	global tournament_running
	loop = asyncio.get_event_loop()
	while True:
		cmd = await loop.run_in_executor(None,input,"> ")
		if cmd == "players":
			print(f"waiting players: {len(waiting_players)}")
		elif cmd == "player_names":
			print("waiting player names:", {p[0].username for p in waiting_players})
		elif cmd == "start":
			if not tournament_running:
				tournament_running = True
				pair_event.set()
				print("Tournament starts")
			else:
				print("Tournament already running")
		elif cmd == "stop":
			if tournament_running:
				tournament_running = False
				
				print("Tournament stopped")
			else:
				print("Tournament already stopped")
		elif cmd == "quit":
			for task in asyncio.all_tasks():
				task.cancel()
			print("shutting down server")
			exit(0)
		else:
			print("command unknown")

async def start_battle(p1, q1, p2, q2):
	p1.battle_start_callback()
	p2.battle_start_callback()
	await p1.battle_against(p2, n_battles=1)

async def main():
	server = await websockets.serve(handler, "localhost", 8765)
	#cli = await admin_cli()
	#pairing_loop = await pair_players()
	await asyncio.gather(admin_cli(),pair_players())


asyncio.run(main())