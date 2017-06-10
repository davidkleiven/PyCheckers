import piece as pc
import numpy as np
import neuralNetwork as nn

class Player:
    def __init__( self ):
        self.name = "NN"
        self.pieces = []
        self.color = "white"
        self.movePolicy = RandomMover( self.pieces )
        self.winner = False

    def setHumanUser( self ):
        self.movePolicy = HumanUser(self.pieces)

    def setNeuralNetwork( self, network, game ):
        self.movePolicy = CleverMover( self.pieces, network, game )

class MovePolicy():
    def __init__( self, pieces ):
        self.state = "OK"
        self.pieces = pieces

    def getMove( self ):
        raise NotImplementedError( "Childs have to implement this function!" )

    def checkForAvailableMoves( self ):
        moves = []
        for piece in self.pieces:
            moves, tree = piece.validMoves()
            if ( len(moves) > 0 ):
                return
        self.state = "noAvailableMoves"

class RandomMover(MovePolicy):
    def __init__( self, pieces ):
        super().__init__(pieces)
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
        self.state = "noAvailableMoves"
        return None,[],None

class HumanUser(MovePolicy):
    def __init__( self, pieces ):
        super().__init__(pieces)
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
        self.playerToMove = self.p2
        self.maxTurns = 1000
        self.numberOfTurns = 0

        # Keep track of the last moves performed
        self.pieceMoved = None
        self.piecesRemoved = []
        self.movedFrom = []
        self.newKing = None

        self.state = "playing"

    def printResult( self ):
        if ( self.p1.winner ):
            print ("Player: %s won"%(self.p1.name))
        elif ( self.p2.winner ):
            print ("Player: %s won"%(self.p2.name) )
        else:
            print ("Ended with draw!")

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
        self.numberOfTurns += 1
        piece, newmove, catchTree = self.playerToMove.movePolicy.getMove()
        if ( self.playerToMove.movePolicy.state == "noAvailableMoves" ):
            if ( self.playerToMove == self.p1 ):
                self.p2.winner = True
            else:
                self.p1.winner = True
            self.state = "finished"
            return

        self.move( piece, newmove, catchTree )

        if ( isinstance(self.playerToMove.movePolicy, HumanUser) ):
            self.playerToMove.movePolicy.selectedPiece = None
            self.playerToMove.movePolicy.newPosition = None

        self.playerToMove.movePolicy.checkForAvailableMoves()

        if ( self.playerToMove == self.p1 ):
            self.playerToMove = self.p2
        else:
            self.playerToMove = self.p1

        if ( len(self.playerToMove.pieces) == 0 ):
            self.state = "finished"
            if ( self.playerToMove == self.p1 ):
                self.p2.winner = True
            else:
                self.p1.winner = True
        if ( self.numberOfTurns >= self.maxTurns ):
            self.state = "finished"

    def undoMove( self ):
        newEmptyPiece = pc.Piece()
        newEmptyPiece.x = self.pieceMoved.x
        newEmptyPiece.y = self.pieceMoved.y
        self.pieceMoved.x = self.movedFrom[0]
        self.pieceMoved.y = self.movedFrom[1]
        pc.Piece.board.setPiece( self.pieceMoved )
        pc.Piece.board.setPiece( newEmptyPiece )

        if ( self.playerToMove == self.p1 ):
            playerLosingPiece = self.p2
        else:
            playerLosingPiece = self.p1

        if ( not self.newKing is None ):
            self.playerToMove.pieces.remove(self.newKing)
            self.newKing = None
            self.playerToMove.pieces.append(self.pieceMoved)

        for piece in self.piecesRemoved:
            playerLosingPiece.pieces.append(piece)
            pc.Piece.board.setPiece(piece)

        pc.Piece.board.checkConsistency( self.p1 )
        pc.Piece.board.checkConsistency( self.p2 )

    def move( self, pieceToMove, newPosition, catchTree ):
        self.newKing = None
        if ( pieceToMove is None ):
            return
        valid, tree = pieceToMove.validMoves()
        if ( not newPosition in valid ):
            print (newPosition)
            print (pieceToMove.name, pieceToMove.color, pieceToMove.x, pieceToMove.y )
            print (pc.Piece.board.getPiece(pieceToMove.x,pieceToMove.y))
            pc.Piece.board.save("boardError.csv")
            print ("The suggested move is not valid!")
            exit()
            return
        pieceCaptured = np.abs( newPosition[1] - pieceToMove.y ) > 1
        self.movedFrom = [pieceToMove.x,pieceToMove.y]
        self.pieceMoved = pieceToMove
        self.piecesRemoved = []

        if ( pieceCaptured ):
            moves = catchTree.getPath( newPosition[0], newPosition[1] )
            for i in range(0,len(moves)-1):
                middleX = int( (moves[i][0]+moves[i+1][0])/2 )
                middleY = int( (moves[i][1]+moves[i+1][1])/2 )
                newEmptyPiece = pc.Piece()
                newEmptyPiece.x = middleX
                newEmptyPiece.y = middleY
                pieceToRemove = pc.Piece.board.getPiece(middleX,middleY)
                self.piecesRemoved.append(pieceToRemove)
                if ( pieceToRemove.name == "empty" or pieceToRemove.color == pieceToMove.color ):
                    print ("==== ERROR INFORMATION ======")
                    print (moves)
                    print (pieceToRemove.x, pieceToRemove.y )
                    print (pieceToMove.x, pieceToMove.y )
                    print (pieceToMove.color, pieceToRemove.color )
                    print (pieceToMove.name, pieceToMove.name )
                    pc.Piece.board.save( "boardError.csv" )
                    print ("Abort! Error when removing piece")
                    exit()
                try:
                    if ( self.playerToMove == self.p1 ):
                        self.p2.pieces.remove( pieceToRemove )
                    else:
                        self.p1.pieces.remove( pieceToRemove )
                except Exception as exc:
                    print (pieceToRemove.name, pieceToRemove.color, pieceToRemove.x, pieceToRemove.y )
                    print (pieceToMove.name, pieceToMove.color, pieceToMove.x, pieceToMove.y )
                    pc.Piece.board.save( "Last board before error")
                    raise exc
                pc.Piece.board.setPiece( newEmptyPiece )

        copy = pc.Piece.board.getPiece( newPosition[0], newPosition[1] )
        copy.x = pieceToMove.x
        copy.y = pieceToMove.y
        pieceToMove.x = newPosition[0]
        pieceToMove.y = newPosition[1]
        pc.Piece.board.setPiece( pieceToMove )
        pc.Piece.board.setPiece( copy )
        #pc.Piece.board.save("lastState.csv")

        if ( pieceToMove.color == "white" and newPosition[1] == 7 and pieceToMove.name != "king" ):
            self.playerToMove.pieces.remove(pieceToMove)
            newKing = pc.King()
            newKing.color = "white"
            newKing.x = newPosition[0]
            newKing.y = newPosition[1]
            self.playerToMove.pieces.append(newKing)
            self.newKing = newKing
            pc.Piece.board.setPiece(newKing)
        elif ( pieceToMove.color == "black" and newPosition[1] == 0 and pieceToMove.name != "king" ):
            self.playerToMove.pieces.remove(pieceToMove)
            newKing = pc.King()
            newKing.color = "black"
            newKing.x = newPosition[0]
            newKing.y = newPosition[1]
            self.playerToMove.pieces.append( newKing )
            self.newKing = newKing
            pc.Piece.board.setPiece(newKing)

class CleverMover(MovePolicy):
    def __init__(self, pieces, network, game ):
        super().__init__(pieces)
        self.network = network
        self.game = game
        self.selectedPiece = None
        self.newPosition = None

    def boardToInputState( self ):
        inputState = np.zeros(5*64)
        for i in range(0,8):
            for j in range(0,8):
                indx = i*8+j
                piece = pc.Piece.board.getPiece(i,j)
                if ( piece.name == "empty" ):
                    inputState[indx] = 1.0
                elif ( piece.name == "man" and piece.color == "white" ):
                    inputState[indx+1] = 1.0
                elif ( piece.name == "king" and piece.color == "white" ):
                    inputState[indx+2] = 1.0
                elif ( piece.name == "man" and piece.color == "black" ):
                    inputState[indx+3] = 1.0
                elif ( piece.name == "king" and piece.color == "black" ):
                    inputState[indx+4] = 1.0
                else:
                    raise Exception( "Error when converting the board to input state for the neural network")
        return inputState

    def getMove( self ):
        value = -np.inf
        selectedCatch = None
        foundMove = False
        for piece in self.pieces:
            valid, catchTree = piece.validMoves()
            for move in valid:
                self.game.move( piece, move, catchTree )
                inp = self.boardToInputState()
                newvalue = self.network.evaluate(inp)
                if ( newvalue > value ):
                    newvalue = value
                    self.selectedPiece = piece
                    self.newPosition = move
                    selectedCatch = catchTree
                    foundMove = True
                self.game.undoMove()
        if ( not foundMove ):
            self.state = "noAvailableMoves"
        return self.selectedPiece, self.newPosition, selectedCatch
