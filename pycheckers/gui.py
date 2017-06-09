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

        # Initialize pygame
        pg.init()
        self.screen = pg.display.set_mode((self.width,self.height))
        pg.display.set_caption("PyCheckers")
        self.pgclock = pg.time.Clock()

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
        for piece in self.game.p1.pieces:
            piece.draw( self.screen, self.getTileSize(), self.getTileSize() )
        for piece in self.game.p2.pieces:
            piece.draw( self.screen, self.getTileSize(), self.getTileSize() )
        pg.display.update()

    def play( self ):
        done = False
        self.initBoard()
        while ( not done ):
            for event in pg.event.get():
                if ( event.type == pg.QUIT ):
                    done = True
            pg.display.flip()
            self.pgclock.tick(60)
        pg.quit()
