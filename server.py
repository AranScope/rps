import importlib
import os
import json

from flask import Flask, request
app = Flask(__name__)

class InvalidScriptError(RuntimeError):
    pass

@app.route('/submit', methods=['POST'])
def submit_script():
    print('requested endoiasd')
    add_script(request.form['name'], request.form['script'])

    try:
        wins, losses, draws = test_script(request.form['name'])
        # name = 
        # if leaderboard[['win/loss'] < wins/losses:
        leaderboard[request.form['name']] = {
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'win/loss': wins/max(1, losses)
        }

        open('leaderboard.json', 'w').write(json.dumps(leaderboard))

        return 'Wins: {}, Losses: {}, Draws: {}'.format(wins, losses, draws)
        
    except InvalidScriptError:
        return 'Invalid script'


GAMES_PER_SCRIPT = 100
MAX_REDOS = 3
leaderboard = json.loads(open('leaderboard.json').read())

def load_scripts(blacklist=[]):
    script_paths = (os.path.splitext(path)[0] for path in os.listdir('scripts') if os.path.splitext(path)[1] == '.py')
    scripts = []
    
    for script_path in script_paths:
        if script_path not in blacklist:
            try:
                mod = importlib.import_module('scripts.{}'.format(script_path))
                scripts.append(mod)
            except:
                print('tried to load invalid script {}'.format(script_path))
                continue

    print(scripts)
    return scripts

def add_script(script_title, script_text):
    with open('scripts/{}.py'.format(script_title), 'w') as f:
        f.write(script_text)

def test_script(script_title):
    wins = 0
    losses = 0
    draws = 0

    for opponent_script in load_scripts(blacklist=[script_title]):
        print("running against", opponent_script.__name__)
        try:
            script = importlib.import_module('scripts.{}'.format(script_title))
        except:
            raise InvalidScriptError()

        try:
            my_turn = script.turn("none")
            opponent_turn = opponent_script.turn("none")
        except:
            raise InvalidScriptError()

        for _ in range(GAMES_PER_SCRIPT):
            for _ in range(MAX_REDOS):

                if(my_turn == "rock"):
                    if(opponent_turn == "rock"):
                        continue
                    elif(opponent_turn == "paper"):
                        losses += 1
                        break
                    elif(opponent_turn == "scissors"):
                        wins += 1
                        break
                elif(my_turn == "paper"):
                    if(opponent_turn == "rock"):
                        wins += 1
                        break
                    elif(opponent_turn == "paper"):
                        continue
                    elif(opponent_turn == "scissors"):
                        losses += 1
                        break
                elif(my_turn == "scissors"):
                    if(opponent_turn == "rock"):
                        losses += 1
                        break
                    elif(opponent_turn == "paper"):
                        wins += 1
                        break
                    elif(opponent_turn == "scissors"):
                        continue
            else:
                draws += 1
                
            my_turn, opponent_turn = script.turn(opponent_turn), opponent_script.turn(my_turn)

        
    print("Script: {}, Wins: {}, Losses: {}, Draws: {}".format(script_title, wins, losses, draws))
    return wins, losses, draws
                
app.run()