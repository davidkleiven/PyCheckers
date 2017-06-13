import game as gm
import piece as pc
import pygame as pg

class PyCheckerGUI:
    def __init__( self ):
        self.game = gm.Game()
        self.game.setupGame()
        self.darkField = (153,52,4)
        self.brightField = (166,206,227)
        self.highlightColor = (254,196,79)
        self.width = 700
        self.height = 500
        self.saveLastState = False

        # Initialize pygame
        pg.init()
        self.screen = pg.display.set_mode((self.width,self.height))
        pg.display.set_caption("PyCheckers")
        self.pgclock = pg.time.Clock()
        self.highlightedTiles = []
        self.undo = Button( self.screen, [550, 400], [100,40], "Undo" )

    def getTileSize( self ):
        return self.height/8

    def drawTile( self, x, y, highlight=False ):
        tilewidth = self.getTileSize()
        tileheight = self.getTileSize()
        pixelX = tilewidth*x
        pixelY = tileheight*y

        if ( highlight ):
            pg.draw.rect( self.screen, self.highlightColor, (pixelX,pixelY,tilewidth,tileheight), 0 )
            return

        if ( y%2 == 0 ):
            # Even row
            if ( x%2 == 0 ):
                color = self.darkField
            else:
                color = self.brightField
        else:
            if ( x%2 == 0 ):
                color = self.brightField
            else:
                color = self.darkField

        pg.draw.rect( self.screen, color, (pixelX,pixelY,tilewidth,tileheight), 0 )


    def initBoard( self ):
        for i in range(0,8):
            for j in range(0,8):
                self.drawTile(i,j)

        # Draw all the pieces
        self.drawPieces()
        pg.display.update()

    def drawBoard( self ):
        for i in range(0,8):
            for j in range(0,8):
                if ( [i,j] in self.highlightedTiles ):
                    self.drawTile(i,j,highlight=True)
                else:
                    self.drawTile(i,j)

    def drawPieces( self ):
        for piece in self.game.p1.pieces:
            piece.draw( self.screen, self.getTileSize(), self.getTileSize() )
        for piece in self.game.p2.pieces:
            piece.draw( self.screen, self.getTileSize(), self.getTileSize() )

    def mouseClickHander( self ):
        if ( self.game.state == "finished" ):
            return
        pos = pg.mouse.get_pos()

        # Check if it hit the undo button
        if ( self.undo.isInside(pos) ):
            self.game.undoMove()
            return


        # Find tile
        x = int( pos[0]/self.getTileSize() )
        y = int( pos[1]/self.getTileSize() )

        if ( isinstance(self.game.playerToMove.movePolicy, gm.HumanUser) ):

            for piece in self.game.playerToMove.pieces:
                if ( x==piece.x and y==piece.y ):
                    self.highlightedTiles = []
                    self.highlightedTiles.append([x,y])
                    self.game.playerToMove.movePolicy.selectPiece(x,y)
                    validMoves, catchTree = piece.validMoves()
                    self.highlightedTiles += validMoves
                    break

            self.game.playerToMove.movePolicy.selecteNewPosition(x,y)
            if ( not self.game.playerToMove.movePolicy.selectedPiece is None and
            not self.game.playerToMove.movePolicy.newPosition is None ):
                self.game.stepGame()

    def returnKeyHandler( self ):
        if ( isinstance(self.game.playerToMove.movePolicy, gm.HumanUser) ):
            return
        if ( self.game.state == "finished" ):
            return
        self.game.stepGame()

    def gameFinished( self ):
        text = "It's a draw!"
        if ( self.game.p1.winner ):
            text = "Player: %s won"%(self.game.p1.name)
        elif( self.game.p2.winner ):
            text = "Player: %s won"%(self.game.p2.name)
        font = pg.font.SysFont('Comic Sans MS', 30)
        textsurface = font.render(text, False, (0, 0, 0))
        self.screen.blit(textsurface,(0,0))

    def updateMoveNumber( self ):
        posX = 8*self.getTileSize()+10
        posY = self.getTileSize()
        height = 80
        width = 200
        pg.draw.rect( self.screen, (0,0,0), (posX, posY, width, height) )
        font = pg.font.SysFont('Comic Sans MS', 60)
        text = "Move: %d"%(self.game.numberOfTurns)
        textsurface = font.render(text, False, (77,175,74))
        self.screen.blit(textsurface,(posX, posY))

    def hasHumanUser( self ):
        return isinstance( self.game.p1.movePolicy, gm.HumanUser ) or isinstance( self.game.p2.movePolicy, gm.HumanUser )

    def play( self ):
        try:
            done = False
            self.initBoard()
            while ( not done ):
                for event in pg.event.get():
                    if ( event.type == pg.QUIT ):
                        done = True
                    elif ( event.type == pg.MOUSEBUTTONDOWN ):
                        self.mouseClickHander()
                    elif ( event.type == pg.KEYDOWN):
                        if ( event.key==pg.K_RETURN):
                            self.returnKeyHandler()

                if ( not self.hasHumanUser() ):
                    self.game.stepGame()
                    if ( self.game.state == "finished" ):
                        done = True
                self.drawBoard()
                self.drawPieces()
                self.updateMoveNumber()
                self.undo.draw()
                if ( self.game.state == "finished" ):
                    self.gameFinished()
                pg.display.update()
                pg.display.flip()
                self.pgclock.tick(10)
                if ( self.saveLastState ):
                    pg.image.save( self.screen, "lastState.jpg")
        except Exception as exc:
            print (str(exc))

        pg.quit()

class Button:
    def __init__(self, screen, pos, dim, text ):
        self.screen = screen
        self.x = pos[0]
        self.y = pos[1]
        self.width = dim[0]
        self.height = dim[1]
        self.text = text

    def draw( self ):
        pg.draw.rect( self.screen, (100,100,100), (self.x, self.y, self.width, self.height) )
        font = pg.font.SysFont('Comic Sans MS', 30)
        textsurface = font.render(self.text, False, (0,40,0))
        self.screen.blit(textsurface,(self.x+20, self.y+10))

    def isInside( self, pos ):
        return pos[0] >= self.x and pos[0] <= self.x+self.width and pos[1] >= self.y and pos[1] <= self.y+self.height
