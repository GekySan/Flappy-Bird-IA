import random
import math

class Neuron:
    def __init__(self):
        self.value = 0.0
        self.weights = []

    def populate(self, nb):
        self.weights = [random.uniform(-1, 1) for _ in range(nb)]

class Layer:
    def __init__(self, id):
        self.id = id
        self.neurons = []

    def populate(self, nb_neurons, nb_inputs):
        self.neurons = []
        for _ in range(nb_neurons):
            neuron = Neuron()
            neuron.populate(nb_inputs)
            self.neurons.append(neuron)

class Network:
    def __init__(self):
        self.layers = []

    def populate(self, network_architecture):
        assert len(network_architecture) >= 2
        self.layers = []
        input_neurons = network_architecture[0]
        hidden_layers = network_architecture[1:-1]
        output_neurons = network_architecture[-1]

        # Couche d'entrée
        input_layer = Layer(0)
        input_layer.populate(input_neurons, 0)
        self.layers.append(input_layer)

        previous_neurons = input_neurons
        layer_id = 1

        # Couches cachées
        for hidden_neurons in hidden_layers:
            hidden_layer = Layer(layer_id)
            hidden_layer.populate(hidden_neurons, previous_neurons)
            self.layers.append(hidden_layer)
            previous_neurons = hidden_neurons
            layer_id += 1

        # Couche de sortie
        output_layer = Layer(layer_id)
        output_layer.populate(output_neurons, previous_neurons)
        self.layers.append(output_layer)

    def activate(self, inputs):
        assert len(inputs) == len(self.layers[0].neurons)
        for i in range(len(inputs)):
            self.layers[0].neurons[i].value = inputs[i]

        for i in range(1, len(self.layers)):
            prev_layer = self.layers[i - 1]
            for neuron in self.layers[i].neurons:
                summation = 0.0
                for k in range(len(prev_layer.neurons)):
                    summation += prev_layer.neurons[k].value * neuron.weights[k]
                neuron.value = self.sigmoid(summation)

        outputs = [neuron.value for neuron in self.layers[-1].neurons]
        return outputs

    '''
    https://fr.wikipedia.org/wiki/Sigmo%C3%AFde_(math%C3%A9matiques)

    On peut utiliser une autre fonction d'activation, voir https://fr.wikipedia.org/wiki/Fonction_d%27activation
    '''
    @staticmethod
    def sigmoid(x):
        return 1 / (1 + math.exp(-x))
    '''
    @staticmethod
    def tan_h(x):
        return math.tanh(x)
    '''

    def get_weights(self):
        weights = []
        for layer in self.layers[1:]:
            for neuron in layer.neurons:
                weights.extend(neuron.weights)
        return weights

    def set_weights(self, weights):
        offset = 0
        for layer in self.layers[1:]:
            for neuron in layer.neurons:
                nb_weights = len(neuron.weights)
                neuron.weights = weights[offset:offset + nb_weights]
                offset += nb_weights

class Genome:
    def __init__(self, score, network):
        self.score = score
        self.network_weights = network.get_weights()

class Generation:
    def __init__(self):
        self.genomes = []

    def add_genome(self, genome):
        self.genomes.append(genome)
        self.genomes.sort(key=lambda x: x.score, reverse=True)

    def breed(self, parent1, parent2, nb_children):
        children = []
        for _ in range(nb_children):
            child_weights = []
            for w1, w2 in zip(parent1.network_weights, parent2.network_weights):
                child_weights.append(w1 if random.random() > 0.5 else w2)

            child_weights = [w + random.uniform(-0.5, 0.5) if random.random() <= 0.1 else w for w in child_weights]
            child_network = Network()
            child_network.populate([2, 2, 1])
            child_network.set_weights(child_weights)
            children.append(child_network)
        return children

    def generate_next_generation(self, population_size):
        next_gen = []
        elite_count = int(0.2 * population_size)
        random_count = int(0.2 * population_size)

        # Élitisme
        next_gen.extend([genome.network_weights for genome in self.genomes[:elite_count]])
        
        # Ajout de réseaux aléatoires
        for _ in range(random_count):
            network = Network()
            network.populate([2, 2, 1])
            next_gen.append(network.get_weights())

        # Croisements
        while len(next_gen) < population_size:
            parent1 = random.choice(self.genomes[:elite_count])
            parent2 = random.choice(self.genomes[:elite_count])
            children = self.breed(parent1, parent2, 1)
            next_gen.extend([child.get_weights() for child in children])

        return next_gen[:population_size]

class Neuroevolution:
    def __init__(self, population_size, network_architecture):
        self.population_size = population_size
        self.network_architecture = network_architecture
        self.generations = []
        self.current_generation = Generation()

    def create_initial_population(self):
        networks = []
        for _ in range(self.population_size):
            network = Network()
            network.populate(self.network_architecture)
            networks.append(network)
        return networks

    def next_generation(self):
        self.generations.append(self.current_generation)
        next_gen_weights = self.current_generation.generate_next_generation(self.population_size)
        networks = []
        for weights in next_gen_weights:
            network = Network()
            network.populate(self.network_architecture)
            network.set_weights(weights)
            networks.append(network)
        self.current_generation = Generation()
        return networks

    def add_genome(self, genome):
        self.current_generation.add_genome(genome)
