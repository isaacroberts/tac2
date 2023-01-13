import numpy as np
from scipy.stats import norm

class Angle():
    def __init__(self):
        #Unicode strings to display which angle
        self.strings=np.array(["\u22a6","|","\u2ade","\u2adf","–","\u2ae0","\\","/"])

        # Angle_amt * 3 spots * (x,y)
        self.poses=np.zeros(shape=(8,3,2),dtype=int)

        for n in range(3):
            for m in range(3):
              self.poses[n,m,:]=[n,m]

        for n in range(3):
            for m in range(3):
                self.poses[n+3,m,:]=[m,n]

        self.poses[6,:,:]=np.arange(3).reshape(-1,1)
        self.poses[7,:,0]=np.arange(3)
        self.poses[7,:,1]=np.arange(2,-1,-1)

class Coord():
    def __init__(self,hx=0,hy=0,sx=0,sy=0):
        self.hx=hx
        self.hy=hy
        self.sx=sx
        self.sy=sy


EMPTY=0
P1=1
P2=2
TIE=3
PL=[0,1]

P1K = '1'
P2K = '2'
TIK = 'T'

LINES_LEN=2


LINES_OS=0
LINES_XS=1


class Game:


    def __init__(self):
        #Array of angles
        self.angles=Angle()

        #lines & board_lines
        #3x3x2 structs of angle info
        #   [0]=ix
        #   [1]=active,1=active,0=off
        #   [2]=player,(-1,0,1)
        #   [3]=completion,(0-3)
        self.lines=np.zeros(shape=(3,3,8,LINES_LEN),dtype=int)
        #self.lines[:,:,:,self.LINES_IX] = range(8)
        #self.lines[:,:,:,self.LINES_ACTIVE]=  1
        #self.lines[:,:,:,self.LINES_PLAYER]= -1
        #self.lines[:,:,:,LINES_COMPLT]= 0

        #1 list of angle IDs
        self.board_lines=np.zeros(shape=(8,LINES_LEN),dtype=int)

        #self.board_lines[:,:,:,self.LINES_IX] = range(8)
        #self.board_lines[:,:,:,self.LINES_ACTIVE]=  1
        #self.board_lines[:,:,:,self.LINES_PLAYER]= -1


        #Square values
        self.values=np.zeros(shape=(3,3,3,3,2))
        #Highest value - ie max convolution of values
        self.highest=np.zeros(shape=(3,3,2))
        #Values of squares
        self.hash_values=np.zeros(shape=(3,3,2))
        #Array of ints for each square
        self.board=np.full(shape=(3,3,3,3),fill_value=EMPTY,dtype=int)
        #Array of states for each square
        self.hashStates=np.full(shape=(3,3),fill_value=EMPTY,dtype=int)

        self.movable= None
        self.winner = EMPTY

        self.last_update_move=[]

    def set_move(self, move, isP1):
        responses = []

        # print('set: ', isP1)

        if move != self.last_update_move:
            lm=move
            player = P1 if isP1 else P2
            if (self.board[lm[0],lm[1],lm[2],lm[3]]==EMPTY):
                # print ('player:', player, 'isP1', isP1,'p1, p2:', P1, P2, 'phrase:', P1 if isP1 else P2, type(isP1))
                responses.append(['square', lm[0],lm[1],lm[2],lm[3], player])
                self.board[lm[0],lm[1],lm[2],lm[3]]=player


                hashWinner=self.updateAngles(move, player)
                winner = None
                if hashWinner is not None:
                    responses.append(['hashtaken', lm[0], lm[1], hashWinner])
                    winner = self.update_board_angles()
                    if winner is not None:
                        responses.append(['gamewon', winner])

                if winner is None:
                    if self.hashStates[lm[2], lm[3]] == EMPTY:
                        self.movable = (lm[2], lm[3])
                        responses.append(['focus', lm[2], lm[3]])
                    else:
                        self.movable= None
                        responses.append(['openboard'])

            else:
                responses.append(['rejected', 'Square full'])

        return responses

    def player_code_to_key(p):
        if p==P1:
            return P1K
        if p==P2:
            return P2K
        if p==TIE:
            return TIK
        return '?'

    def get_next_move(self,isP1):

        if self.winner!=EMPTY:
            return {'responses': ['gamewon', Game.player_code_to_key(self.winner)], 'delay':0}

        avail = []

        if self.movable is None:
            ixes = np.argwhere(self.board == EMPTY)

            ixes = [i for i in ixes if self.hashStates[i[0]][i[1]]==EMPTY]
            ixes = np.array(ixes)
        else:
            hx, hy = self.movable
            ixes = np.argwhere(self.board[hx, hy] == EMPTY)

        # print (ixes)

        chAmt = ixes.shape[0]

        if chAmt == 0:
            print ('Err: no choices?')
            return

        ch = np.random.randint(chAmt)

        # print ('Moving', ixes[ch])
        move = ixes[ch]
        if len(move)==2:
            move = [hx, hy, move[0], move[1]]

        move = [int(x) for x in move]
        # delay = 200 + np.random.randint(500)

        xr = np.random.sample()
        delay = norm.cdf((xr*2-1)*3)*1000
        delay = 10+int(delay)

        resp =  self.set_move(move, isP1)
        return {'responses': resp, 'delay':delay}

    def win(self):
        self.winner = P1
        return [['gamewon', P1K]]


    def get_full_update(self):
        responses = []

        ixes = np.argwhere(self.board != EMPTY)

        for ix in ixes:
            r = ['square']
            for i in ix:
                r.append(int(i))
            r.append(int(self.board[ix[0], ix[1], ix[2], ix[3]]))
            responses.append(r)


        for hx in range(3):
            for hy in range(3):
                if self.hashStates[hx, hy]!= EMPTY:
                    responses.append(['hashtaken', int(hx), int(hy), Game.player_code_to_key(self.hashStates[hx, hy])])


        if self.winner != EMPTY:
            responses.append(['gamewon', Game.player_code_to_key(self.winner)])

        else:
            if self.movable is None:
                responses.append(['openboard'])
            else:
                responses.append(['focus', self.movable[0], self.movable[1]])

        return responses

    def updateAngles(self,lastMove,player):
        hx=lastMove[0]
        hy=lastMove[1]
        #8x2
        hash=self.lines[hx,hy,:,:]
        #2
        coords=np.array([lastMove[2],lastMove[3]])

        #8x3
        matchX=self.angles.poses[:,:,0]==coords[0]
        matchY=self.angles.poses[:,:,1]==coords[1]
        #8 angles x 3 possible positions
        #Isin = (x&y).any along pose axis
        isin=np.logical_and(matchX,matchY).any(axis=1)

        ax= (LINES_OS if player==P1 else LINES_XS)
        otherax=1-ax

        self.lines[hx,hy,isin,ax]+=1

        over=self.lines[hx,hy,:,otherax]>0
        over=np.logical_and(isin,over)

        self.lines[hx,hy,over,:]=-1

        if np.any(self.lines[hx,hy,:,LINES_OS]>=3):
            self.hashStates[hx, hy]=P1
            return P1K
        elif np.any(self.lines[hx,hy,:,LINES_XS]>=3):
            self.hashStates[hx, hy]=P2
            return P2K
        elif (self.board[hx, hy]!=EMPTY).all():
            self.hashStates[hx, hy]=TIE
            return TIK

        return None

    def allAngles(self):
        posXs=self.angles.poses[:,:,0]
        posYs=self.angles.poses[:,:,1]
        #3x3x8x3
        posPlayers=self.board[:,:,posXs,posYs]

        #Only useful for grandboard - represents ties
        done=np.any(posPlayers==TIE,axis=3,keepdims=True)[:,:,:,0]

        #Where there are x's and o's
        p1=np.any(posPlayers==P1,axis=3,keepdims=True)[:,:,:,0]
        p2=np.any(posPlayers==P2,axis=3,keepdims=True)[:,:,:,0]

        #Intersections of done are invalidated
        #done = (p1 and p2) or tie
        done=np.logical_or(done,np.logical_and(p1,p2))

        #p1=np.logical_and(p1,np.logical_not(done))
        #p2=np.logical_and(p2,np.logical_not(done))

        #self.lines[p1,self.LINES_PLAYER]=self.P1
        #self.lines[p2,self.LINES_PLAYER]=self.P2

        compP1=np.count_nonzero(posPlayers==P1,axis=3)
        compP2=np.count_nonzero(posPlayers==P2,axis=3)

        self.lines[p1,LINES_OS]=compP1[p1]
        self.lines[p2,LINES_XS]=compP2[p2]

        #Invalidate dones to overwrite p1/p2 intersecting
        self.lines[done,:]=-1

        # print(self.lines)


    def update_board_angles(self):
        # print ('-----Board Lines------')
        posXs=self.angles.poses[:,:,0]
        posYs=self.angles.poses[:,:,1]
        #8x3
        posPlayers=self.hashStates[posXs,posYs]

        #Only useful for grandboard - represents ties
        done=np.any(posPlayers==TIE,axis=1,keepdims=True)[:,0]

        #Where there are x's and o's
        p1=np.any(posPlayers==P1,axis=1,keepdims=True)[:,0]
        p2=np.any(posPlayers==P2,axis=1,keepdims=True)[:,0]

        #Intersections of done are invalidated
        #done = (p1 and p2) or tie
        done=np.logical_or(done,np.logical_and(p1,p2))

        #p1=np.logical_and(p1,np.logical_not(done))
        #p2=np.logical_and(p2,np.logical_not(done))

        #self.lines[p1,self.LINES_PLAYER]=self.P1
        #self.lines[p2,self.LINES_PLAYER]=self.P2

        compP1=np.count_nonzero(posPlayers==P1,axis=1)
        compP2=np.count_nonzero(posPlayers==P2,axis=1)

        self.board_lines[p1,LINES_OS]=compP1[p1]
        self.board_lines[p2,LINES_XS]=compP2[p2]

        #Invalidate dones to overwrite p1/p2 intersecting
        self.board_lines[done,:]=-1

        # print(self.board_lines)

        if (self.board_lines[:,LINES_OS]>=3).any():
            self.winner = P1
            return P1K
        elif (self.board_lines[:,LINES_XS]>=3).any():
            self.winner = P2
            return P2K
        elif (self.hashStates!=EMPTY).all():
            self.winner = TIE
            return TIK

        return None
