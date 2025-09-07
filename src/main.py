import asyncio
import websockets
import json
from poke_env import RandomPlayer
import RelayPlayer
from poke_env import AccountConfiguration
import data.teams as teams
from Utils import logger

waiting_players = []
lost_players = []

won_player_count:int = 0
lost_player_count:int = 0
joined_player:int = 0
format = "gen9randombattle"
random_format:bool = False
tournament_running:bool = False
total_players_at_start:int = 0

pair_event = asyncio.Event()
shutdown_event = asyncio.Event()

taken_usernames:list[str] = []

async def handler(ws):
	global joined_player
	global random_format
	global taken_usernames
	joined_player += 1
	#print("Client connected!")
	logger.log("client connected")

	client_registered:bool = False
	queue = asyncio.Queue()
	
	
	try:
		async for raw in ws:
			data = json.loads(raw)
			#print(f"Got data from Godot: {data}")

			if data["type"] == "register_request":
				name = data["name"]
				if name in taken_usernames and client_registered == False or name == "":
					await ws.send(json.dumps(
						{
							"type":"name_taken"
						}
					))
				elif client_registered == False:
					client_registered = True
					taken_usernames.append(name)

					client_player = RelayPlayer.RelayPlayer(
						account_configuration = AccountConfiguration(name,""),
						web_socket = ws,
						input_queue=queue,
						battle_format=format,
						#team=teams.teams[joined_player-1], #if random_format == False else None,
						message_handler=handle_relay_message)
					
					waiting_players.append((client_player,queue))
					logger.log(f"client succesfully registered with username {name}")
					await ws.send(json.dumps(
						{
							"type":"registration_sucessful"
						}
					))

			elif data["type"] == "move" or data["type"] == "switch":
				#print("vaild input received")
				joined_player -= 1
				await queue.put(data)


	except websockets.exceptions.ConnectionClosed:
		logger.log("client disconnected")
		#print("Client disconnected")

def handle_relay_message(player_id,payload):
	global lost_player_count, won_player_count
	#print(f"[Relay->Handler] {player_id}: {payload}")

	player, ws = payload["payload"]["player"], payload["payload"]["ws"]

	if	payload["message"] == "battle_lost":
		lost_players.append((player,ws))
		won_player_count += 1
		loser_position = check_loser_position()
		#print(f"loser position is: {str(loser_position)}")
		logger.log(f"player {player.username} lost, finishing position {loser_position}")
		player.battle_position_commuincator(loser_position)

	elif payload["message"] == "battle_won":
		lost_player_count += 1
		winner_position = check_winner_position()
		#print("the winner position is at:",str(winner_position))
		logger.log(f"payer {player.username} won, player survival position {winner_position}")
		if winner_position >= 2:
			waiting_players.append((player,ws))
			pair_event.set()
		elif winner_position == 1:
			#print("we have a winner")
			logger.log(f"player {player.username} won the tournament")
			player.tournament_champion_communicator()

def check_round_type():
	global total_players_at_start,lost_players
	round_num = total_players_at_start - len(lost_players)
	if  round_num == 2:
		return "Finals starting"
	elif round_num <= 4:
		return "Semi finals starting"
	elif round_num <= 8:
		return "quarter finals starting"
	return None

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
			(p1,q1),(p2,q2) = waiting_players.pop(0),waiting_players.pop(0)
			#print(f"pairing players {p1.username} with {p2.username}")
			logger.log(f"pairing players {p1.username} with {p2.username}")
			asyncio.create_task(start_battle(p1,q1,p2,q2))
		


async def admin_cli():
	global tournament_running
	global total_players_at_start
	global format
	global random_format
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
				logger.log(f"Tournment starts with {len(waiting_players)} players")
				logger.log("players participating are " + ", ".join(p[0].username for p in waiting_players))
				tournament_running = True
				pair_event.set()
				total_players_at_start = len(waiting_players)
				print("Tournament starts")
			else:
				print("Tournament already running")

		elif cmd == "stop":
			if tournament_running:
				tournament_running = False
				logger.log("tournament stopped")
				print("Tournament stopped")
			else:
				print("Tournament already stopped")
		elif cmd == "quit":
			logger.log("attempting to shutdown")
			shutdown_event.set()
			print("shutting down server")
			break
		
		elif cmd.startswith("format"):
			result = cmd.split()
			if len(result) == 2:
				format = result[1]
				random_format = False
				logger.log(f"changed format to {format}")
			elif len(result) == 3:
				if result[1] == "random":
					format = result[2]
					random_format = True
					logger.log(f"changed format to {format}")
				else:
					print("invalid format")
			else:
				print("invalid format")
		else:
			logger.log(f"unknown command entered: {cmd}")
			print("command unknown")

async def start_battle(p1, q1, p2, q2):
	round_type = check_round_type()
	logger.log(round_type) if round_type != None else logger.log("regular round is about to be started")
	p1.battle_start_callback()
	p2.battle_start_callback()
	logger.log(f"starting battle of two players {p1.username} and {p2.username}")
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

logger.create_log_file()
asyncio.run(main())