import piece as pc
import numpy as np

class Player:
    def __init__( self ):
        self.name = "NN"
        self.pieces = []
        self.color = "white"
        self.movePolicy = RandomMover( self.pieces )

    def setHumanUser( self ):
        self.movePolicy = HumanUser(self.pieces)

class RandomMover:
    def __init__( self, pieces ):
        self.pieces = pieces
        pass

    def getMove( self ):
        maxIter = 1000
        for i in range(0,maxIter):
            pieceIndx = np.random.randint(0, high=len(self.pieces) )
            validMoves, catchTree = self.pieces[pieceIndx].validMoves()
            if ( len(validMoves) == 0 ):
                continue
            moveIndx = np.random.randint(0,high=len(validMoves))
            return self.pieces[pieceIndx], validMoves[moveIndx], catchTree
        raise Exception( "Could not find a valid move in %d attempts..."%(maxIter))

class HumanUser:
    def __init__( self, pieces ):
        self.pieces = pieces
        self.selectedPiece = None
        self.newPosition = None
        self.catchTree = None

    def selectPiece( self, x, y ):
        for piece in self.pieces:
            if ( piece.x == x ) and ( piece.y == y ):
                self.selectedPiece = piece

    def selecteNewPosition( self, x, y ):
        if ( self.selectedPiece is None ):
            return
        valid, self.catchTree = self.selectedPiece.validMoves()
        if ( [x,y] in valid ):
            self.newPosition = [x,y]

    def getMove( self ):
        if ( self.selectedPiece is None ):
            raise Exception( "No piece is selected!" )
        if ( self.newPosition is None ):
            raise Exception("No new position is selected!")
        return self.selectedPiece, self.newPosition, self.catchTree

class Game:
    def __init__( self ):
        self.p1 = Player()
        self.p2 = Player()
        self.p1.name = "Player 1"
        self.p2.name = "Player 2"
        self.p1.color = "white"
        self.p2.color = "black"
        self.playerToMove = self.p1

        # Keep track of the last moves performed
        self.lastFrom = [0]*2
        self.lastTo = [0]*2

    def setupGame( self ):
        # Fill board with empty
        for i in range(0,8):
            for j in range(0,8):
                newpiece = pc.Piece()
                newpiece.x = i
                newpiece.y = j
                pc.Piece.board.setPiece( newpiece )

        # Create the pieces of player 1 and player 2
        # Each has 4*3 = 12 pieces
        for i in range(0,12):
            indx = 2*i
            y = int(indx/8)
            x = indx%8 + y%2
            self.p1.pieces.append( pc.Man() )
            self.p1.pieces[-1].x = x
            self.p1.pieces[-1].y = y
            self.p1.pieces[-1].color = "white"


            y = 7-int(indx/8)
            x = (indx+1)%8 - int(indx/8)%2
            self.p2.pieces.append( pc.Man() )
            self.p2.pieces[-1].x = x
            self.p2.pieces[-1].y = y
            self.p2.pieces[-1].color = "black"

            # Put pieces on the board
            pc.Piece.board.setPiece( self.p1.pieces[-1] )
            pc.Piece.board.setPiece( self.p2.pieces[-1] )
            #pc.Piece.board.printOut()

        #pc.Piece.board.printOut()

    def stepGame( self ):
        piece, newmove, catchTree = self.playerToMove.movePolicy.getMove()
        self.move( piece, newmove, catchTree )

        if ( isinstance(self.playerToMove.movePolicy, HumanUser) ):
            self.playerToMove.movePolicy.selectedPiece = None
            self.playerToMove.movePolicy.newPosition = None

        if ( self.playerToMove == self.p1 ):
            self.playerToMove = self.p2
        else:
            self.playerToMove = self.p1

        if ( len(self.playerToMove.pieces) == 0 ):
            print ("GAME OVER!")

    def move( self, pieceToMove, newPosition, catchTree ):
        valid, tree = pieceToMove.validMoves()
        if ( not newPosition in valid ):
            print ("The suggested move is not valid!")
            return
        pieceCaptured = np.abs( newPosition[1] - pieceToMove.y ) > 1
        lastFrom = [ pieceToMove.x, pieceToMove.y ]
        lastTo = newPosition

        if ( pieceCaptured ):
            moves = catchTree.getPath( newPosition[0], newPosition[1] )
            print (moves)
            for i in range(0,len(moves)-1):
                middleX = int( (moves[i][0]+moves[i+1][0])/2 )
                middleY = int( (moves[i][1]+moves[i+1][1])/2 )
                newEmptyPiece = pc.Piece()
                newEmptyPiece.x = middleX
                newEmptyPiece.y = middleY
                if ( self.playerToMove == self.p1 ):
                    self.p2.pieces.remove( pc.Piece.board.getPiece(middleX,middleY) )
                else:
                    self.p1.pieces.remove( pc.Piece.board.getPiece(middleX,middleY) )
                pc.Piece.board.setPiece( newEmptyPiece )

        copy = pc.Piece.board.getPiece( newPosition[0], newPosition[1] )
        copy.x = pieceToMove.x
        copy.y = pieceToMove.y
        pieceToMove.x = newPosition[0]
        pieceToMove.y = newPosition[1]
        pc.Piece.board.setPiece( pieceToMove )
        pc.Piece.board.setPiece( copy )

        if ( pieceToMove.color == "white" and newPosition[1] == 7 ):
            self.playerToMove.pieces.remove(pieceToMove)
            newKing = pc.King()
            newKing.color = "white"
            newKing.x = newPosition[0]
            newKing.y = newPosition[1]
            self.playerToMove.pieces.append(newKing)
        elif ( pieceToMove.color == "black" and newPosition[1] == 0 ):
            self.playerToMove.pieces.remove(pieceToMove)
            newKing = pc.King()
            newKing.color = "black"
            newKing.x = newPosition[0]
            newKing.y = newPosition[1]
            self.playerToMove.pieces.append( newKing )
