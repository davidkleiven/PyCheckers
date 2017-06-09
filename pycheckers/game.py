import piece as pc

class Player:
    def __init__( self ):
        self.name = "NN"
        self.pieces = []
        self.color = "white"

class Game:
    def __init__( self ):
        self.p1 = Player()
        self.p2 = Player()
        self.p1.name = "Player 1"
        self.p2.name = "Player 2"
        self.p1.color = "white"
        self.p2.color = "black"

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
            x = indx%8 - y%2
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

    def move( self, player, pieceToMove, newPosition ):
        if ( not newPosition in pieceToMove.validMoves() ):
            print ("The suggested move is not valid!")
            return

        pieceCaptured = math.abs( newPosition[1] - self.y ) > 1

        if ( pieceCaptured ):
            middleX = int( (newPosition[0]+self.x)/2 )
            middleY = int( (newPosition[1]+self.y)/2 )
            newEmptyPiece = Piece()
            newEmptyPiece.x = middleX
            newEmptyPiece.y = middleY
            if ( player == self.p1 ):
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
