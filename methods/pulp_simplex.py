import pulp

# Define the quarters and nodes
quarters = [1, 2, 3, 4, 5, 6, 7, 8]
nodes = [1, 2, 3]

# Initial weekly loading for Q1'26 (given)
initial_loading = {1: {1: 12000, 2: 5000, 3: 1000}}

# Yield data for each node and quarter (from Table 2)
yield_data = {
    1: {1: 0.98, 2: 0.60, 3: 0.20},  # Q1'26
    2: {1: 0.98, 2: 0.82, 3: 0.25},  # Q2'26
    3: {1: 0.98, 2: 0.95, 3: 0.35},  # Q3'26
    4: {1: 0.98, 2: 0.98, 3: 0.50},  # Q4'26
    5: {1: 0.98, 2: 0.98, 3: 0.65},  # Q1'27
    6: {1: 0.98, 2: 0.98, 3: 0.85},  # Q2'27
    7: {1: 0.98, 2: 0.98, 3: 0.95},  # Q3'27
    8: {1: 0.98, 2: 0.98, 3: 0.98}   # Q4'27
}

# GB per wafer for each node
GB_per_wafer = {1: 100000, 2: 150000, 3: 270000}

# TAM for each quarter (in billions, convert to GB by multiplying by 1e9)
TAM = {
    1: 21.8e9,
    2: 27.4e9,
    3: 34.9e9,
    4: 39.0e9,
    5: 44.7e9,
    6: 51.5e9,
    7: 52.5e9,
    8: 53.5e9,
}

def solve(prob):
    # Decision variables: L[q][n] for each quarter and node.
    # For Q1, values are fixed. For Q2-Q8, define as continuous variables (could be set as integer if needed).
    L = {}
    for q in quarters:
        L[q] = {}
        for n in nodes:
            if q == 1:
                L[q][n] = initial_loading[1][n]
            else:
                L[q][n] = pulp.LpVariable(f"L_{q}_{n}", lowBound=0, cat="Continuous")

    # Auxiliary variables for absolute change between quarters
    d = {}
    for q in quarters:
        if q == 1:
            continue
        d[q] = {}
        for n in nodes:
            d[q][n] = pulp.LpVariable(f"d_{q}_{n}", lowBound=0, cat="Continuous")

    # Objective: Minimize the total change in wafer loading across quarters
    prob += pulp.lpSum(d[q][n] for q in quarters if q != 1 for n in nodes)

    # Production constraints: For each quarter except Q1, total GB output must equal TAM.
    for q in quarters:
        if q == 1:
            continue  # Skip Q1 as loading is fixed.
        production = 13 * (
            L[q][1] * GB_per_wafer[1] * yield_data[q][1] +
            L[q][2] * GB_per_wafer[2] * yield_data[q][2] +
            L[q][3] * GB_per_wafer[3] * yield_data[q][3]
        )
        prob += production == TAM[q], f"Production_Q{q}"

    # Loading change constraints: For q>=2, the change in loading cannot exceed 2500 wafers.
    for q in quarters:
        if q == 1:
            continue
        for n in nodes:
            prob += L[q][n] - L[q-1][n] <= 2500, f"Increase_Q{q}_Node{n}"
            prob += L[q-1][n] - L[q][n] <= 2500, f"Decrease_Q{q}_Node{n}"
            # Link the auxiliary variable to the absolute difference
            prob += d[q][n] >= L[q][n] - L[q-1][n], f"Abs_Pos_Q{q}_Node{n}"
            prob += d[q][n] >= L[q-1][n] - L[q][n], f"Abs_Neg_Q{q}_Node{n}"

    # Solve the optimization problem
    prob.solve()

    return L

def get_pulp_simplex_loading_plan():
    # Create the LP problem (minimization)
    prob = pulp.LpProblem("Minimize_Wafer_Change", pulp.LpMinimize)
    L = solve(prob)

    result = []
    my_dict = {}
    for q in quarters:
        my_dict = {}
        for i, n in enumerate(nodes, start=1):
            my_dict[f'Node{i}'] = int(pulp.value(L[q][n]))
        result.append(my_dict)

    return result