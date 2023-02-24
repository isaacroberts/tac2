from flask import Flask
from flask import render_template
from flask import request
from flask import send_from_directory


from flask_cors import CORS


import os
import sync_manager


# template_dir = os.path.abspath('./web/')
# template_dir = 'web/'
app = Flask(__name__)
# app = Flask(__name__, template_folder='web/')
CORS(app, resources={r"*": {"origins": "*"}})


FLUTTER_WEB_APP = 'templates'

syncer = sync_manager.Syncer()


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

def get_id(request):
    if request.method=='GET':
        return 1
    elif request.method=='POST':
        try:
            return request.form['id']
        except:
            return 2
    return 1


@app.route('/connect', methods=[ 'GET', 'POST'])
def connect():
    return syncer.connect(get_id(request))

@app.route('/getupdate', methods=[ 'GET', 'POST'])
def getupdate():
    return syncer.get_full_update(get_id(request))


@app.route('/move', methods=['POST'])
def move():
    # print('move request:',request)
    sxs = False

    updates = ['rejected', 'unknown error']

    try:
        if request.method=='GET':
            bx = request.args.get('bx')
            by = request.args.get('by')
            sx = request.args.get('sx')
            sy = request.args.get('sy')
            sxs = True
        elif request.method=='POST':
            bx = request.form['bx']
            by = request.form['by']
            sx = request.form['sx']
            sy = request.form['sy']
            sxs = True

    except:
        # print('except')
        updates = ['rejected', 'parameters invalid']

    if sxs:
        try:
            lm = [int(bx), int(by), int(sx), int(sy)]
        except:
            updates = ['rejected', 'invalid integers']
            sxs = False

    if sxs:
        return syncer.move(get_id(request), [bx,by,sx, sy])

    return updates





@app.route('/poll', methods=['GET', 'POST'])
def poll():
    return syncer.poll(get_id(request))


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    return syncer.reset(get_id(request))


@app.route('/yourturn', methods=['GET', 'POST'])
def yourturn():
    # print(request.form);
    isP1 = request.form['p1']=='true'
    # print ('isP1:',isP1)
    resp= game.get_next_move(isP1)
    print('response:', resp)
    return resp


@app.route('/modcmd/<cmd>', methods=['GET', 'POST'])
def changing_cmd(cmd):
    return syncer.changing_cmd(get_id(request), cmd, request)
    # return game.win()

@app.route('/staticcmd/<cmd>', methods=['GET', 'POST'])
def static_cmd(cmd):
    return syncer.nochange_cmd(get_id(request), cmd, request)

if __name__ == '__main__':
    print('running');
    app.debug = False
    app.run() #go to http://localhost:5000/ to view the page.
