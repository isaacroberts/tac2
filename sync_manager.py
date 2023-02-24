

import game_manager

import sqlite3

conn = sqlite3.connect('tac2.db')

class Syncer:

    def __init__(self):

        self.game = game_manager.Game()


    def addstate(self, l):
        # l.insert(0, ['state', self.cur_state])
        if l is list:
            return {'state':self.cur_state, 'response':l}
        elif l is dict:
            l['state'] = self.cur_state
        else:
            return {'state':self.cur_state, 'data': l}


    def poll(self, id):
        return {'state': self.cur_state}

    def connect(self, id):
        query = f"INSERT INTO player(name) VALUES {id}"
        cursor = conn.cursor()
        cursor.execute(query)

        conn.commit()

        user_id = cursor.lastrowid()
        cursor.close()
        

        self.cur_state+=1
        d = self.addstate(self.game.get_full_update())
        d['yourP'] = 1
        return d

    def get_full_update(self, id):
        return self.addstate(self.game.get_full_update())


    def move(self, id, move):
        self.cur_state+=1
        resp = self.game.set_move(move[0], move[1], move[2], move[3])
        return self.addstate(resp)

    def failresponse(self, id, reason):

        return self.addstate(resp)

    def yourturn(self, id, isP1):
        self.cur_state+=1
        # print ('isP1:',isP1)
        resp= game.get_next_move(isP1)
        # print('response:', resp)
        return self.addstate(resp)


    def reset(self, id):
        self.cur_state+=1
        self.game = game_manager.Game()
        # return 'confirmed'
        return self.poll(id)

    def changing_cmd(self, id, cmd, request):
        self.cur_state+=1
        return []

    def nochange_cmd(self, id, cmd, request):
        return []
