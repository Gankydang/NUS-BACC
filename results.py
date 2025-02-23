from methods import (
    get_docplex_barrier_loading_plan,
    get_brute_force_loading_plan,
    get_naive_loading_plan,
    get_pulp_simplex_loading_plan
)
from calculate_profits import run_analysis

docplex_loading_plan = get_docplex_barrier_loading_plan()
brute_force_loading_plan = get_brute_force_loading_plan()
naive_loading_plan = get_naive_loading_plan()
pulp_simplex_loading_plan = get_pulp_simplex_loading_plan()

print('### Docplex ###')
run_analysis(docplex_loading_plan)

print('### Pulp ###')
run_analysis(pulp_simplex_loading_plan)

print('### Naive ###')
run_analysis(naive_loading_plan)

print('### Brute Force ###')
run_analysis(brute_force_loading_plan)
