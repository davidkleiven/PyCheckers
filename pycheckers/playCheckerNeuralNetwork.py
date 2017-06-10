import gui as pychgui
import game as gm
import neuralNetwork as nn
import pickle as pck

def main():
    fname = "trainedNetwork.pkl"

    try:
        networkfile = open(fname, 'rb')
        network = pck.load( networkfile )
    except Exception as exc:
        print (str(exc))
        neurons = [5*64,int(0.66*5*64),1]
        network = nn.Network( neurons )

    app = pychgui.PyCheckerGUI()
    app.game.p1.setHumanUser()
    app.game.p2.setNeuralNetwork( network, app.game )
    app.game.p1.name = "David Kleiven"
    app.game.p2.name = "Computer"
    app.saveLastState = True
    app.play()

if __name__ == "__main__":
    main()
