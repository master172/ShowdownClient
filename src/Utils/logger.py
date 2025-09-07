from datetime import datetime
from pathlib import Path

global_filename:str = ""

def create_file_path():
	base_dir = Path(__file__).resolve().parents[2]
	log_folder =  base_dir / "logs"
	log_folder.mkdir(parents=True, exist_ok=True)
	timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	log_file = log_folder / f"log_{timestamp}.txt"
	return log_file, timestamp

def create_log_file():
	global global_filename
	filename,timestamp = create_file_path()
	global_filename = filename
	with open(filename,"w") as file:
		file.write(f"log starts at {timestamp}\n")

def log(msg:str):
	global global_filename
	if global_filename == None:
		print("No log file created")
		return
	timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	with open(global_filename,"a") as file:
		file.write(f"logged message at {timestamp} message: {msg}\n")