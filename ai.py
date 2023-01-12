
import numpy as np


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


class NumPAI():

    EMPTY=0
    P1=-1
    P2=1
    TIE=-2
    PL=[0,1]

    LINES_LEN=2


    LINES_OS=0
    LINES_XS=1

    def __init__(self):
        #Array of angles
        self.angles=Angle()

        #lines & board_lines
        #3x3x2 structs of angle info
        #   [0]=ix
        #   [1]=active,1=active,0=off
        #   [2]=player,(-1,0,1)
        #   [3]=completion,(0-3)
        self.lines=np.zeros(shape=(3,3,8,self.LINES_LEN),dtype=int)
        #self.lines[:,:,:,self.LINES_IX] = range(8)
        #self.lines[:,:,:,self.LINES_ACTIVE]=  1
        #self.lines[:,:,:,self.LINES_PLAYER]= -1
        #self.lines[:,:,:,LINES_COMPLT]= 0

        #1 list of angle IDs
        self.board_lines=np.zeros(shape=(8,self.LINES_LEN),dtype=int)

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
        self.board=np.full(shape=(3,3,3,3),fill_value=self.EMPTY,dtype=int)
        #Array of states for each square
        self.hashStates=np.full(shape=(3,3),fill_value=self.EMPTY,dtype=int)


        self.last_update_move=[]

    def play(self,last_move,isP1):

        if last_move != self.last_update_move:
            lm=last_move
            player= self.P1 if isP1 else self.P2
            self.board[lm[0],lm[1],lm[2],lm[3]]=player
            win=self.updateAngles(last_move,player)

            self.last_update_move=last_move

            if win:
                self.hashStates[lm[0],lm[1]]=player
                self.update_board_angles()

            print(self.board)

        return '[0,0,0,1]'

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

        ax= (self.LINES_OS if player==self.P1 else self.LINES_XS)
        otherax=1-ax

        self.lines[hx,hy,isin,ax]+=1

        over=self.lines[hx,hy,:,otherax]>0
        over=np.logical_and(isin,over)

        self.lines[hx,hy,over,:]=-1

        won=np.any(self.lines[hx,hy,:,:]>=3)

        return won

    def allAngles(self):
        posXs=self.angles.poses[:,:,0]
        posYs=self.angles.poses[:,:,1]
        #3x3x8x3
        posPlayers=self.board[:,:,posXs,posYs]

        #Only useful for grandboard - represents ties
        done=np.any(posPlayers==self.TIE,axis=3,keepdims=True)[:,:,:,0]

        #Where there are x's and o's
        p1=np.any(posPlayers==self.P1,axis=3,keepdims=True)[:,:,:,0]
        p2=np.any(posPlayers==self.P2,axis=3,keepdims=True)[:,:,:,0]

        #Intersections of done are invalidated
        #done = (p1 and p2) or tie
        done=np.logical_or(done,np.logical_and(p1,p2))

        #p1=np.logical_and(p1,np.logical_not(done))
        #p2=np.logical_and(p2,np.logical_not(done))

        #self.lines[p1,self.LINES_PLAYER]=self.P1
        #self.lines[p2,self.LINES_PLAYER]=self.P2

        compP1=np.count_nonzero(posPlayers==self.P1,axis=3)
        compP2=np.count_nonzero(posPlayers==self.P2,axis=3)

        self.lines[p1,self.LINES_OS]=compP1[p1]
        self.lines[p2,self.LINES_XS]=compP2[p2]

        #Invalidate dones to overwrite p1/p2 intersecting
        self.lines[done,:]=-1

        print(self.lines)


    def update_board_angles(self):
        print ('-----Board Lines------')
        posXs=self.angles.poses[:,:,0]
        posYs=self.angles.poses[:,:,1]
        #8x3
        posPlayers=self.hashStates[posXs,posYs]

        #Only useful for grandboard - represents ties
        done=np.any(posPlayers==self.TIE,axis=1,keepdims=True)[:,0]

        #Where there are x's and o's
        p1=np.any(posPlayers==self.P1,axis=1,keepdims=True)[:,0]
        p2=np.any(posPlayers==self.P2,axis=1,keepdims=True)[:,0]

        #Intersections of done are invalidated
        #done = (p1 and p2) or tie
        done=np.logical_or(done,np.logical_and(p1,p2))

        #p1=np.logical_and(p1,np.logical_not(done))
        #p2=np.logical_and(p2,np.logical_not(done))

        #self.lines[p1,self.LINES_PLAYER]=self.P1
        #self.lines[p2,self.LINES_PLAYER]=self.P2

        compP1=np.count_nonzero(posPlayers==self.P1,axis=1)
        compP2=np.count_nonzero(posPlayers==self.P2,axis=1)

        self.board_lines[p1,self.LINES_OS]=compP1[p1]
        self.board_lines[p2,self.LINES_XS]=compP2[p2]

        #Invalidate dones to overwrite p1/p2 intersecting
        self.board_lines[done,:]=-1

        print(self.board_lines)



numpai=NumPAI()

moves=[[2,2,0,0],[2,2,1,0],[2,2,2,2],[2,2,0,1],[2,2,1,1],
    [0,0,0,0],[0,0,1,0],[0,0,2,2],[0,0,0,1],[0,0,1,1]]
p1=True
for m in moves:
    numpai.play(last_move=m,isP1=p1)
    p1=not p1
