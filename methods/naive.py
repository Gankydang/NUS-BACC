import numpy as np

# Constants from the problem
QUARTERS = 8  # Q1'26 to Q4'27
WEEKS_PER_QUARTER = 13

# TAM data (billions of GBs)
tam_base = np.array([21.8, 27.4, 34.9, 39.0, 44.7, 51.5, 52.5, 53.5])
tam_range = 2.0  # ±2 billion GBs

# Product specifications
gb_per_wafer = {
    'Node1': 100000,  # 100k
    'Node2': 150000,  # 150k
    'Node3': 270000   # 270k
}

# Yield data
yields = {
    'Node1': [0.98, 0.98, 0.98, 0.98, 0.98, 0.98, 0.98, 0.98],
    'Node2': [0.60, 0.82, 0.95, 0.98, 0.98, 0.98, 0.98, 0.98],
    'Node3': [0.20, 0.25, 0.35, 0.50, 0.65, 0.85, 0.95, 0.98]
}

# Initial conditions for Q1'26
initial_loading = {
    'Node1': 12000,
    'Node2': 5000,
    'Node3': 1000
}

def calculate_quarterly_output(loading, quarter):
    """Calculate total GB output for a given quarter's loading"""
    output = 0
    output += loading['Node1'] * WEEKS_PER_QUARTER * gb_per_wafer['Node1'] * yields['Node1'][quarter]
    output += loading['Node2'] * WEEKS_PER_QUARTER * gb_per_wafer['Node2'] * yields['Node2'][quarter]
    output += loading['Node3'] * WEEKS_PER_QUARTER * gb_per_wafer['Node3'] * yields['Node3'][quarter]
    return output / 1e9  # Convert to billions of GBs

def get_node_efficiency(quarter):
    """Calculate and sort nodes by their GB output efficiency (GB per wafer * yield)"""
    efficiencies = []
    for node in ['Node1', 'Node2', 'Node3']:
        efficiency = gb_per_wafer[node] * yields[node][quarter]
        efficiencies.append((node, efficiency))
    
    # Sort by efficiency in descending order
    return sorted(efficiencies, key=lambda x: x[1], reverse=True)

def adjust_loading_for_tam(prev_loading, quarter):
    """Adjust loading based on TAM deficit and node efficiency"""
    # First, calculate output with previous loading
    current_loading = prev_loading.copy()
    current_output = calculate_quarterly_output(current_loading, quarter)
    
    # Calculate TAM deficit (positive means we need more output)
    tam_target = tam_base[quarter]
    tam_deficit = tam_target - current_output
    
    # Get nodes sorted by efficiency
    node_efficiencies = get_node_efficiency(quarter)
    
    # Adjust loading based on deficit
    while abs(tam_deficit) > tam_range:
        adjustment_made = False
        
        for node, efficiency in node_efficiencies:
            # Calculate how much one wafer of this node contributes to output
            wafer_contribution = (gb_per_wafer[node] * yields[node][quarter] * WEEKS_PER_QUARTER) / 1e9
            
            if tam_deficit > 0:  # Need to increase output
                # Check if we can increase this node's loading
                if current_loading[node] < prev_loading[node] + 2500:
                    # Increase by up to 1 wafers
                    increase = min(1, int((tam_deficit / wafer_contribution) + 0.5))
                    increase = min(increase, prev_loading[node] + 2500 - current_loading[node])
                    if increase > 0:
                        current_loading[node] += increase
                        current_output = calculate_quarterly_output(current_loading, quarter)
                        tam_deficit = tam_target - current_output
                        adjustment_made = True
                        break
        
        if not adjustment_made:
            break
    
    return current_loading

def find_loading_plan():
    """Find loading plan for all quarters using TAM deficit method"""
    # Initialize results with the first quarter's known values
    results = [{
        'Node1': initial_loading['Node1'],
        'Node2': initial_loading['Node2'],
        'Node3': initial_loading['Node3']
    }]
    
    # For each subsequent quarter
    for quarter in range(1, QUARTERS):
        new_loading = adjust_loading_for_tam(results[-1], quarter)
        results.append(new_loading)
    
    return results

def print_loading_plan(loading_plan):
    """Print the loading plan in a formatted table"""
    print("\nQuarterly Loading Plan (wafers per week):")
    print("Quarter  Node1   Node2   Node3   Output(B GBs)  TAM Range")
    print("-" * 65)
    
    for quarter, loading in enumerate(loading_plan):
        output = calculate_quarterly_output(loading, quarter)
        tam_min = tam_base[quarter] - tam_range
        tam_max = tam_base[quarter] + tam_range
        print(f"Q{quarter+1}'26" if quarter < 4 else f"Q{quarter-3}'27", end="")
        print(f"    {loading['Node1']:5d}   {loading['Node2']:5d}   {loading['Node3']:5d}   ",
              f"{output:11.1f}   [{tam_min:.1f}, {tam_max:.1f}]")

def get_naive_loading_plan():
    # Find and print solution
    loading_plan = find_loading_plan()
    return loading_plan