import asyncio
import websockets
import json
from poke_env import RandomPlayer
import RelayPlayer
from poke_env import AccountConfiguration
import data.teams as teams

waiting_players = []
lost_players = []

won_player_count:int = 0
lost_player_count:int = 0
joined_player:int = 0
format = "gen9ou"
tournament_running:bool = False
total_players_at_start:int = 0

pair_event = asyncio.Event()
shutdown_event = asyncio.Event()

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
	global lost_player_count, won_player_count
	#print(f"[Relay->Handler] {player_id}: {payload}")

	player, ws = payload["payload"]["player"], payload["payload"]["ws"]

	if	payload["message"] == "battle_lost":
		lost_players.append((player,ws))
		won_player_count += 1
		print(f"loser position is: {str(check_loser_position())}")
	elif payload["message"] == "battle_won":
		waiting_players.append((player,ws))
		lost_player_count += 1
		print("the winner position is at:",str(check_winner_position()))
		pair_event.set()

def check_round_type():
	global total_players_at_start,lost_players
	round_num = total_players_at_start - len(lost_players)
	if  round_num == 2:
		print("Finals starting")
	elif round_num <= 4:
		print("Semi finals starting")
	elif round_num <= 8:
		print("quarter finals starting")
	

def check_loser_position():
	global total_players_at_start
	global won_player_count
	loser_position:int = (total_players_at_start - won_player_count) + 1
	return loser_position
	
def check_winner_position():
	global lost_player_count
	global total_players_at_start
	winner_position:int = total_players_at_start - lost_player_count
	return winner_position

async def pair_players():
	global tournament_running

	while not shutdown_event.is_set():

		pair_task = asyncio.create_task(pair_event.wait())
		shutdown_task = asyncio.create_task(shutdown_event.wait())


		done, pending = await asyncio.wait(
			[pair_task,shutdown_task],
			return_when=asyncio.FIRST_COMPLETED
		)

		for task in pending:
			task.cancel()

		if shutdown_event.is_set():
			break

		pair_event.clear()

		while tournament_running and len(waiting_players) >= 2:
			print("two players availaible")
			print(p[0].username for p in waiting_players)
			(p1,q1),(p2,q2) = waiting_players.pop(0),waiting_players.pop(0)
			print(f"pairing players {p1.username} with {p2.username}")
			asyncio.create_task(start_battle(p1,q1,p2,q2))
		


async def admin_cli():
	global tournament_running
	global total_players_at_start
	loop = asyncio.get_event_loop()
	while not shutdown_event.is_set():
		cmd = await loop.run_in_executor(None,input,"> ")

		if shutdown_event.is_set():
			break

		if cmd == "players":
			print(f"waiting players: {len(waiting_players)}")

		elif cmd == "player_names":
			print("waiting player names:", {p[0].username for p in waiting_players})

		elif cmd == "player_count":
			print(f"tournament started with: {total_players_at_start}") if tournament_running else print("tournament not started yet")
		elif cmd == "start":
			if not tournament_running:
				tournament_running = True
				pair_event.set()
				total_players_at_start = len(waiting_players)
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
			shutdown_event.set()
			print("shutting down server")
			break
		else:
			print("command unknown")

async def start_battle(p1, q1, p2, q2):
	check_round_type()
	p1.battle_start_callback()
	p2.battle_start_callback()
	await p1.battle_against(p2, n_battles=1)

async def main():
	server = await websockets.serve(handler, "localhost", 8765)
	#cli = await admin_cli()
	#pairing_loop = await pair_players()
	await asyncio.gather(admin_cli(),pair_players(),shutdown_event.wait())

	print("Closing server…")
	server.close()
	await server.wait_closed()
	print("Server closed.")

asyncio.run(main())