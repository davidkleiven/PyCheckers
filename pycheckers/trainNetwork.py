import gui as pychgui
import game as gm
import sys
import time
import pickle as pck
import neuralNetwork as nn
from matplotlib import pyplot as plt
import piece as pc
import numpy as np

def main( argv ):
    if ( len(argv) != 1 ):
        print ("Usage: trainNetwork.py <numberOfHours>")
        return

    fname = "trainedNetwork.pkl"

    try:
        networkfile = open(fname, 'rb')
        network = pck.load( networkfile )
    except Exception as exc:
        print (str(exc))
        neurons = [5*64,0.66*5*64,1]
        network = nn.Network( neurons )
    network.visualize()
    plt.show()

    numberOfWeightUpdates = 0
    starttime = time.time()
    gameResult = "draw"
    generateNewInitialState = True
    gameFname = "lastInitialState.pck"
    fitness = 0.0
    pNNVictories = 0
    pOpponentVictory = 0
    draws = 0
    while( time.time() -starttime < float(argv[0])*3600 ):
        diffSec = time.time() -starttime
        print ("Run for: %d min. End at %d min. Last game: %s, Fitness=%.8E"%(diffSec/60, float(argv[0])*60,gameResult,fitness), end="\r")
        game = gm.Game()
        game.setupGame()

        singleGameStartTime = time.time()

        # Change to neural network players
        #game.p1.setNeuralNetwork( network, game )
        game.p2.setNeuralNetwork( network, game )

        counter = 0
        randomStepCounter = 0
        while ( game.state != "finished" ):
            game.stepGame()
            if ( counter%10 == 0 ):
                game.p1.setRandomPolicy()
                randomStepCounter = 0
            randomStepCounter += 1
            counter += 1
            if ( randomStepCounter >= 2 ):
                game.p1.setNeuralNetwork( network, game )

        singleGameTime = time.time() - singleGameStartTime

        alpha = 100.0
        if ( game.p1.winner ):
            # Our player loose
            gameResult = "p1  "
            pOpponentVictory += 1
            fitness = np.exp(-alpha/game.numberOfTurns)
        elif ( game.p2.winner ):
            # Our player wins
            fitness = np.exp(alpha/game.numberOfTurns)
            gameResult = "p2  "
            pNNVictories += 1
        else:
            fitness = 0.5*( np.exp(alpha/game.numberOfTurns) + np.exp(-alpha/game.numberOfTurns) )
            draws += 1
            gameResult = "draw"
        network.perturbNext( fitness )

    network.save(fname)
    print ("Newly trained network saved to %s"%(fname))

    totGames = pNNVictories+pOpponentVictory+draws
    print ("=============== RESULTS =================")
    print ("Neural network wins: %d (%.2f per cent)"%(pNNVictories,pNNVictories*100.0/totGames))
    print ("Handicaped player wins: %d (%.2f per cent)"%(pOpponentVictory,pOpponentVictory*100.0/totGames))
    print ("Draw: %d (%.2f per cent)"%(draws,draws*100.0/totGames))
    print ("==========================================")

if __name__ == "__main__":
    main( sys.argv[1:] )
