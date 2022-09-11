# initial genomes
NUM_INPUTS = 2
NUM_HIDDEN = 0
NUM_OUTPUTS = 4
INIT_CONNECTS = 'unconnected'

# bias
BIAS_ENABLED = True

# activation function
ACTIVATION_FUNCTION = 'sigmoid'

# genomic compatibility
C1 = 1
C2 = 1
C3 = 0.4
COMPAT_THRESHOLD = 10

# crossover
WEAK_RATIO = 0.5

# mutations rates
MUT_ADD_NODE = 0.01
MUT_REMOVE_NODE = 0.01
MUT_ADD_CONN = 0.2
MUT_DISABLE_CONN = 0.2
MUT_ENABLE_CONN = 0.2
MUT_WEIGHTS = 0.8
MUT_REPLACE_WEIGHT = 0.1