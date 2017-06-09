import numpy as np
import pygame as pg

class MoveTree:
    def __init__( self ):
        self.entries = []

    def toList( self ):
        moves = []
        for i in range(1,len(self.entries)):
            moves.append( self.entries[i].move )
        return moves

class BinaryMoveTreeEntry:
    def __init__(self):
        self.left = None
        self.right = None
        self.parent = None
        self.move = []
        self.nTimesVisited = 0

class Board:
    def __init__(self):
        self.board = [[None]*8 for _ in range(8)]

    def getPiece( self, x, y ):
        assert( self.isInside(x,y) )
        return self.board[x][y]

    def setPiece( self, piece ):
        self.board[piece.x][piece.y] = piece

    def isInside( self, x, y ):
        return x >= 0 and x < 8 and y >= 0 and y < 8

    def printOut( self ):
        for i in range(0,8):
            for j in range(0,8):
                print (" %s "%(self.board[j][i].name), end="" )
            print ("\n")
        print ("--------------------------------------------------------------")

class Piece:
    board = Board() # All Pieces share the same board

    def __init__( self ):
        self.x = 0
        self.y = 0
        self.color = "white"
        self.name = "empty"

    def validMoves( self ):
        moves = []
        moves += self.validRegularMoves()
        moves += self.validCatchMoves()
        return moves

    def validRegularMoves( self ):
        raise NotImplementedError( "This function must be implemented by child" )

    def validCatchMoves( self ):
        raise NotImplementedError( "This function must be implemented by child" )

    def draw( self, screen, tilewidth, tileheight ):
        raise NotImplementedError( "The draw function should be implemented in child classes" )

class Man( Piece ):
    def __init__( self ):
        super().__init__()
        self.name = "man"
        self.guiRadiusInPx = 30

    def validRegularMoves( self ):
        """
        This function returns the valid move for the current piece
        It return a list of the form [[x1,y1],[x2,y2]] where (x1,y1) are
        the coordinates of the new move
        """
        moves = []
        x1 = self.x + 1
        if ( self.color == "white" ):
            y1 = self.y + 1
        else:
            y1 = self.y - 1

        if ( self.board.isInside(x1,y1) ):
            if ( self.board.getPiece(x1,y1).name == "empty" ):
                moves.append([x1,y1])

        x2 = self.x - 1
        if ( self.color == "white" ):
            y2 = self.y + 1
        else:
            y2 = self.y - 1

        if ( self.board.isInside(x2,y2) ):
            if ( self.board.getPiece(x2,y2).name == "empty" ):
                moves.append([x2,y2])
        return moves

    def validCatchMoves( self ):
        moves = []
        tree = MoveTree()
        rootMove = BinaryMoveTreeEntry()
        rootMove.move = [self.x,self.y]
        tree.entries.append(rootMove)

        current = rootMove
        while ( True ):
            current.nTimesVisited += 1
            # Check right of the current node
            if ( current.nTimesVisited == 1 ):
                newmove = self.findCatchMove( current.move[0], current.move[1], True )
                if ( len(newmove) > 0 ):
                    newEntry = BinaryMoveTreeEntry()
                    newEntry.move = newmove
                    newEntry.parent = current
                    current.right = newEntry
                    current = newEntry
                    tree.entries.append(current)
                    continue

            # Check left node
            if ( current.nTimesVisited == 2 or current.nTimesVisited == 1 ):
                print ("here")
                newmove = self.findCatchMove( current.move[0], current.move[1], False )
                if ( len(newmove) > 0 ):
                    newEntry = BinaryMoveTreeEntry()
                    newEntry.move = newmove
                    newEntry.parent = current
                    current.left = newEntry
                    current = newEntry
                    tree.entries.append(current)
                    continue

            # If it enters here go back to parent
            current = current.parent
            if ( current is None ):
                break
            if ( current == rootMove and rootMove.nTimesVisited == 3 ):
                break
        return tree.toList()


    def findCatchMove( self, x, y, checkRight ):
        if ( checkRight ):
            x1 = x+1
        else:
            x1 = x-1

        if ( self.color == "white" ):
            y1 = y+1
        else:
            y1 = y-1

        if ( self.board.isInside(x1,y1) and self.board.getPiece(x1,y1).name != "empty" and
        self.board.getPiece(x1,y1).color != self.color ):
            if ( checkRight ):
                x2 = x1+1
            else:
                x2 = x1-1
            if ( self.color == "white" ):
                y2 = y1+1
            else:
                y2 = y1-1
            if ( self.board.isInside(x2,y2) and self.board.getPiece(x2,y2).name == "empty" ):
                return [x2,y2]
        return []


    def draw( self, screen, tilewidth, tileheight ):
        """
        This function draws a graphical representation on the screen
        """
        if ( self.color == "white" ):
            color = (255,255,255)
        else:
            color = (0,0,0)
        xPx = int( self.x*tilewidth+tilewidth/2.0 )
        yPx = int( self.y*tileheight+tileheight/2.0 )
        pg.draw.circle( screen, color, (xPx,yPx), self.guiRadiusInPx, 0 )
