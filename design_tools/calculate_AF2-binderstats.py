import pickle
import numpy as np
from scipy.special import softmax
import sys

if len(sys.argv) != 3:
    print("Usage: python script_name.py path_to_pickle_file binderlength")
    sys.exit(1)

pickle_file = sys.argv[1]
binderlen = int(sys.argv[2])

try:
    feature_dict = pickle.load(open(pickle_file, 'rb'))
except FileNotFoundError:
    print("File not found.")
    sys.exit(1)

# Calculate alignment error of binder relative to target
pae = feature_dict['predicted_aligned_error']
pae_interaction1 = np.mean(pae[:binderlen, binderlen:])
pae_interaction2 = np.mean(pae[binderlen:, :binderlen])
pae_interaction_total = (pae_interaction1 + pae_interaction2) / 2

# Calculate overall confidence in derived structures
plddt = feature_dict['plddt']
plddt_binder = np.mean(plddt[:binderlen])
plddt_target = np.mean(plddt[binderlen:])

# Calculate fraction of binder <8A from target
bin_edges = feature_dict["distogram"]["bin_edges"]
bin_edges = np.insert(bin_edges, 0, 0)

distogram_softmax = softmax(feature_dict["distogram"]["logits"], axis=2)
distance_predictions = np.sum(np.multiply(distogram_softmax, bin_edges), axis=2)
#binder_dist = np.mean(distance_predictions[:binderlen, binderlen:])
#target_dist = np.mean(distance_predictions[binderlen:, :binderlen])
upper_right_quad = distance_predictions[:binderlen, binderlen:]
num_total_points = upper_right_quad.size
num_points_less_than_8 = np.sum(upper_right_quad < 8)
fraction = num_points_less_than_8 / num_total_points

print(pickle_file,"\t",pae_interaction_total,"\t",plddt_binder,"\t",plddt_target,"\t",num_points_less_than_8,"\t",num_total_points,"\t",fraction)

