import math
import pygame as pg

class Board:
    def __init__(self):
        self.board = [[None]*8]*8

    def getPiece( self, x, y ):
        assert( x < 8 and y < 8 and x >= 0 and y >= 0 )
        return self.board[x][y]

    def setPiece( self, piece ):
        self.board[piece.x][piece.y] = piece

class Piece:
    board = Board() # All Pieces share the same board

    def __init__( self ):
        self.x = 0
        self.y = 0
        self.color = "white"
        self.name = "empty"

    def validMoves( self ):
        raise NotImplementedError( "This function should be implemented in child classes" )

    def draw( self, screen, tilewidth, tileheight ):
        raise NotImplementedError( "The draw function should be implemented in child classes" )

class Man( Piece ):
    def __init__( self ):
        Piece.__init__( self )
        self.name = "man"
        self.guiRadiusInPx = 30

    def validMoves( self ):
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

        if ( x1 < 8 and y1 < 8 and y1 >= 0 ):
            if ( self.board.getPiece(x1,y1).name == "empty" ):
                moves.append([x1,y1])
            elif ( self.board.getPiece(x1,y1).color != self.color ):
                x1 += 1
                if ( self.color == "white" ):
                    y1 += 1
                else:
                    y1 -= 1
                if ( x1 < 8 and y1 < 8 and y1 >= 0 ):
                    if ( self.board.getPiece(x1,y1).name == "empty" ):
                        moves.append([x1,y1])

        x2 = self.x - 1
        if ( self.color == "white" ):
            y2 = self.y + 1
        else:
            y2 = self.y - 1

        if ( x2 >= 0 and y2 < 8 and y2 >= 0 ):
            if ( self.board.getPiece(x2,y2).name == "empty" ):
                moves.append([x2,y2])
            elif ( self.board.getPiece(x2,y2).color != self.color ):
                x2 -= 1
                if ( self.color == "white" ):
                    y2 += 1
                else:
                    y2 -= 1
                if ( x2 >= 0 and y2 < 8 and y2 >= 0 ):
                    if ( self.board.getPiece(x2,y2).name == "empty" ):
                        moves.append([x2,y2])
        return moves

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
