import importlib
import os
import json

from flask import Flask, request, render_template

class InvalidScriptError(RuntimeError):
    pass

app = Flask(__name__)

GAMES_PER_SCRIPT = 100
MAX_REDOS = 3
leaderboard = None

with open('leaderboard.json') as f:
    leaderboard = json.loads(f.read())

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/leaderboard', methods=['GET'])
def lb():
    scores = []

    for key in sorted(leaderboard, key=lambda k: 1/leaderboard[k]['win/loss']):
        scores.append({
            'name': key,
            'winlossratio': leaderboard[key]['win/loss']
        })
            
    return render_template('leaderboard.html', scores=scores)


@app.route('/submit', methods=['POST'])
def submit_script():
    print('requested endoiasd')

    if 'script' not in request.form:
        return "Missing script text"

    if 'name' not in request.form:
        return "Missing name text"

    add_script(request.form['name'], request.form['script'])

    try:
        wins, losses, draws, games = test_script(request.form['name'])
        # name = 
        # if leaderboard[['win/loss'] < wins/losses:
        leaderboard[request.form['name']] = {
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'win/loss': wins/max(1, losses)
        }

        with open('leaderboard.json', 'w') as f:
            f.write(json.dumps(leaderboard))

        return render_template('submit.html', result='Wins: {}, Losses: {}, Draws: {}'.format(wins, losses, draws), games=games)
        
    except InvalidScriptError:
        return 'Invalid script'




def load_scripts(blacklist=[]):
    script_paths = (os.path.splitext(path)[0] for path in os.listdir('scripts') if os.path.splitext(path)[1] == '.py')
    scripts = []
    importlib.invalidate_caches()
    
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

    results = []

    for opponent_script in load_scripts(blacklist=[script_title]):
        print("running against", opponent_script.__name__)
        try:
            importlib.invalidate_caches()
            script = importlib.import_module('scripts.{}'.format(script_title))
        except:
            raise InvalidScriptError()

        my_turn = "none"
        opponent_turn = "none"

        for _ in range(GAMES_PER_SCRIPT):
            for _ in range(MAX_REDOS):
                try:
                    my_turn, opponent_turn = script.turn(opponent_turn), opponent_script.turn(my_turn)
                except:
                    raise InvalidScriptError()

                if(my_turn == "rock"):
                    if(opponent_turn == "rock"):
                        continue
                    elif(opponent_turn == "paper"):
                        results.append({'outcome': 'loss', 'player': script_title, 'player_turn': my_turn, 'opponent': opponent_script.__name__.replace("scripts.", ""), 'opponent_turn': opponent_turn})
                        losses += 1
                        break
                    elif(opponent_turn == "scissors"):
                        results.append({'outcome': 'win', 'player': script_title, 'player_turn': my_turn, 'opponent': opponent_script.__name__.replace("scripts.", ""), 'opponent_turn': opponent_turn})
                        wins += 1
                        break
                elif(my_turn == "paper"):
                    if(opponent_turn == "rock"):
                        results.append({'outcome': 'win', 'player': script_title, 'player_turn': my_turn, 'opponent': opponent_script.__name__.replace("scripts.", ""), 'opponent_turn': opponent_turn})
                        wins += 1
                        break
                    elif(opponent_turn == "paper"):
                        continue
                    elif(opponent_turn == "scissors"):
                        losses += 1
                        results.append({'outcome': 'loss', 'player': script_title, 'player_turn': my_turn, 'opponent': opponent_script.__name__.replace("scripts.", ""), 'opponent_turn': opponent_turn})
                        break
                elif(my_turn == "scissors"):
                    if(opponent_turn == "rock"):
                        losses += 1
                        results.append({'outcome': 'loss', 'player': script_title, 'player_turn': my_turn, 'opponent': opponent_script.__name__.replace("scripts.", ""), 'opponent_turn': opponent_turn})
                        break
                    elif(opponent_turn == "paper"):
                        wins += 1
                        results.append({'outcome': 'win', 'player': script_title, 'player_turn': my_turn, 'opponent': opponent_script.__name__.replace("scripts.", ""), 'opponent_turn': opponent_turn})
                        break
                    elif(opponent_turn == "scissors"):
                        continue
                
            else:
                draws += 1
                results.append({'outcome': 'draw', 'player': script_title, 'player_turn': my_turn, 'opponent': opponent_script.__name__.replace("scripts.", ""), 'opponent_turn': opponent_turn})
                

        
    print("Script: {}, Wins: {}, Losses: {}, Draws: {}".format(script_title, wins, losses, draws))
    return wins, losses, draws, results
                
app.run()