import gui as pychgui
import game as gm
import sys
import time

def main( argv ):
    if ( len(argv) == 0 ):
        print ("Usage: python3 twoRandomPlayer.py <numberofHours>" )
        return

    useGUI = False
    starttime = time.time()
    gameNumber = 0
    while( time.time()-starttime < float(argv[0])*3600 ):
        gameNumber += 1
        print ("Game: %d"%(gameNumber))
        if ( useGUI ):
            app = pychgui.PyCheckerGUI()
            app.game.p1.name = "Rnd player"
            app.game.p2.name = "Even more rnd plaer"
            #app.saveLastState = True
            app.play()
        else:
            game = gm.Game()
            game.setupGame()
            game.p1.name = "Random player"
            game.p2.name = "Even more random player"
            while( not game.state == "finished" ):
                game.stepGame()

            game.printResult()

if __name__ == "__main__":
    main( sys.argv[1:] )
