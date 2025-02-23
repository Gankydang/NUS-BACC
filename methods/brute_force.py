# Brute force
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

def is_valid_transition(prev_loading, new_loading):
    """Check if the transition between quarters is valid (≤2.5k wafer change)"""
    for node in ['Node1', 'Node2', 'Node3']:
        if abs(new_loading[node] - prev_loading[node]) > 2500:
            return False
    return True

def is_within_tam_range(output, quarter):
    """Check if output is within the acceptable TAM range"""
    return (tam_base[quarter] - tam_range) <= output <= (tam_base[quarter] + tam_range)

def find_valid_loading():
    """Find a valid loading profile for all quarters"""
    # Initialize results with the first quarter's known values
    results = [{
        'Node1': initial_loading['Node1'],
        'Node2': initial_loading['Node2'],
        'Node3': initial_loading['Node3']
    }]
    
    # For each subsequent quarter
    for quarter in range(1, QUARTERS):
        found_valid = False
        
        rangee = 1500
        step = 500

        # Try different loading combinations
        for n1 in range(max(0, results[-1]['Node1'] - rangee), results[-1]['Node1'] + rangee + 1, step):
            for n2 in range(max(0, results[-1]['Node2'] - rangee), results[-1]['Node2'] + rangee + 1, step):
                for n3 in range(max(0, results[-1]['Node3'] - rangee), results[-1]['Node3'] + rangee + 1, step):
                    current_loading = {'Node1': n1, 'Node2': n2, 'Node3': n3}
                    
                    # Calculate output and check constraints
                    output = calculate_quarterly_output(current_loading, quarter)
                    
                    if (is_within_tam_range(output, quarter) and 
                        is_valid_transition(results[-1], current_loading)):
                        results.append(current_loading)
                        found_valid = True
                        break
                if found_valid:
                    break
            if found_valid:
                break
                
        if not found_valid:
            print(f"Could not find valid loading for quarter {quarter + 1}")
            return None
            
    return results

def print_loading_plan(loading_plan):
    """Print the loading plan in a formatted table"""
    if loading_plan is None:
        return
        
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

def get_brute_force_loading_plan():
    return find_valid_loading()

