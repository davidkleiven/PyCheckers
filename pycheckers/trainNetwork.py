import gui as pychgui
import game as gm
import sys
import time
import pickle as pck
import neuralNetwork as nn
from matplotlib import pyplot as plt

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
        neurons = [5*64,int(0.66*5*64),1]
        network = nn.Network( neurons )
    network.visualize()
    plt.show()

    numberOfWeightUpdates = 0
    starttime = time.time()
    while( time.time() -starttime < float(argv[0])*3600 ):
        diffSec = time.time() -starttime
        print ("Run for: %d min. End at %d min.  Weights updated: %d times   "%(diffSec/60, float(argv[0])*60,numberOfWeightUpdates), end="\r")
        game = gm.Game()
        game.setupGame()
        game.p1.setNeuralNetwork( network, game )
        game.p2.setNeuralNetwork( network, game )
        while ( game.state != "finished" ):
            game.stepGame()

        costFunc = 0.0
        if ( game.p1.winner ):
            costFunc = 1.0
        elif ( game.p2.winner ):
            costFunc = -1.0
        else:
            costFunc = 0.0

        if ( not network.hasNewWeights ):
            network.updateGradient(costFunc)
            network.perturbNext()
        else:
            network.previousCostFunction = costFunc
            network.hasNewWeights = False
            numberOfWeightUpdates += 1
    network.save(fname)
    print ("Newly trained network saved to %s"%(fname))

if __name__ == "__main__":
    main( sys.argv[1:] )
