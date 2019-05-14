import numpy as np

from findley_evaluation_functions import evaluate_findley

# Testing biaxial residual stress plus alternating sxx
k = 0.65
sa = 760.

load_hist = np.zeros((2, 1, 6))
load_hist[0, :, 0] = -250
load_hist[1, :, 0] = 650

print load_hist
print evaluate_findley(combined_stress=load_hist, a_cp=np.array([k]), worker_run_out_time=8000,
                       num_workers=8, chunk_size=300, search_grid=1)

sa = 760.

load_hist = np.zeros((2, 1, 6))
load_hist[0, 0, 0] = -40
load_hist[1, 0, 0] = 455

load_hist[0, 0, 1] = -10
load_hist[1, 0, 1] = 220

load_hist[0, 0, 2] = -140
load_hist[1, 0, 2] = -48

load_hist[0, 0, 3] = 25
load_hist[1, 0, 3] = -310


print load_hist

print evaluate_findley(combined_stress=load_hist, a_cp=np.array([k]*3), worker_run_out_time=8000,
                       num_workers=8, chunk_size=300, search_grid=1)
