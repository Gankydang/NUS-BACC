
# calculate profits
import numpy as np
from math import ceil

# Constants from part 1a
QUARTERS = 8
WEEKS_PER_QUARTER = 13

# TAM and pricing data
tam_base = np.array([21.8, 27.4, 34.9, 39.0, 44.7, 51.5, 52.5, 53.5])
contribution_margin_per_gb = 0.002  # $0.002 per GB

# Tool information
workstations = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

initial_tool_count = {
    'A': 10, 'B': 18, 'C': 5, 'D': 11, 'E': 15,
    'F': 2, 'G': 23, 'H': 3, 'I': 4, 'J': 1
}

utilization = {
    'A': 0.78, 'B': 0.76, 'C': 0.80, 'D': 0.80, 'E': 0.76,
    'F': 0.80, 'G': 0.70, 'H': 0.85, 'I': 0.75, 'J': 0.60
}

capex_per_tool = {
    'A': 3.0, 'B': 6.0, 'C': 2.2, 'D': 3.0, 'E': 3.5,
    'F': 6.0, 'G': 2.1, 'H': 1.8, 'I': 3.0, 'J': 8.0
}  # In millions USD

# Minute load for each node at each workstation
minute_load = {
    'Node1': {'A': 4.0, 'B': 6.0, 'C': 2.0, 'D': 5.0, 'E': 5.0, 'F': 0, 'G': 12.0, 'H': 2.1, 'I': 0, 'J': 0},
    'Node2': {'A': 4.0, 'B': 9.0, 'C': 2.0, 'D': 5.0, 'E': 10, 'F': 1.8, 'G': 0, 'H': 0, 'I': 6.0, 'J': 0},
    'Node3': {'A': 4.0, 'B': 15.0, 'C': 5.4, 'D': 0, 'E': 0, 'F': 5.8, 'G': 16.0, 'H': 0, 'I': 0, 'J': 2.1}
}

def calculate_tool_requirement(loading, workstation):
    """Calculate tool requirement for a workstation based on loading"""
    total_time = 0
    for node in ['Node1', 'Node2', 'Node3']:
        if minute_load[node][workstation] > 0:
            total_time += loading[node] * minute_load[node][workstation]
    
    available_minutes = 7 * 24 * 60 * utilization[workstation]  # Weekly available minutes
    return total_time / available_minutes

def calculate_quarterly_tools_needed(loading):
    """Calculate tools needed for each workstation in a quarter"""
    tools_needed = {}
    for ws in workstations:
        requirement = calculate_tool_requirement(loading, ws)
        tools_needed[ws] = ceil(requirement)  # Round up to nearest integer
    return tools_needed

def calculate_capex(prev_tools, current_tools):
    """Calculate CAPEX needed based on difference in tool requirements"""
    capex = 0
    for ws in workstations:
        if current_tools[ws] >= prev_tools[ws]:
            additional_tools = current_tools[ws] - prev_tools[ws]
            capex += additional_tools * capex_per_tool[ws]
    return capex

def calculate_quarterly_output(loading, quarter):
    """Calculate total GB output for a given quarter's loading (from part 1a)"""
    output = 0
    output += loading['Node1'] * WEEKS_PER_QUARTER * 100000 * 0.98  # Node1
    output += loading['Node2'] * WEEKS_PER_QUARTER * 150000 * yields['Node2'][quarter]  # Node2
    output += loading['Node3'] * WEEKS_PER_QUARTER * 270000 * yields['Node3'][quarter]  # Node3
    return output / 1e9  # Convert to billions of GBs

# Yield data from part 1a
yields = {
    'Node2': [0.60, 0.82, 0.95, 0.98, 0.98, 0.98, 0.98, 0.98],
    'Node3': [0.20, 0.25, 0.35, 0.50, 0.65, 0.85, 0.95, 0.98]
}

def analyze_loading_plan(loading_plan):
    """Analyze loading plan to calculate tools, CAPEX, and profit"""
    current_tools = initial_tool_count.copy()
    total_capex = 0
    quarterly_results = []
    
    for quarter, loading in enumerate(loading_plan):
        # Calculate tool requirements
        tools_needed = calculate_quarterly_tools_needed(loading)
        
        # Calculate CAPEX for this quarter
        quarter_capex = calculate_capex(current_tools, tools_needed)
        total_capex += quarter_capex
        
        # Calculate output and revenue
        output = calculate_quarterly_output(loading, quarter)
        revenue = output * 1e9 * contribution_margin_per_gb  # Convert back to GB for revenue calc
        
        # Store results
        quarterly_results.append({
            'quarter': quarter,
            'loading': loading,
            'tools_needed': tools_needed,
            'capex': quarter_capex,
            'output': output,
            'revenue': revenue
        })
        
        # Update current tools for next quarter
        current_tools = tools_needed.copy()
    
    return quarterly_results, total_capex

def print_analysis(results, total_capex):
    """Print detailed analysis results"""
    print("\nQuarterly Analysis:")
    print("Quarter  Output(B GB)  Revenue($M)  CAPEX($M)  Net($M)")
    print("-" * 60)
    
    total_revenue = 0
    for res in results:
        q = res['quarter']
        quarter_name = f"Q{q+1}'26" if q < 4 else f"Q{q-3}'27"
        revenue = res['revenue'] / 1e6  # Convert to millions
        capex = res['capex']
        net = revenue - capex
        total_revenue += revenue
        
        print(f"{quarter_name:8} {res['output']:11.1f} {revenue:11.1f} {capex:10.1f} {net:9.1f}")
    
    print("\nTool Requirements by Quarter:")
    print("Quarter ", end="")
    for ws in workstations:
        print(f"{ws:4}", end="")
    print()
    print("-" * 50)
    
    for res in results:
        q = res['quarter']
        quarter_name = f"Q{q+1}'26" if q < 4 else f"Q{q-3}'27"
        print(f"{quarter_name:8}", end="")
        for ws in workstations:
            print(f"{res['tools_needed'][ws]:4}", end="")
        print()
    
    print(f"\nTotal Revenue: ${total_revenue:.1f}M")
    print(f"Total CAPEX: ${total_capex:.1f}M")
    print(f"Net Profit: ${(total_revenue - total_capex):.1f}M")


def run_analysis(loading_plan):
    results, total_capex = analyze_loading_plan(loading_plan)
    print_analysis(results, total_capex)
    print()

