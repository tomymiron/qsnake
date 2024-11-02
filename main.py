from players import AiPlayer, RandomPlayer
from game import Game
import sys

ALLOWED_PLAYERS = {"ai": AiPlayer, "random": RandomPlayer}

def print_help():
    print("Como correr el script: \n")
    print("\t python3 main.py ai no 1000")

if __name__ == "__main__":
    try:
        player_type = sys.argv[1].lower()
        handle_train = sys.argv[2].lower()
        training_number = sys.argv[3]
    
    except Exception:
        print("Error, parametros pasados de manera incorrecta")
        print_help()
    
    game = Game(32)
    if player_type in ALLOWED_PLAYERS:
        player = ALLOWED_PLAYERS[player_type](game)
    else:
        raise Exception("Nombre de jugador no conocido")

    if player_type == "ai":
        if handle_train in {"si", "true"}:
            player.train()
        
    player.run(training_number)