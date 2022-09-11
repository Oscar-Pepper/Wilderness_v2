import numpy as np
from random import random, randint, uniform
from copy import copy, deepcopy
from collections import defaultdict
from config import *

class Node:
    id_count = 0
    innovations = defaultdict(list)
    def __init__(self, id, layer, act_function_type):
        self.id = id
        self.layer = layer
        self.value = 0
        self.input_nodes = []
        self.input_weights = []
        self.act_function_type = act_function_type
        if self.act_function_type == 'sigmoid':
            self.activation_function = lambda x: 1 / (1 + np.exp(-1 * x))
        elif self.act_function_type == 'mod_sigmoid':
            self.activation_function = lambda x: 1 / (1 + np.exp(-4.9 * x))

    def link(self, input_nodes, input_weights):
        # add input nodes and connection weights to node
        self.input_nodes.extend(input_nodes)
        self.input_weights.extend(input_weights)
        # initialise input and weight arrays
        self.input_array = np.zeros(len(self.input_nodes))
        self.weights_array = np.array(self.input_weights, ndmin=2).T

    def update(self):
        if self.input_nodes:
            # load input array
            for i in range(len(self.input_nodes)):
                self.input_array[i] = self.input_nodes[i].value
            # dot product input node values with connection weights and apply activation function
            self.value = self.activation_function(np.dot(self.input_array, self.weights_array)[0])

    def info(self):
        print('node id:', self.id,
              '\tlayer:', self.layer,
              '\tvalue:', self.value,
              '\tactivation function:', self.act_function_type)

class Connect:
    innovations = {}
    def __init__(self, key, weight=None):
        self.key = key
        # if key exists, use value as ID. otherwise, add key to dictionary and assign unique ID
        self.id = Connect.innovations.setdefault(self.key, len(Connect.innovations) + 1)
        self.input_node = self.key[0]
        self.output_node = self.key[1]
        self.enabled = True
        if weight:
            self.weight = weight
        else:
            self.weight = random() - 0.5

    def info(self):
        print('connect innov:', self.id,
              '\tinput node:', self.input_node,
              '\toutput node:', self.output_node,
              '\tweight:', self.weight,
              '\tenabled:', self.enabled)

class Genome:
    def __init__(self):
        self.nodes = []
        self.connects = []
        if INIT_CONNECTS == 'unconnected':
            self.init_nodes()
        elif INIT_CONNECTS == 'full_nodirect':
            self.init_nodes()
            self.full_nodirect()
        self.nodes.sort(key=lambda x: x.layer)
        self.first_output_index = len(self.nodes) - NUM_OUTPUTS

    def create_node(self, key, layer):
        new_node_id = 0
        # check if key already exists
        if key in Node.innovations:
            # iterate through IDs in the key and check if existing innovations are not in genome
            for id in Node.innovations.get(key):
                if find_by_id(id, self.nodes) == False:
                    new_node_id = id
                    break
        # if the key is unique or the genome already contains all innovations of existing key, create new ID.
        if new_node_id == 0:
            Node.id_count += 1
            new_node_id = Node.id_count
            Node.innovations[key].append(new_node_id)
        new_node = Node(new_node_id, layer, ACTIVATION_FUNCTION)
        return new_node

    def init_nodes(self):
        # assign output layer and create list of nodes in each layer
        if NUM_HIDDEN:
            output_layer = 2
            self.node_layers = [NUM_INPUTS + 1, NUM_HIDDEN, NUM_OUTPUTS]
        else:
            output_layer = 1
            self.node_layers = [NUM_INPUTS + 1, NUM_OUTPUTS]
        # create bias node
        new_node = self.create_node((0, 0), 0)
        new_node.value = 1
        self.nodes.append(new_node)
        # create input nodes
        for i in range(NUM_INPUTS):
            new_node = self.create_node((0, i + 1), 0)
            self.nodes.append(new_node)
        # create output nodes
        for o in range(NUM_OUTPUTS):
            new_node = self.create_node((o + 1, 0), output_layer)
            self.nodes.append(new_node)
        # create hidden nodes
        for h in range(NUM_HIDDEN):
            new_node = self.create_node((h + 1, h + 1), 1)
            self.nodes.append(new_node)

    def full_nodirect(self):
        # create connections
        if NUM_HIDDEN:
            for i in range(NUM_INPUTS):
                for h in range(NUM_HIDDEN):
                    new_connect = Connect((i + 2, NUM_INPUTS + NUM_OUTPUTS + h + 2))
                    self.connects.append(new_connect)
            for h in range(NUM_HIDDEN):
                for o in range(NUM_OUTPUTS):
                    new_connect = Connect((NUM_INPUTS + NUM_OUTPUTS + h + 2, NUM_INPUTS + o + 2))
                    self.connects.append(new_connect)
        else:
            for i in range(NUM_INPUTS):
                for o in range(NUM_OUTPUTS):
                    new_connect = Connect((i + 2, NUM_INPUTS + o + 2))
                    self.connects.append(new_connect)

    def add_connect(self):
        # calculate total possible connections
        connects_count = 0
        nodes_to_connect = len(self.nodes) + BIAS_ENABLED - 1
        for i in range(len(self.node_layers) - 1):
            if i == 0:
                nodes_in_layer = self.node_layers[0] + BIAS_ENABLED - 1
            else:
                nodes_in_layer = self.node_layers[i]
            connects_count += (nodes_to_connect - nodes_in_layer) * nodes_in_layer
            nodes_to_connect -= nodes_in_layer
        # add random connection if possible
        if len(self.connects) < connects_count:
            connect_exists = True
            while connect_exists:
                # select connection input
                index = randint(0, self.first_output_index - 1)
                input_node_id = self.nodes[index].id
                input_node_layer = self.nodes[index].layer
                # select connection output in a higher layer
                for i, node in enumerate(self.nodes):
                    if node.layer > input_node_layer:
                        first_index = i
                        break
                index = randint(first_index, len(self.nodes) - 1)
                output_node_id = self.nodes[index].id
                # check connection doesn't already exist
                connect_exists = False
                for connect in self.connects:
                    if connect.key == (input_node_id, output_node_id):
                        connect_exists = True
                # disallow bias connections if not enabled
                if BIAS_ENABLED == False:
                    if input_node_id == 1:
                        connect_exists = True
            new_connect = Connect((input_node_id, output_node_id))
            self.connects.append(new_connect)

    def enable_connect(self):
        disabled_connects = []
        # create list of disabled connections
        for connect in self.connects:
            if connect.enabled == False:
                disabled_connects.append(connect)
        # enable random connection from the list
        if disabled_connects:
            index = randint(0, len(disabled_connects) - 1)
            rand_connect = disabled_connects[index]
            rand_connect.enabled = True

    def disable_connect(self):
        enabled_connects = []
        # create list of enabled connections
        for connect in self.connects:
            if connect.enabled:
                enabled_connects.append(connect)
        # disable random connection from the list
        if enabled_connects:
            index = randint(0, len(enabled_connects) - 1)
            rand_connect = enabled_connects[index]
            rand_connect.enabled = False

    def add_node(self):
        enabled_connects = []
        # create list of enabled connections not connected to bias node
        for connect in self.connects:
            if connect.enabled and connect.input_node != 1:
                enabled_connects.append(connect)
        if enabled_connects:
            # select random enabled connection
            index = randint(0, len(enabled_connects) - 1)
            rand_connect = enabled_connects[index]
            # if layer already exists, add node to random layer. otherwise, create new layer.
            input_layer = find_by_id(rand_connect.input_node, self.nodes).layer
            output_layer = find_by_id(rand_connect.output_node, self.nodes).layer
            if output_layer - input_layer > 1:
                layer = randint(input_layer + 1, output_layer - 1)
                self.node_layers[layer] += 1
            else:
                layer = output_layer
                self.node_layers.insert(layer, 1)
                # increment layer of all nodes above new layer
                for node in self.nodes:
                    if node.layer >= layer:
                        node.layer += 1
            # find new node index
            for i, node in enumerate(self.nodes):
                if node.layer > layer:
                    new_node_index = i
                    break
            # add new node
            new_node = self.create_node((rand_connect.input_node, rand_connect.output_node), layer)
            self.nodes.insert(new_node_index, new_node)
            self.first_output_index += 1
            # add new connections and disable existing connection
            new_connect = Connect((rand_connect.input_node, new_node.id), rand_connect.weight)
            self.connects.append(new_connect)
            new_connect = Connect((new_node.id, rand_connect.output_node), 1)
            self.connects.append(new_connect)
            rand_connect.enabled = False

    def remove_node(self):
        # check if hidden nodes exist
        if len(self.nodes) > NUM_INPUTS + NUM_OUTPUTS + 1:
            # select random hidden node
            index = randint(NUM_INPUTS + 1, self.first_output_index - 1)
            rand_node = self.nodes[index]
            # remove node connections
            connects_to_remove = []
            for connect in self.connects:
                if connect.input_node == rand_node.id or connect.output_node == rand_node.id:
                    connects_to_remove.append(connect)
            for connect in connects_to_remove:
                self.connects.remove(connect)
            # remove node
            self.node_layers[rand_node.layer] -= 1
            self.nodes.remove(rand_node)
            self.first_output_index -= 1

    def modify_weight(self, replace_all=False):
        if replace_all:
            replace_chance = 1
        else:
            replace_chance = MUT_REPLACE_WEIGHT
        for connect in self.connects:
            if random() < replace_chance:
                connect.weight = random() - 0.5
            else:
                connect.weight += uniform(-0.1, 0.1)

    def mutate(self):
        mutation = False
        if random() < MUT_ADD_NODE:
            self.add_node()
            mutation = True
        if random() < MUT_REMOVE_NODE:
            self.remove_node()
            mutation = True
        if random() < MUT_ADD_CONN:
            self.add_connect()
            mutation = True
        if random() < MUT_DISABLE_CONN:
            self.disable_connect()
            mutation = True
        if random() < MUT_ENABLE_CONN:
            self.enable_connect()
            mutation = True
        if random() < MUT_WEIGHTS:
            self.modify_weight()
            mutation = True
        return mutation

class Neural_network:
    def __init__(self, genome):
        self.genome = genome
        self.nodes = self.genome.nodes
        self.node_layers = self.genome.node_layers
        self.create_network()
        self.outputs = np.zeros(NUM_OUTPUTS)

    def create_network(self):
        self.reset_network()
        if self.connects:
            # sort connections by output node IDs and set current node to top of the list
            self.connects.sort(key=lambda x: x.output_node)
            input_nodes = []
            input_weights = []
            current_node_id = self.connects[0].output_node
            for connect in self.connects:
                if connect.enabled == True:
                    # for each node, link input nodes and connection weights
                    if connect.output_node is not current_node_id:
                        current_node = find_by_id(current_node_id, self.nodes)
                        current_node.link(input_nodes, input_weights)
                        input_nodes = []
                        input_weights = []
                        current_node_id = connect.output_node
                    input_nodes.append(find_by_id(connect.input_node, self.nodes))
                    input_weights.append(connect.weight)
            current_node = find_by_id(current_node_id, self.nodes)
            current_node.link(input_nodes, input_weights)

    def reset_network(self):
        self.connects = copy(self.genome.connects)
        self.first_output_index = self.genome.first_output_index
        for node in self.nodes:
            node.input_nodes = []
            node.input_weights = []

    def get_outputs(self, inputs):
        # load input values
        for i in range(NUM_INPUTS):
            self.nodes[i + 1].value = inputs[i]
        # update all node values
        for node in self.nodes:
            node.update()
        # return output values
        for i in range(NUM_OUTPUTS):
            self.outputs[i] = self.nodes[self.first_output_index + i].value
        return self.outputs

class Neat:
    def __init__(self):
        self.species = []
        self.init_genome = Genome() # create initial genome from config

    def create_genome(self):
        genome = deepcopy(self.init_genome)
        genome.modify_weight(replace_all=True)
        return genome

    def genomic_distance(self, genome1, genome2):
        connects1 = genome1.connects
        connects2 = genome2.connects
        connects1_index = 0
        connects2_index = 0
        sum_weight_diff = 0
        avg_weight_diff = 0
        self.num_homologous = 0
        num_disjoint = 0
        num_genes = max([len(connects1), len(connects2)])
        # in case no connections in either genome
        if num_genes == 0:
            return 0
        # count homologous, disjoint and excess genes
        while connects1_index < len(connects1) and connects2_index < len(connects2):
            if connects1[connects1_index].id < connects2[connects2_index].id:
                num_disjoint += 1
                connects1_index += 1
            elif connects1[connects1_index].id > connects2[connects2_index].id:
                num_disjoint += 1
                connects2_index += 1
            else:
                sum_weight_diff += abs(connects1[connects1_index].weight - connects2[connects2_index].weight)
                self.num_homologous += 1
                connects1_index += 1
                connects2_index += 1
        if connects1_index == len(connects1):
            num_excess = len(connects2[connects2_index:])
        else:
            num_excess = len(connects1[connects1_index:])
        # calculate genomic distance
        if self.num_homologous:
            avg_weight_diff = sum_weight_diff / self.num_homologous
        genomic_distance = (C1 * num_excess + C2 * num_disjoint) + C3 * avg_weight_diff
        return genomic_distance

    def crossover(self, parent1, parent2):
        if self.genomic_distance(parent1.genome, parent2.genome) < COMPAT_THRESHOLD:
            connects1_index = 0
            connects2_index = 0
            homologous_index = 0
            weak_index = 0

            # determine dominant parent
            if parent1.adj_fitness > parent2.adj_fitness:
                strong_parent = parent1
                weak_parent = parent2
            elif parent2.adj_fitness > parent1.adj_fitness:
                strong_parent = parent2
                weak_parent = parent1
            else:
                if random() < 0.5:
                    strong_parent = parent1
                    weak_parent = parent2
                else:
                    strong_parent = parent2
                    weak_parent = parent1
            connects1 = strong_parent.genome.connects
            connects2 = weak_parent.genome.connects
            # crossover parents genomes
            child_genome = deepcopy(strong_parent.genome)
            num_weak_genes = int(self.num_homologous * WEAK_RATIO)
            weak_index_list = np.random.choice(np.arange(self.num_homologous), num_weak_genes, replace=False)
            weak_index_list.sort()
            while weak_index < len(weak_index_list):
                # skip disjoint genes
                if connects1[connects1_index].id < connects2[connects2_index].id:
                    connects1_index += 1
                elif connects1[connects1_index].id > connects2[connects2_index].id:
                    connects2_index += 1
                else:
                    # crossover weights and enabled status of strong and weak homologous genes
                    if weak_index_list[weak_index] == homologous_index:
                        child_genome.connects[connects1_index].weight = connects2[connects2_index].weight
                        child_genome.connects[connects1_index].enabled = connects2[connects2_index].enabled
                        weak_index += 1
                    homologous_index += 1
                    connects1_index += 1
                    connects2_index += 1
            child_genome.mutate()
            return child_genome
        return False

    def determine_species(self, child):
        species_exists = False
        for species in self.species:
            if self.genomic_distance(child.genome, species.genome) < COMPAT_THRESHOLD:
                child.species = species
                species.population.append(child)
                species_exists = True
                break
        # if child is not compatible with existing species, create new species
        if species_exists == False:
            new_species = Species(child.genome)
            self.species.append(new_species)
            child.species = new_species
            new_species.population.append(child)

    def calculate_fitness(self, organism):
        organism.fitness_function()
        adjustment = 0
        for member in organism.species.population:
            genomic_similarity = 1 - self.genomic_distance(organism.genome, member.genome) / COMPAT_THRESHOLD
            if genomic_similarity > 0:
                adjustment += genomic_similarity
        organism.adj_fitness = organism.fitness / adjustment

    def kill(self, organism):
        for species in self.species:
            if species.id == organism.species.id:
                species.population.remove(organism)
                break

class Species:
    id = 0
    def __init__(self, genome):
        Species.id += 1
        self.id = Species.id
        self.genome = genome
        self.population = []

    def sort_by_fitness(self):
        self.population.sort(key=lambda x: x.adj_fitness, reverse=True)

def find_by_id(id, list):
    for object in list:
        if object.id == id:
            return object
    return False
