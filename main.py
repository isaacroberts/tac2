from flask import Flask
from flask import render_template
from flask import request
from flask import send_from_directory


from flask_cors import CORS


import os
import game_manager



# template_dir = os.path.abspath('./web/')
# template_dir = 'web/'
app = Flask(__name__)
# app = Flask(__name__, template_folder='web/')
CORS(app, resources={r"*": {"origins": "*"}})


FLUTTER_WEB_APP = 'templates'


@app.route('/')
def render_page():
    return render_template('index.html')


@app.route('/web/')
def render_page_web():
    return render_template('index.html')



@app.route('/web/<path:name>')
def return_flutter_doc(name):

    datalist = str(name).split('/')
    DIR_NAME = FLUTTER_WEB_APP

    if len(datalist) > 1:
        for i in range(0, len(datalist) - 1):
            DIR_NAME += '/' + datalist[i]

    return send_from_directory(DIR_NAME, datalist[-1])

game = game_manager.Game()


@app.route('/connect', methods=[ 'GET', 'POST'])
def connect():
    return game.get_full_update()


@app.route('/move', methods=['POST'])
def move():
    print('move request:',request)

    sxs = False

    updates = ['rejected', 'unknown error']

    try:
        if request.method=='GET':
            bx = request.args.get('bx')
            bx = request.args.get('bx')
            bx = request.args.get('bx')
            bx = request.args.get('bx')
            sxs = True

        elif request.method=='POST':
            print('post')
            print ('form :' , request.form)
            bx = request.form['bx']
            by = request.form['by']
            sx = request.form['sx']
            sy = request.form['sy']
            sxs = True

    except:
        print('except')
        updates = ['rejected', 'parameters invalid']

    if sxs:
        try:
            lm = [int(bx), int(by), int(sx), int(sy)]
        except:
            updates = ['rejected', 'invalid integers']
            sxs = False

    if sxs:
        updates = game.set_move(lm, True)

    print ('updates: ',updates)
    return updates
    # return f"[{', '.join(updates)}]"



@app.route('/reset', methods=['GET', 'POST'])
def reset():
    global game
    game = game_manager.Game()
    return 'confirmed'


@app.route('/win', methods=['GET', 'POST'])
def win():
    return game.win()


@app.route('/yourturn', methods=['GET', 'POST'])
def yourturn():
    # print(request.form);
    isP1 = request.form['p1']=='true'
    # print ('isP1:',isP1)
    resp= game.get_next_move(isP1)
    print('response:', resp)
    return resp


if __name__ == '__main__':
    print('running');
    app.debug = False
    app.run() #go to http://localhost:5000/ to view the page.
