import numpy as np

from findley_evaluation_functions import evaluate_findley

# Testing biaxial residual stress plus alternating sxx
k = 1.
sa = 760

load_hist = np.zeros((2, 1, 6))
load_hist[:, :, 0] = -254.6
load_hist[:, :, 1] = -248
load_hist[0, :, 0] -= sa
load_hist[1, :, 0] += sa

print load_hist

print evaluate_findley(combined_stress=load_hist, a_cp=np.array([k]), worker_run_out_time=8000,
                       num_workers=8, chunk_size=300, search_grid=10)

