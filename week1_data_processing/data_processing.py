import scipy.io as sio
import numpy as np

# Load hyperspectral cube and ground truth
loaded_data = sio.loadmat("salinas_corrected.mat")
cube = loaded_data["salinas_corrected"]

gt_data = sio.loadmat("salinas_gt.mat")
gt = gt_data["salinas_gt"]
