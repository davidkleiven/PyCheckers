import numpy as np
import pickle as pck
from matplotlib import pyplot as plt

class Neuron:
    def __init__( self, nWeights ):
        self.weights = np.ones(nWeights)
        self.threshold = 1.0

    def evaluate( self, inputState ):
        """
        Evaluates the parameter z that is sent to the sigmoid function sigma(z) = 1/(1+exp(-z))
        """
        return np.sum( self.weights*inputState ) - self.threshold

class Layer:
    def __init__( self, nIn, nOut ):
        self.neurons = []
        for i in range(0,int(nOut)):
            self.neurons.append( Neuron(int(nIn)) )

    def evaluate( self, inputState ):
        """
        Evaluates the output vector of the current layer
        """
        output = np.zeros(len(self.neurons) )
        for i in range(0,len(self.neurons) ):
            output[i] = self.sigmoid( self.neurons[i].evaluate(inputState) )
        return output

    def sigmoid( self, z ):
        """
        Sigmoid function used as activation function for the neurons
        """
        return 1.0/( 1.0 + np.exp(-z) )

    def visualize( self, ax ):
        """
        Plot subfigure corresponding to the current layer
        """
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
        self.stepsize = 0.5
        self.gradient = np.zeros( self.getNumberOfParameters() )
        self.previousGradient = np.zeros( self.getNumberOfParameters() )
        self.previousValues = np.zeros( self.getNumberOfParameters() )
        self.newValues = self.collectParameters()
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
        """
        Evaluates the entire neural network. Returns a scalar value describing the "goodness" if the board state
        """
        output = self.layers[0].evaluate(inputState)
        for i in range(1,len(self.layers)):
            output = self.layers[i].evaluate(output)
        return output[0]

    def save( self, fname ):
        """
        Dumps the current network to a pickle file
        """
        out = open(fname, 'wb' )
        pck.dump( self, out )
        out.close()

    def collectParameters( self ):
        """
        Collects all weights and threshold in a single vector
        """
        params = np.zeros( self.getNumberOfParameters() )
        current = 0
        for layer in self.layers:
            for neuron in layer.neurons:
                params[current:current+len(neuron.weights)] = neuron.weights
                params[current+len(neuron.weights)] = neuron.threshold
                current += len(neuron.weights)+1
        return params

    def distribute( self, newvalues ):
        """
        Distributes the values in the vector newvalues to the weights and threshold in the neural network
        """
        current = 0
        assert( len(newvalues) == self.getNumberOfParameters() )
        for layer in self.layers:
            for neuron in layer.neurons:
                neuron.weights = newvalues[current:current+len(neuron.weights)]
                neuron.threshold = newvalues[current+len(neuron.weights)]
                current += len(neuron.weights)+1

    def updateGradient( self, newCostFuncValue ):
        """
        Updates the gradient based on the current value of the cost function
        """
        change = (newCostFuncValue - self.previousCostFunction)
        self.gradient[self.currentIndx] = change/(self.stepsize)
        self.currentIndx += 1
        if ( self.currentIndx >= len(self.gradient) ):
            self.updateWeights()

    def updateWeights( self ):
        """
        When the full gradient has been determined, this function updates all the weights and thresholds
        based on the gradient descent method
        """
        gradDiff = self.gradient - self.previousGradient
        gamma = ( self.newValues - self.previousValues ).dot(gradDiff)
        gamma /= np.sum(gradDiff**2)

        self.previousValues[:] = self.newValues[:]
        self.newValues = self.newValues - gamma*self.gradient
        self.previousGradient[:] = self.gradient[:]
        self.currentIndx = 0
        self.hasNewWeights = True
        self.distribute( self.newValues )

    def perturbNext( self ):
        """
        Modifies the next weight/threshold. Successive calls to this function will eventually vary all the
        weights and thresholds in the network
        """
        if ( self.currentIndx > 0 ):
            self.newValues[self.currentIndx-1] -= self.stepsize
        self.newValues[self.currentIndx] += self.stepsize

    def visualize( self ):
        """
        Create figure showing all the weights. Each subfigure corresponds to one layer
        """
        nLayers = len(self.layers)
        ncols = int(np.sqrt(nLayers))+1
        fig = plt.figure()
        for i in range(0, len(self.layers)):
            ax = fig.add_subplot(ncols,ncols,i+1)
            im = self.layers[i].visualize(ax)
            fig.colorbar(im)
