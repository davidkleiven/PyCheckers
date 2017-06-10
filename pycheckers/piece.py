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

    def clean( self ):
        for entry in self.entries:
            entry.nTimesVisited = 0

class QuarticMoveTree(MoveTree):
    def __init__( self ):
        super().__init__()

    def clean( self ):
        for entry in self.entries:
            entry.checked = [False,False,False,False]
    def isInSearchTree( self, newmove ):
        for entry in self.entries:
            if ( newmove == entry.move ):
                return True
        return False

    def getPath( self, x, y ):
        moves = []
        current = self.entries[0]
        self.clean()
        #moves.append(current.move)
        maxIter = 1000
        counter = 0
        while ( True ):
            counter += 1
            if ( counter >= maxIter ):
                raise Exception("Infinite loop when searching for path in quartic move tree")

            proceedToNextLevel = False
            print (current)
            for i in range(0,4):
                if ( not current.checked[i] ):
                    current.checked[i] = True
                    moves.append(current.move)
                    if ( moves[-1][0] == x and moves[-1][1] == y ):
                        return moves
                    if ( current.branches[i] is None ):
                        del moves[-1]
                    else:
                        current = current.branches[i]
                        proceedToNextLevel = True
                        break
            if ( proceedToNextLevel ):
                continue

            #del moves[-1]
            current = current.parent
            if ( current is None ):
                raise Exception("Error! Did not find path to for the current move")

class BinaryMoveTree(MoveTree):
    def __init__(self):
        super().__init__()

    def getPath( self, x, y ):
        moves = []
        current = self.entries[0]
        self.clean()
        moves.append(current.move)
        counter = 0
        maxIter = 1000
        while ( True ):
            counter += 1
            if ( counter >= maxIter ):
                raise Exception("Infinite loop when searching for path in binary move tree")
            current.nTimesVisited += 1
            if ( not current.left is None and current.nTimesVisited == 1 ):
                moves.append(current.left.move)
                if ( moves[-1][0] == x and moves[-1][1] == y ):
                    return moves
                current = current.left
                continue

            elif ( not current.right is None and current.nTimesVisited <= 2 ):
                moves.append(current.right.move)
                if ( moves[-1][0] == x and moves[-1][1] == y ):
                    return moves
                current = current.right
                continue

            del moves[-1]
            current = current.parent
            if ( current is None ):
                raise Exception("Could not find path for the current move!")

class BinaryMoveTreeEntry:
    def __init__(self):
        self.left = None
        self.right = None
        self.parent = None
        self.move = []
        self.nTimesVisited = 0

class QuarticMoveTreeEntry:
    def __init__(self):
        self.branches = [None,None,None,None]
        self.parent = None
        self.move = []
        self.nTimesVisited = 0
        self.checked = [False,False,False,False]

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

    def save( self, fname ):
        out = open(fname, 'w')
        for i in range(0,8):
            for j in range(0,8):
                out.write("%s(%s),"%(self.board[j][i].name, self.board[j][i].color))
            out.write("\n")
        out.close()
        print ("Board state written to %s"%(fname))

class Piece:
    board = Board() # All Pieces share the same board

    def __init__( self ):
        self.x = 0
        self.y = 0
        self.color = "white"
        self.name = "empty"

    def validMoves( self ):
        allMoves = []
        allMoves =  self.validRegularMoves()
        catchMoves =  self.validCatchMoves()
        allMoves += catchMoves.toList()
        return allMoves, catchMoves

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
        tree = BinaryMoveTree()
        rootMove = BinaryMoveTreeEntry()
        rootMove.move = [self.x,self.y]
        tree.entries.append(rootMove)

        current = rootMove
        counter = 0
        maxIter = 1000
        while ( True ):
            counter += 1
            if ( counter >= maxIter ):
                raise Exception("Infinite loop in search tree for class %s"%(self.name))
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
        return tree


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

class King(Piece):
    def __init__(self):
        super().__init__()
        self.name = "king"
        self.guiRadiusInPx = 30

    def validRegularMoves( self ):
        moves = []
        x1 = [self.x+1,self.x+1,self.x-1,self.x-1]
        y1 = [self.y+1,self.y-1,self.y+1,self.y-1]
        for i in range(0,len(x1)):
            if ( self.board.isInside(x1[i],y1[i]) and self.board.getPiece(x1[i],y1[i]).name == "empty" ):
                moves.append([x1[i],y1[i]])
        return moves

    def validCatchMoves( self ):
        moves = []
        tree = QuarticMoveTree()
        rootMove = QuarticMoveTreeEntry()
        rootMove.move = [self.x,self.y]
        tree.entries.append(rootMove)

        current = rootMove
        maxIter = 10
        counter = 0
        directions = ["ne", "se", "sw", "nw"]
        print ("-----------------")
        while ( True ):
            counter += 1
            if ( counter >= maxIter ):
                raise Exception("Infinite loop in search tree for valid moves in class %s"%(self.name))
            moveFound = False
            print (current, current.move)
            # Check right of the current node
            for i in range(0,4):
                if ( not current.checked[i] ):
                    current.checked[i] = True
                    newmove = self.findCatchMove( current.move[0], current.move[1], direction=directions[i] )
                    if ( len(newmove) > 0 and not tree.isInSearchTree(newmove) ):
                        print (newmove)
                        newEntry = QuarticMoveTreeEntry()
                        newEntry.move = newmove
                        newEntry.parent = current
                        current.branches[i] = newEntry
                        current = newEntry
                        tree.entries.append(current)
                        moveFound = True
                        break
            if ( moveFound ):
                continue

            # If it enters here go back to parent
            current = current.parent
            if ( current is None ):
                # Back to the root node
                break
            print (tree.toList())
        return tree

    def findCatchMove( self, x, y, direction="nw" ):
        if ( direction == "ne" ):
            x1 = x + 1
            y1 = y + 1
            x2 = x + 2
            y2 = y + 2
        elif ( direction == "se" ):
            x1 = x+1
            y1 = y-1
            x2 = x+2
            y2 = y-2
        elif ( direction == "sw" ):
            x1 = x-1
            y1 = y-1
            x2 = x-2
            y2 = y-2
        elif ( direction == "nw" ):
            x1 = x-1
            y1 = y+1
            x2 = x-2
            y2 = y+2
        else:
            raise Exception("Unknown direction in find path in class %s"%(self.name))

        if ( self.board.isInside(x1,y1) and self.board.getPiece(x1,y1).color != self.color and
        self.board.getPiece(x1,y1).name != "empty"):
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
        colorSq = (228,26,28)
        width = self.guiRadiusInPx*0.5
        xPx = int( self.x*tilewidth+tilewidth/2.0 )
        yPx = int( self.y*tileheight+tileheight/2.0 )
        pg.draw.circle( screen, color, (xPx,yPx), self.guiRadiusInPx, 0 )
        pg.draw.rect( screen, colorSq, (xPx-0.5*width,yPx-0.5*width,width,width), 0 )
