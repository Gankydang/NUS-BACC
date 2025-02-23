from docplex.mp.model import Model

# Sets and indices
quarters = list(range(8))  # Q1'26 to Q4'27
nodes = [1, 2, 3]

# Parameters
# TAM forecast in billions of GBs for each quarter
TAM = [21.8, 27.4, 34.9, 39.0, 44.7, 51.5, 52.5, 53.5]
# GB per wafer for each node
gb = {1: 100000, 2: 150000, 3: 270000}
# Yield per node per quarter
yield_dict = {
    1: [0.98] * 8,
    2: [0.60, 0.82, 0.95, 0.98, 0.98, 0.98, 0.98, 0.98],
    3: [0.20, 0.25, 0.35, 0.50, 0.65, 0.85, 0.95, 0.98]
}
# Initial weekly loading for Q1'26

initial_loading = {1: 12000, 2: 5000, 3: 1000}

def solve(mdl):
    # Decision variables: x[node,q] = weekly loading (number of wafers) for each node and quarter
    x = mdl.integer_var_dict(((node, q) for node in nodes for q in quarters), lb=0, name="x")
    # Auxiliary variables for absolute change in loading between quarters
    diff = mdl.continuous_var_dict(((node, q) for node in nodes for q in range(1, len(quarters))), lb=0, name="diff")

    # Fix initial loading for Q1'26
    for node in nodes:
        mdl.add_constraint(x[node, 0] == initial_loading[node])

    # Enforce maximum change of ±2500 wafers and capture the absolute differences
    for node in nodes:
        for q in range(1, len(quarters)):
            mdl.add_constraint(x[node, q] - x[node, q-1] <= 2500)
            mdl.add_constraint(x[node, q-1] - x[node, q] <= 2500)
            mdl.add_constraint(diff[node, q] >= x[node, q] - x[node, q-1])
            mdl.add_constraint(diff[node, q] >= x[node, q-1] - x[node, q])

    # Production constraints: total production must lie within TAM ±2 billion GB
    # Production per quarter = 13 (weeks) * x[node,q] * (GB per wafer * yield)
    for q in quarters:
        total_production = mdl.sum(13 * x[node, q] * gb[node] * yield_dict[node][q] for node in nodes)
        lower_bound = (TAM[q] - 2) * 1e9
        upper_bound = (TAM[q] + 2) * 1e9
        mdl.add_constraint(total_production >= lower_bound)
        mdl.add_constraint(total_production <= upper_bound)

    # Objective: minimize the total change in loading across quarters
    mdl.minimize(mdl.sum(diff[node, q] for node in nodes for q in range(1, len(quarters))))

    solution = mdl.solve(log_output=True)
    return solution, x


def get_docplex_barrier_loading_plan():
    # Create model
    mdl = Model("Wafer_Loading_Optimization")
    solution, x = solve(mdl)

    result = []
    my_dict = {}
    if solution:
        for q in quarters:
            my_dict = {}
            for node in nodes:
                my_dict[f'Node{node}'] = int(solution[x[node, q]])
            result.append(my_dict)
        return result
    else:
        print("No solution found")
