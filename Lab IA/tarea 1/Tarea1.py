# Imports
from pgmpy.estimators import PC, HillClimbSearch
from pgmpy.utils import get_example_model
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.models import DiscreteBayesianNetwork
from IPython.display import Image
import networkx as nx
import numpy as np
from sklearn.metrics import f1_score
import pprint
import random

# Load the model
water_model = get_example_model('water')

# Visualize the network
viz = water_model.to_graphviz()
viz.draw('water.png', prog='dot')
Image('water.png')
viz.close()

nodes = water_model.nodes()    #Devuelve nodos del grafo
edges = water_model.edges()    #Devuelve aristas del grafo
cpds = water_model.get_cpds()  #Devuelve lista de objetos del modelo

print(f"Nodes in the model: {nodes} \n")
print(f"Edges in the model: {edges} \n")
print(f"A subset of CPDs in the model: ")
pprint.pp(cpds)

water_samples = water_model.simulate(10000)
water_samples.head()
pprint.pp(water_samples)


def get_f1_score(estimated_model, true_model):
    nodes = estimated_model.nodes()
    est_adj = nx.to_numpy_array(
        estimated_model.to_undirected(), nodelist=nodes, weight=None
    )
    true_adj = nx.to_numpy_array(
        true_model.to_undirected(), nodelist=nodes, weight=None
    )

    f1 = f1_score(np.ravel(true_adj), np.ravel(est_adj))
    print("F1-score for the model skeleton: ", f1)

#Structure learning

# PC learning method
est_pc = PC(data=water_samples)
estimated_model_pc = est_pc.estimate(ci_test='chi_square', variant="stable", max_cond_vars=4, return_type='dag')
get_f1_score(estimated_model_pc, water_model)

# HillClimbSearch method
est_HillClimbSearch = HillClimbSearch(data=water_samples)
estimated_model_HillClimbSearch = est_HillClimbSearch.estimate(scoring_method="k2", max_indegree=4, max_iter=int(1e4))
get_f1_score(estimated_model_HillClimbSearch, water_model)

#Parameters
new_model = DiscreteBayesianNetwork(ebunch=edges)
