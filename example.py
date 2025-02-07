import numpy as np

def example(p1, p2, p3):
    parameters = {
        "Upper Body Resistance": p1,
        "Lower Body Resistance": p2,
        "Pulmonary Resistance": p3,
    }

    cos = {param: [] for param in parameters.keys()}  # Initialize a dictionary to store results
    
    normalized_range = np.linspace(0.5, 1.5, 5)

    for param_name, base_value in parameters.items():
        cardiac_outputs = []  # To store cardiac outputs for this parameter
            
        for factor in normalized_range:
            # Scale the parameter value
            scaled_value = base_value * factor
            
            # Replace `q_p` with actual logic to compute cardiac output if necessary
            q_p = scaled_value  # Placeholder for cardiac output calculation
            
            cardiac_outputs.append(q_p)  # Collect scaled values
            
        cos[param_name] = cardiac_outputs  # Store results in the dictionary

    return cos

# Call the function and capture the result
result = example(4, 5, 6)

# Print the result
print(result)
