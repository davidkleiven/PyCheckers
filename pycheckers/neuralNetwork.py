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
        return (np.sum( self.weights*inputState ) - self.threshold)

class OutputNeuron:
    def __init__(self):
        pass
    def evaluate( self, inputState ):
        return inputState.mean()

class Layer:
    def __init__( self, nIn, nOut, useOutputNeurons=False ):
        self.neurons = []
        if ( useOutputNeurons ):
            self.neurons.append(OutputNeuron())
        else:
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
            if ( numberOfNeurons[i] == 1 ):
                self.layers.append( Layer( int(numberOfNeurons[i]), int(numberOfNeurons[i+1]) ), useOutputNeurons=True )
            else:
                self.layers.append( Layer( int(numberOfNeurons[i]), int(numberOfNeurons[i+1]) ) )
        self.generateNewInitialCondition = True
        self.ga = GeneticAlgorithm( self, 1000 )
        self.numberOfGAGenerations = 100

    def perturbNext( self, fitness ):
        """
        Use the next chromosome in the GA population
        """
        self.ga.nextChromosome( fitness )
        if ( self.ga.currentGeneration >= self.numberOfGAGenerations ):
            self.generateNewInitialCondition = True
            self.ga.currentGeneration = 0

    def setRandomThresholds( self ):
        """
        Set random thresholds
        """
        for layer in self.layers:
            for neuron in layer.neurons:
                neuron.threshold = np.random.normal(loc=0.0,scale=10.0)

    def getNumberOfParameters( self ):
        """
        Get the total number of optimization parameters (weights and threshold)
        """
        nParams = 0
        for i in range(0,len(self.layers)-1):
            layer = self.layers[i]
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
        for i in range(0,len(self.layers)-1):
            layer = self.layers[i]
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
        for i in range(0,len(self.layers)-1):
            layer = self.layers[i]
            for neuron in layer.neurons:
                neuron.weights = newvalues[current:current+len(neuron.weights)]
                neuron.threshold = newvalues[current+len(neuron.weights)]
                current += len(neuron.weights)+1

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

class GeneticAlgorithm:
    def __init__( self, network, populationSize ):
        self.network = network
        self.populationSize = populationSize
        self.population = np.zeros((self.network.getNumberOfParameters(),populationSize) )
        self.generateNewInitialState()
        self.fitness = np.zeros(populationSize)
        self.currentChromosome = 0
        self.numberOfParents = 4
        self.mutationProbability = 0.05
        self.currentGeneration = 0

    def generateNewInitialState( self ):
        """
        Initialize all weights and thresholds to random values
        """
        mean = 0.0
        # Want of the parameter z in each layer is in [-1,1]
        sigma = 4.0
        for i in range(0,self.population.shape[1]):
            slope = 2.0*np.random.rand()-1.0
            exp = np.random.rand()*2.0
            self.population[0,i] = np.random.normal( loc=mean, scale=sigma )
            for j in range(1, self.population.shape[0] ):
                #self.population[j,i] = self.population[j-1,i] + np.random.normal( loc=mean, scale=0.1*sigma )
                self.population[j,i] = np.random.normal( loc=mean, scale=sigma )

        # Set random threshols and write it back to the population array
        #for i in range(0,self.populationSize ):
        #    self.network.distribute( self.population[:,i] )
        #    self.network.setRandomThresholds()
        #    self.population[:,i] -= np.mean( self.population[:,i] )
        #    self.population[:,i] = self.network.collectParameters()
        #    self.population[:,i] /= np.max( np.abs(self.population[:,i]) )
        self.network.distribute( self.population[:,0] )

    def nextChromosome( self, currentFitnessValue ):
        """
        Update the fitness of the current chromosome and make the next one active
        If it is the last chromosome a new generation will be created
        """
        self.fitness[self.currentChromosome] = currentFitnessValue
        self.currentChromosome += 1
        if ( self.currentChromosome >= self.populationSize ):
            self.currentChromosome = 0
            self.reproduce()
            self.mutate()
            self.currentGeneration += 1
            print()
            print ("New generation created...")
        chrom = self.population[:,self.currentChromosome]
        self.network.distribute( self.population[:,self.currentChromosome] )

    def selectParents( self ):
        """
        Selects parants for a chromosome
        """
        # Roulette selection
        parents = []
        fitnessCopy = []
        for i in range(0,self.numberOfParents):
            fitnessSum = np.sum(fitness)
            random = np.random.rand(0.0,fitnessSum)
            cumsum = 0.0
            for i in range(0,len(fitness)):
                cumsum += self.fitness[i]
                if ( cumsum > random ):
                    parents.append[i]
                    fitnessCopy.append(self.fitness[i])

                    # Set fitness to zero such that is not elected again
                    self.fitness[i] = 0.0
        # Reset the fitness
        for i in range(0,len(parents)):
            self.fitness[parents[i]] = fitnessCopy[i]
        return parents

    def reproduce( self ):
        """
        Produce a new generation
        """
        newGeneration = np.zeros(self.population.shape)

        for i in range(0,self.population.shape[1]):
            parents = self.parents()
            for j in range(0,self.population.shape[0] ):
                selectedParent = np.random.randint(0,high=self.numberOfParents)
                newGeneration[j,i] = self.population[j,parents[selectedParent]]
        del self.population
        self.population = newGeneration

    def mutate( self ):
        """
        Perform the mutation step. Mutation is done by assigning a random value to the selected gene
        """
        for i in range(0,self.populationSize):
            for j in range(0,self.population.shape[0]):
                if ( np.random.rand() < self.mutationProbability ):
                    stddev = np.std( self.population.ravel() )
                    self.population[j,i] = np.random.normal(loc=self.population[j,i],scale=std )
