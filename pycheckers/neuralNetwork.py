import numpy as np
import pickle as pck
from matplotlib import pyplot as plt

class Neuron:
    def __init__( self, nWeights ):
        self.weights = np.ones(nWeights)
        self.threshold = 1.0

    def evaluate( self, inputState ):
        return np.sum( self.weights*inputState ) - self.threshold

class Layer:
    def __init__( self, nIn, nOut ):
        self.neurons = []
        for i in range(0,int(nOut)):
            self.neurons.append( Neuron(int(nIn)) )

    def evaluate( self, inputState ):
        output = np.zeros(len(self.neurons) )
        for i in range(0,len(self.neurons) ):
            output[i] = self.sigmoid( self.neurons[i].evaluate(inputState) )
        return output

    def sigmoid( self, z ):
        return 1.0/( 1.0 + np.exp(-z) )

    def visualize( self, ax ):
        values = np.zeros((len(self.neurons),len(self.neurons[0].weights)))
        for i in range(0,len(self.neurons)):
            values[i,:] = self.neurons[i].weights
        return ax.imshow( values, aspect="auto", cmap="inferno")


class Network:
    def __init__( self, numberOfNeurons ):
        self.layers = []
        for i in range(0,len(numberOfNeurons)-1):
            self.layers.append( Layer( int(numberOfNeurons[i]), int(numberOfNeurons[i+1]) ) )
        self.learningRate = 0.1
        self.prevValue = 0.5
        self.currentLayer = 0
        self.currentNeuron = 0
        self.currentWeight = 0
        self.relativeWeightPertubation = 0.3
        self.alterThreshold = False
        self.gradient = np.zeros( self.getNumberOfParameters() )
        self.currentIndx = 0
        self.previousCostFunction = 1.0
        self.hasNewWeights = True

    def getNumberOfParameters( self ):
        nParams = 0
        for layer in self.layers:
            for neuron in layer.neurons:
                nParams += (len(neuron.weights)+1)
        return nParams

    def evaluate( self, inputState ):
        output = self.layers[0].evaluate(inputState)
        for i in range(1,len(self.layers)):
            output = self.layers[i].evaluate(output)
        return output[0]

    def save( self, fname ):
        out = open(fname, 'wb' )
        pck.dump( self, out )
        out.close()

    def updateGradient( self, newCostFuncValue ):
        change = (newCostFuncValue - self.previousCostFunction)
        self.gradient[self.currentIndx] = change/(self.relativeWeightPertubation*self.prevValue)
        self.currentIndx += 1

        # Reset the value
        if ( self.alterThreshold ):
            self.layers[self.currentLayer].neurons[self.currentNeuron].threshold = self.prevValue
        else:
            self.layers[self.currentLayer].neurons[self.currentNeuron].weights[self.currentWeight]= self.prevValue

        self.currentWeight += 1
        if ( self.currentWeight >= len(self.layers[self.currentLayer].neurons[self.currentNeuron].weights) ):
            self.alterThreshold = True
        else:
            self.alterThreshold = False
            self.currentWeight = 0
            self.currentNeuron += 1

        if ( self.currentNeuron >= len(self.layers[self.currentLayer].neurons) ):
            self.currentLayer += 1
            self.currentNeuron = 0
            self.currentWeight = 0

        if ( self.currentLayer >= len(self.layers) ):
            self.currentLayer = 0
            self.currentNeuron = 0
            self.currentWeight = 0
            self.updateWeights()

        if ( self.currentIndx >= len(self.gradient) ):
            raise Exception("The gradient has the wrong length")

    def updateWeights( self ):
        startIndx = 0
        for layer in self.layers:
            for neuron in layer.neurons:
                grad = self.gradient[startIndx:startIndx+len(neuron.weights)]
                dw = self.relativeWeightPertubation*neuron.weights
                neuron.weights += self.learningRate*grad*dw
                grad = self.gradient[startIndx+len(neuron.weights)]
                deltaThres = self.relativeWeightPertubation*neuron.threshold
                neuron.threshold += self.learningRate*grad*deltaThres
                startIndx += startIndx+len(neuron.weights)+1
        self.currentIndx = 0
        self.hasNewWeights = True

    def perturbNext( self ):
        if ( not self.alterThreshold ):
            self.prevValue = self.layers[self.currentLayer].neurons[self.currentNeuron].weights[self.currentWeight]
            self.layers[self.currentLayer].neurons[self.currentNeuron].weights[self.currentWeight] += self.relativeWeightPertubation*self.prevValue
        else:
            self.prevValue = self.layers[self.currentLayer].neurons[self.currentNeuron].threshold
            self.layers[self.currentLayer].neurons[self.currentNeuron].threshold += 0.3*self.prevValue

    def visualize( self ):
        nLayers = len(self.layers)
        ncols = int(np.sqrt(nLayers))+1
        fig = plt.figure()
        for i in range(0, len(self.layers)):
            ax = fig.add_subplot(ncols,ncols,i+1)
            im = self.layers[i].visualize(ax)
            fig.colorbar(im)
