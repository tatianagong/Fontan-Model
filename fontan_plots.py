# Get Dependencies
import pandas as pd
import numpy as np
import math as math
import seaborn as sns
import matplotlib.pyplot as plt   
import scipy.optimize
import os


def fun_flows(variables, *param):

    ( UVR,LVR, PVR, HR, C_d, C_s,C_sa,C_pv,C_pa) = param
    ( Q_v, Q_u, Q_l, Q_p, P_sa, P_pa, P_pv ) = variables

    eqn_a01 = Q_v - HR *( C_d * P_pv - C_s * P_sa)
    eqn_a02 = Q_u + Q_l - Q_v
    eqn_a03 = Q_p - Q_v
    eqn_a04 = PVR * Q_p - (P_pa - P_pv)
    eqn_a05 = UVR * Q_u - (P_sa - P_pa)
    eqn_a06 = LVR * Q_l - (P_sa - P_pa)
    eqn_a07 = 1 - ( C_sa * P_sa + C_pv * P_pv + C_pa * P_pa)  
    return [eqn_a01, eqn_a02, eqn_a03, eqn_a04, eqn_a05, eqn_a06, eqn_a07]

def fun_sat(variables, *param):
    
    ( Q_p, Q_u, Q_l, S_sa, CVO2u, CVO2l, Hb) = param
    ( S_pa, S_pv, S_svu, S_svl ) = variables
    
    eqn_s1 = CVO2u - 1.34 * Hb / 100 * Q_u * 1000 * (S_sa - S_svu)
    eqn_s2 = CVO2l - 1.34 * Hb / 100 * Q_l * 1000 *(S_sa - S_svl)
    eqn_s3 = Q_p * S_pa - (Q_u * S_svu + Q_l * S_svl)
    eqn_s4 = S_sa - S_pv
    return [eqn_s1, eqn_s2, eqn_s3, eqn_s4]

def complete_results(UVR, LVR, PVR, HR, C_d, C_s, C_sa, C_pv,C_pa, z0_flows, S_sa, CVO2u, CVO2l, Hb, z0_sat):
    
    param_flows = ( UVR, LVR, PVR, HR, C_d, C_s, C_sa,C_pv,C_pa )

    result_flows = scipy.optimize.fsolve(fun_flows, z0_flows, args=param_flows, full_output=True, xtol=1e-4, maxfev=1000, factor=0.1) 
    ( Q_v, Q_u, Q_l, Q_p, P_sa, P_pv, P_pa  ) = result_flows[0]

    param_sat = ( Q_p, Q_u, Q_l, S_sa, CVO2u, CVO2l, Hb)

    result_O2_sat = scipy.optimize.fsolve(fun_sat, z0_sat, args=param_sat, full_output=True, xtol=1e-4, maxfev=1000, factor=0.1) 
    ( S_pa, S_svu, S_svu, S_svl ) = result_O2_sat[0]

    OER = (Q_u * (S_sa - S_svu) + Q_l * (S_sa - S_svl))/ ((Q_u + Q_l) * S_sa)

    return {
        "Q_v": Q_v,
        "Q_u": Q_u,
        "Q_l": Q_l,
        "Q_p": Q_p,
        "P_sa": P_sa,
        "P_pv": P_pv,
        "P_pa": P_pa,
        "S_pa": S_pa,
        "S_svu": S_svu,
        "S_svl": S_svl,
        "OER": OER,
        
    }

###
#def plotCO(UVR, LVR, PVR, HR, C_d, C_s, C_sa, C_pv, C_pa, z0_flows, S_sa, CVO2u, CVO2l, Hb, z0_sat):
# the line above should be used once I figure out a way to pass the values from the sliders into inputs, but before that, we will keep it as is with these values
from hlhs_model import C_d, C_s, C_sa, C_pv, C_pa
def plotCO(UVR=45, LVR=35, PVR=10, HR=100, C_d=C_d, C_s=C_s, C_sa=C_sa, C_pv=C_pv, C_pa=C_pa, z0_flows=(3.1, 1.5, 1.5, 3.2, 75, 26, 2.5), S_sa=0.99, CVO2u=70, CVO2l=50, Hb=15, z0_sat=(0.55, 0.99, 0.55, 0.55)):
    # Parameters to vary
    parameters = {
        "Upper Body Resistance": UVR,
        "Lower Body Resistance": LVR,
        "Pulmonary Resistance": PVR,
        "Heart Rate": HR,
        "Compliance at Dia": C_d,
        "Compliance at Sys": C_s,
        "Compliance of Sys Artery Over Vol": C_sa,
        "Compliance of Plm Vein Over Vol": C_pv,
        "Compliance of Plm Artery Over Vol": C_pa,
        "Oxygen Consumption of Upper Body": CVO2u,
        "Oxygen Consumption of Lower Body": CVO2l,
        "Systemic Arterial Oxygen Saturation": S_sa,  # ✅ Added S_sa
        "Hemoglobin Concentration": Hb  # ✅ Added Hb
    }
    
    COs = {param: [] for param in parameters.keys()}  # Initialize a dictionary to store results

    # Normalized range for the x-axis (0.5 to 1.5)
    normalized_range = np.linspace(0.5, 1.5, 50)

    # Iterate through each parameter
    for param_name, base_value in parameters.items():
        cardiac_outputs = []  # To store cardiac outputs for this parameter
        
        for factor in normalized_range:
            # Scale the parameter value
            scaled_value = base_value * factor
            
            # Create updated parameter set
            updated_params = {**parameters, param_name: scaled_value}
            
            try:
                # Calculate cardiac output
                results = complete_results(
                    updated_params["Upper Body Resistance"], updated_params["Lower Body Resistance"], updated_params["Pulmonary Resistance"], 
                    updated_params["Heart Rate"], updated_params["Compliance at Dia"], updated_params["Compliance at Sys"], 
                    updated_params["Compliance of Sys Artery Over Vol"], updated_params["Compliance of Plm Vein Over Vol"], updated_params["Compliance of Plm Artery Over Vol"], 
                    z0_flows, updated_params["Systemic Arterial Oxygen Saturation"], updated_params["Oxygen Consumption of Upper Body"], updated_params["Oxygen Consumption of Lower Body"], updated_params["Hemoglobin Concentration"], z0_sat
                )
                #Q_p = results[3]  # Cardiac output
                Q_p = results.get("Q_p", float('nan'))
                cardiac_outputs.append(Q_p)
            except ValueError:
                # If the solver fails, append NaN
                cardiac_outputs.append(float('nan'))
        
        COs[param_name] = cardiac_outputs  # Store results in the dictionary
    return COs

def plotQU(UVR=45, LVR=35, PVR=10, HR=100, C_d=C_d, C_s=C_s, C_sa=C_sa, C_pv=C_pv, C_pa=C_pa, z0_flows=(3.1, 1.5, 1.5, 3.2, 75, 26, 2.5), S_sa=0.99, CVO2u=70, CVO2l=50, Hb=15, z0_sat=(0.55, 0.99, 0.55, 0.55)):
    # Parameters to vary
    parameters = {
        "Upper Body Resistance": UVR,
        "Lower Body Resistance": LVR,
        "Pulmonary Resistance": PVR,
        "Heart Rate": HR,
        "Compliance at Dia": C_d,
        "Compliance at Sys": C_s,
        "Compliance of Sys Artery Over Vol": C_sa,
        "Compliance of Plm Vein Over Vol": C_pv,
        "Compliance of Plm Artery Over Vol": C_pa,
        "Oxygen Consumption of Upper Body": CVO2u,
        "Oxygen Consumption of Lower Body": CVO2l,
        "Systemic Arterial Oxygen Saturation": S_sa,  # ✅ Added S_sa
        "Hemoglobin Concentration": Hb  # ✅ Added Hb
    }
    
    QUs = {param: [] for param in parameters.keys()}  # Initialize a dictionary to store results

    # Normalized range for the x-axis (0.5 to 1.5)
    normalized_range = np.linspace(0.5, 1.5, 50)

    # Iterate through each parameter
    for param_name, base_value in parameters.items():
        QU_outputs = []  # To store cardiac outputs for this parameter
        
        for factor in normalized_range:
            # Scale the parameter value
            scaled_value = base_value * factor
            
            # Create updated parameter set
            updated_params = {**parameters, param_name: scaled_value}
            
            try:
                # Calculate cardiac output
                results = complete_results(
                    updated_params["Upper Body Resistance"], updated_params["Lower Body Resistance"], updated_params["Pulmonary Resistance"], 
                    updated_params["Heart Rate"], updated_params["Compliance at Dia"], updated_params["Compliance at Sys"], 
                    updated_params["Compliance of Sys Artery Over Vol"], updated_params["Compliance of Plm Vein Over Vol"], updated_params["Compliance of Plm Artery Over Vol"], 
                    z0_flows, updated_params["Systemic Arterial Oxygen Saturation"], updated_params["Oxygen Consumption of Upper Body"], updated_params["Oxygen Consumption of Lower Body"], updated_params["Hemoglobin Concentration"], z0_sat
                )
                Q_u = results.get("Q_u", float('nan'))
                QU_outputs.append(Q_u)
            except ValueError:
                # If the solver fails, append NaN
                QU_outputs.append(float('nan'))
        
        QUs[param_name] = QU_outputs  # Store results in the dictionary
    return QUs

def plotQL(UVR=45, LVR=35, PVR=10, HR=100, C_d=C_d, C_s=C_s, C_sa=C_sa, C_pv=C_pv, C_pa=C_pa, z0_flows=(3.1, 1.5, 1.5, 3.2, 75, 26, 2.5), S_sa=0.99, CVO2u=70, CVO2l=50, Hb=15, z0_sat=(0.55, 0.99, 0.55, 0.55)):
    # Parameters to vary
    parameters = {
        "Upper Body Resistance": UVR,
        "Lower Body Resistance": LVR,
        "Pulmonary Resistance": PVR,
        "Heart Rate": HR,
        "Compliance at Dia": C_d,
        "Compliance at Sys": C_s,
        "Compliance of Sys Artery Over Vol": C_sa,
        "Compliance of Plm Vein Over Vol": C_pv,
        "Compliance of Plm Artery Over Vol": C_pa,
        "Oxygen Consumption of Upper Body": CVO2u,
        "Oxygen Consumption of Lower Body": CVO2l,
        "Systemic Arterial Oxygen Saturation": S_sa,  # ✅ Added S_sa
        "Hemoglobin Concentration": Hb  # ✅ Added Hb
    }
    
    QLs = {param: [] for param in parameters.keys()}  # Initialize a dictionary to store results

    # Normalized range for the x-axis (0.5 to 1.5)
    normalized_range = np.linspace(0.5, 1.5, 50)

    # Iterate through each parameter
    for param_name, base_value in parameters.items():
        QL_outputs = []  # To store cardiac outputs for this parameter
        
        for factor in normalized_range:
            # Scale the parameter value
            scaled_value = base_value * factor
            
            # Create updated parameter set
            updated_params = {**parameters, param_name: scaled_value}
            
            try:
                # Calculate cardiac output
                results = complete_results(
                    updated_params["Upper Body Resistance"], updated_params["Lower Body Resistance"], updated_params["Pulmonary Resistance"], 
                    updated_params["Heart Rate"], updated_params["Compliance at Dia"], updated_params["Compliance at Sys"], 
                    updated_params["Compliance of Sys Artery Over Vol"], updated_params["Compliance of Plm Vein Over Vol"], updated_params["Compliance of Plm Artery Over Vol"], 
                    z0_flows, updated_params["Systemic Arterial Oxygen Saturation"], updated_params["Oxygen Consumption of Upper Body"], updated_params["Oxygen Consumption of Lower Body"], updated_params["Hemoglobin Concentration"], z0_sat
                )
                Q_l = results.get("Q_l", float('nan'))
                QL_outputs.append(Q_l)
            except ValueError:
                # If the solver fails, append NaN
                QL_outputs.append(float('nan'))
        
        QLs[param_name] = QL_outputs  # Store results in the dictionary
    return QLs

def plotQP(UVR=45, LVR=35, PVR=10, HR=100, C_d=C_d, C_s=C_s, C_sa=C_sa, C_pv=C_pv, C_pa=C_pa, z0_flows=(3.1, 1.5, 1.5, 3.2, 75, 26, 2.5), S_sa=0.99, CVO2u=70, CVO2l=50, Hb=15, z0_sat=(0.55, 0.99, 0.55, 0.55)):
    # Parameters to vary
    parameters = {
        "Upper Body Resistance": UVR,
        "Lower Body Resistance": LVR,
        "Pulmonary Resistance": PVR,
        "Heart Rate": HR,
        "Compliance at Dia": C_d,
        "Compliance at Sys": C_s,
        "Compliance of Sys Artery Over Vol": C_sa,
        "Compliance of Plm Vein Over Vol": C_pv,
        "Compliance of Plm Artery Over Vol": C_pa,
        "Oxygen Consumption of Upper Body": CVO2u,
        "Oxygen Consumption of Lower Body": CVO2l,
        "Systemic Arterial Oxygen Saturation": S_sa,  # ✅ Added S_sa
        "Hemoglobin Concentration": Hb  # ✅ Added Hb
    }
    
    QPs = {param: [] for param in parameters.keys()}  # Initialize a dictionary to store results

    # Normalized range for the x-axis (0.5 to 1.5)
    normalized_range = np.linspace(0.5, 1.5, 50)

    # Iterate through each parameter
    for param_name, base_value in parameters.items():
        QP_outputs = []  # To store cardiac outputs for this parameter
        
        for factor in normalized_range:
            # Scale the parameter value
            scaled_value = base_value * factor
            
            # Create updated parameter set
            updated_params = {**parameters, param_name: scaled_value}
            
            try:
                # Calculate cardiac output
                results = complete_results(
                    updated_params["Upper Body Resistance"], updated_params["Lower Body Resistance"], updated_params["Pulmonary Resistance"], 
                    updated_params["Heart Rate"], updated_params["Compliance at Dia"], updated_params["Compliance at Sys"], 
                    updated_params["Compliance of Sys Artery Over Vol"], updated_params["Compliance of Plm Vein Over Vol"], updated_params["Compliance of Plm Artery Over Vol"], 
                    z0_flows, updated_params["Systemic Arterial Oxygen Saturation"], updated_params["Oxygen Consumption of Upper Body"], updated_params["Oxygen Consumption of Lower Body"], updated_params["Hemoglobin Concentration"], z0_sat
                )
                Q_p = results.get("Q_p", float('nan'))
                QP_outputs.append(Q_p)
            except ValueError:
                # If the solver fails, append NaN
                QP_outputs.append(float('nan'))
        
        QPs[param_name] = QP_outputs  # Store results in the dictionary
    return QPs

def plotPSA(UVR=45, LVR=35, PVR=10, HR=100, C_d=C_d, C_s=C_s, C_sa=C_sa, C_pv=C_pv, C_pa=C_pa, z0_flows=(3.1, 1.5, 1.5, 3.2, 75, 26, 2.5), S_sa=0.99, CVO2u=70, CVO2l=50, Hb=15, z0_sat=(0.55, 0.99, 0.55, 0.55)):
    # Parameters to vary
    parameters = {
        "Upper Body Resistance": UVR,
        "Lower Body Resistance": LVR,
        "Pulmonary Resistance": PVR,
        "Heart Rate": HR,
        "Compliance at Dia": C_d,
        "Compliance at Sys": C_s,
        "Compliance of Sys Artery Over Vol": C_sa,
        "Compliance of Plm Vein Over Vol": C_pv,
        "Compliance of Plm Artery Over Vol": C_pa,
        "Oxygen Consumption of Upper Body": CVO2u,
        "Oxygen Consumption of Lower Body": CVO2l,
        "Systemic Arterial Oxygen Saturation": S_sa,  # ✅ Added S_sa
        "Hemoglobin Concentration": Hb  # ✅ Added Hb
    }
    
    PSAs = {param: [] for param in parameters.keys()}  # Initialize a dictionary to store results

    # Normalized range for the x-axis (0.5 to 1.5)
    normalized_range = np.linspace(0.5, 1.5, 50)

    # Iterate through each parameter
    for param_name, base_value in parameters.items():
        PSA_outputs = []  # To store cardiac outputs for this parameter
        
        for factor in normalized_range:
            # Scale the parameter value
            scaled_value = base_value * factor
            
            # Create updated parameter set
            updated_params = {**parameters, param_name: scaled_value}
            
            try:
                # Calculate cardiac output
                results = complete_results(
                    updated_params["Upper Body Resistance"], updated_params["Lower Body Resistance"], updated_params["Pulmonary Resistance"], 
                    updated_params["Heart Rate"], updated_params["Compliance at Dia"], updated_params["Compliance at Sys"], 
                    updated_params["Compliance of Sys Artery Over Vol"], updated_params["Compliance of Plm Vein Over Vol"], updated_params["Compliance of Plm Artery Over Vol"], 
                    z0_flows, updated_params["Systemic Arterial Oxygen Saturation"], updated_params["Oxygen Consumption of Upper Body"], updated_params["Oxygen Consumption of Lower Body"], updated_params["Hemoglobin Concentration"], z0_sat
                )
                P_sa = results.get("P_sa", float('nan'))
                PSA_outputs.append(P_sa)
            except ValueError:
                # If the solver fails, append NaN
                PSA_outputs.append(float('nan'))
        
        PSAs[param_name] = PSA_outputs  # Store results in the dictionary
    return PSAs


def plotPPV(UVR=45, LVR=35, PVR=10, HR=100, C_d=C_d, C_s=C_s, C_sa=C_sa, C_pv=C_pv, C_pa=C_pa, z0_flows=(3.1, 1.5, 1.5, 3.2, 75, 26, 2.5), S_sa=0.99, CVO2u=70, CVO2l=50, Hb=15, z0_sat=(0.55, 0.99, 0.55, 0.55)):
    # Parameters to vary
    parameters = {
        "Upper Body Resistance": UVR,
        "Lower Body Resistance": LVR,
        "Pulmonary Resistance": PVR,
        "Heart Rate": HR,
        "Compliance at Dia": C_d,
        "Compliance at Sys": C_s,
        "Compliance of Sys Artery Over Vol": C_sa,
        "Compliance of Plm Vein Over Vol": C_pv,
        "Compliance of Plm Artery Over Vol": C_pa,
        "Oxygen Consumption of Upper Body": CVO2u,
        "Oxygen Consumption of Lower Body": CVO2l,
        "Systemic Arterial Oxygen Saturation": S_sa,  # ✅ Added S_sa
        "Hemoglobin Concentration": Hb  # ✅ Added Hb
    }
    
    PPVs = {param: [] for param in parameters.keys()}  # Initialize a dictionary to store results

    # Normalized range for the x-axis (0.5 to 1.5)
    normalized_range = np.linspace(0.5, 1.5, 50)

    # Iterate through each parameter
    for param_name, base_value in parameters.items():
        PPV_outputs = []  # To store cardiac outputs for this parameter
        
        for factor in normalized_range:
            # Scale the parameter value
            scaled_value = base_value * factor
            
            # Create updated parameter set
            updated_params = {**parameters, param_name: scaled_value}
            
            try:
                # Calculate cardiac output
                results = complete_results(
                    updated_params["Upper Body Resistance"], updated_params["Lower Body Resistance"], updated_params["Pulmonary Resistance"], 
                    updated_params["Heart Rate"], updated_params["Compliance at Dia"], updated_params["Compliance at Sys"], 
                    updated_params["Compliance of Sys Artery Over Vol"], updated_params["Compliance of Plm Vein Over Vol"], updated_params["Compliance of Plm Artery Over Vol"], 
                    z0_flows, updated_params["Systemic Arterial Oxygen Saturation"], updated_params["Oxygen Consumption of Upper Body"], updated_params["Oxygen Consumption of Lower Body"], updated_params["Hemoglobin Concentration"], z0_sat
                )
                P_pv = results.get("P_pv", float('nan'))
                PPV_outputs.append(P_pv)
            except ValueError:
                # If the solver fails, append NaN
                PPV_outputs.append(float('nan'))
        
        PPVs[param_name] = PPV_outputs  # Store results in the dictionary
    return PPVs

def plotPPA(UVR=45, LVR=35, PVR=10, HR=100, C_d=C_d, C_s=C_s, C_sa=C_sa, C_pv=C_pv, C_pa=C_pa, z0_flows=(3.1, 1.5, 1.5, 3.2, 75, 26, 2.5), S_sa=0.99, CVO2u=70, CVO2l=50, Hb=15, z0_sat=(0.55, 0.99, 0.55, 0.55)):
    # Parameters to vary
    parameters = {
        "Upper Body Resistance": UVR,
        "Lower Body Resistance": LVR,
        "Pulmonary Resistance": PVR,
        "Heart Rate": HR,
        "Compliance at Dia": C_d,
        "Compliance at Sys": C_s,
        "Compliance of Sys Artery Over Vol": C_sa,
        "Compliance of Plm Vein Over Vol": C_pv,
        "Compliance of Plm Artery Over Vol": C_pa,
        "Oxygen Consumption of Upper Body": CVO2u,
        "Oxygen Consumption of Lower Body": CVO2l,
        "Systemic Arterial Oxygen Saturation": S_sa,  # ✅ Added S_sa
        "Hemoglobin Concentration": Hb  # ✅ Added Hb
    }
    
    PPAs = {param: [] for param in parameters.keys()}  # Initialize a dictionary to store results

    # Normalized range for the x-axis (0.5 to 1.5)
    normalized_range = np.linspace(0.5, 1.5, 50)

    # Iterate through each parameter
    for param_name, base_value in parameters.items():
        PPA_outputs = []  # To store cardiac outputs for this parameter
        
        for factor in normalized_range:
            # Scale the parameter value
            scaled_value = base_value * factor
            
            # Create updated parameter set
            updated_params = {**parameters, param_name: scaled_value}
            
            try:
                # Calculate cardiac output
                results = complete_results(
                    updated_params["Upper Body Resistance"], updated_params["Lower Body Resistance"], updated_params["Pulmonary Resistance"], 
                    updated_params["Heart Rate"], updated_params["Compliance at Dia"], updated_params["Compliance at Sys"], 
                    updated_params["Compliance of Sys Artery Over Vol"], updated_params["Compliance of Plm Vein Over Vol"], updated_params["Compliance of Plm Artery Over Vol"], 
                    z0_flows, updated_params["Systemic Arterial Oxygen Saturation"], updated_params["Oxygen Consumption of Upper Body"], updated_params["Oxygen Consumption of Lower Body"], updated_params["Hemoglobin Concentration"], z0_sat
                )
                P_pa = results.get("P_pa", float('nan'))
                PPA_outputs.append(P_pa)
            except ValueError:
                # If the solver fails, append NaN
                PPA_outputs.append(float('nan'))
        
        PPAs[param_name] = PPA_outputs  # Store results in the dictionary
    return PPAs

def plotSPA(UVR=45, LVR=35, PVR=10, HR=100, C_d=C_d, C_s=C_s, C_sa=C_sa, C_pv=C_pv, C_pa=C_pa, z0_flows=(3.1, 1.5, 1.5, 3.2, 75, 26, 2.5), S_sa=0.99, CVO2u=70, CVO2l=50, Hb=15, z0_sat=(0.55, 0.99, 0.55, 0.55)):
    # Parameters to vary
    parameters = {
        "Upper Body Resistance": UVR,
        "Lower Body Resistance": LVR,
        "Pulmonary Resistance": PVR,
        "Heart Rate": HR,
        "Compliance at Dia": C_d,
        "Compliance at Sys": C_s,
        "Compliance of Sys Artery Over Vol": C_sa,
        "Compliance of Plm Vein Over Vol": C_pv,
        "Compliance of Plm Artery Over Vol": C_pa,
        "Oxygen Consumption of Upper Body": CVO2u,
        "Oxygen Consumption of Lower Body": CVO2l,
        "Systemic Arterial Oxygen Saturation": S_sa,  # ✅ Added S_sa
        "Hemoglobin Concentration": Hb  # ✅ Added Hb
    }
    
    SPAs = {param: [] for param in parameters.keys()}  # Initialize a dictionary to store results

    # Normalized range for the x-axis (0.5 to 1.5)
    normalized_range = np.linspace(0.5, 1.5, 50)

    # Iterate through each parameter
    for param_name, base_value in parameters.items():
        SPA_outputs = []  # To store cardiac outputs for this parameter
        
        for factor in normalized_range:
            # Scale the parameter value
            scaled_value = base_value * factor
            
            # Create updated parameter set
            updated_params = {**parameters, param_name: scaled_value}
            
            try:
                # Calculate cardiac output
                results = complete_results(
                    updated_params["Upper Body Resistance"], updated_params["Lower Body Resistance"], updated_params["Pulmonary Resistance"], 
                    updated_params["Heart Rate"], updated_params["Compliance at Dia"], updated_params["Compliance at Sys"], 
                    updated_params["Compliance of Sys Artery Over Vol"], updated_params["Compliance of Plm Vein Over Vol"], updated_params["Compliance of Plm Artery Over Vol"], 
                    z0_flows, updated_params["Systemic Arterial Oxygen Saturation"], updated_params["Oxygen Consumption of Upper Body"], updated_params["Oxygen Consumption of Lower Body"], updated_params["Hemoglobin Concentration"], z0_sat
                )
                S_pa = results.get("S_pa", float('nan'))
                SPA_outputs.append(S_pa)
            except ValueError:
                # If the solver fails, append NaN
                SPA_outputs.append(float('nan'))
        
        SPAs[param_name] = SPA_outputs  # Store results in the dictionary
    return SPAs


def plotSSVU(UVR=45, LVR=35, PVR=10, HR=100, C_d=C_d, C_s=C_s, C_sa=C_sa, C_pv=C_pv, C_pa=C_pa, z0_flows=(3.1, 1.5, 1.5, 3.2, 75, 26, 2.5), S_sa=0.99, CVO2u=70, CVO2l=50, Hb=15, z0_sat=(0.55, 0.99, 0.55, 0.55)):
    # Parameters to vary
    parameters = {
        "Upper Body Resistance": UVR,
        "Lower Body Resistance": LVR,
        "Pulmonary Resistance": PVR,
        "Heart Rate": HR,
        "Compliance at Dia": C_d,
        "Compliance at Sys": C_s,
        "Compliance of Sys Artery Over Vol": C_sa,
        "Compliance of Plm Vein Over Vol": C_pv,
        "Compliance of Plm Artery Over Vol": C_pa,
        "Oxygen Consumption of Upper Body": CVO2u,
        "Oxygen Consumption of Lower Body": CVO2l,
        "Systemic Arterial Oxygen Saturation": S_sa,  # ✅ Added S_sa
        "Hemoglobin Concentration": Hb  # ✅ Added Hb
    }
    
    SSVUs = {param: [] for param in parameters.keys()}  # Initialize a dictionary to store results

    # Normalized range for the x-axis (0.5 to 1.5)
    normalized_range = np.linspace(0.5, 1.5, 50)

    # Iterate through each parameter
    for param_name, base_value in parameters.items():
        SSVU_outputs = []  # To store cardiac outputs for this parameter
        
        for factor in normalized_range:
            # Scale the parameter value
            scaled_value = base_value * factor
            
            # Create updated parameter set
            updated_params = {**parameters, param_name: scaled_value}
            
            try:
                # Calculate cardiac output
                results = complete_results(
                    updated_params["Upper Body Resistance"], updated_params["Lower Body Resistance"], updated_params["Pulmonary Resistance"], 
                    updated_params["Heart Rate"], updated_params["Compliance at Dia"], updated_params["Compliance at Sys"], 
                    updated_params["Compliance of Sys Artery Over Vol"], updated_params["Compliance of Plm Vein Over Vol"], updated_params["Compliance of Plm Artery Over Vol"], 
                    z0_flows, updated_params["Systemic Arterial Oxygen Saturation"], updated_params["Oxygen Consumption of Upper Body"], updated_params["Oxygen Consumption of Lower Body"], updated_params["Hemoglobin Concentration"], z0_sat
                )
                S_svu = results.get("S_svu", float('nan'))
                SSVU_outputs.append(S_svu)
            except ValueError:
                # If the solver fails, append NaN
                SSVU_outputs.append(float('nan'))
        
        SSVUs[param_name] = SSVU_outputs  # Store results in the dictionary
    return SSVUs

def plotSSVL(UVR=45, LVR=35, PVR=10, HR=100, C_d=C_d, C_s=C_s, C_sa=C_sa, C_pv=C_pv, C_pa=C_pa, z0_flows=(3.1, 1.5, 1.5, 3.2, 75, 26, 2.5), S_sa=0.99, CVO2u=70, CVO2l=50, Hb=15, z0_sat=(0.55, 0.99, 0.55, 0.55)):
    # Parameters to vary
    parameters = {
        "Upper Body Resistance": UVR,
        "Lower Body Resistance": LVR,
        "Pulmonary Resistance": PVR,
        "Heart Rate": HR,
        "Compliance at Dia": C_d,
        "Compliance at Sys": C_s,
        "Compliance of Sys Artery Over Vol": C_sa,
        "Compliance of Plm Vein Over Vol": C_pv,
        "Compliance of Plm Artery Over Vol": C_pa,
        "Oxygen Consumption of Upper Body": CVO2u,
        "Oxygen Consumption of Lower Body": CVO2l,
        "Systemic Arterial Oxygen Saturation": S_sa,  # ✅ Added S_sa
        "Hemoglobin Concentration": Hb  # ✅ Added Hb
    }
    
    SSVLs = {param: [] for param in parameters.keys()}  # Initialize a dictionary to store results

    # Normalized range for the x-axis (0.5 to 1.5)
    normalized_range = np.linspace(0.5, 1.5, 50)

    # Iterate through each parameter
    for param_name, base_value in parameters.items():
        SSVL_outputs = []  # To store cardiac outputs for this parameter
        
        for factor in normalized_range:
            # Scale the parameter value
            scaled_value = base_value * factor
            
            # Create updated parameter set
            updated_params = {**parameters, param_name: scaled_value}
            
            try:
                # Calculate cardiac output
                results = complete_results(
                    updated_params["Upper Body Resistance"], updated_params["Lower Body Resistance"], updated_params["Pulmonary Resistance"], 
                    updated_params["Heart Rate"], updated_params["Compliance at Dia"], updated_params["Compliance at Sys"], 
                    updated_params["Compliance of Sys Artery Over Vol"], updated_params["Compliance of Plm Vein Over Vol"], updated_params["Compliance of Plm Artery Over Vol"], 
                    z0_flows, updated_params["Systemic Arterial Oxygen Saturation"], updated_params["Oxygen Consumption of Upper Body"], updated_params["Oxygen Consumption of Lower Body"], updated_params["Hemoglobin Concentration"], z0_sat
                )
                S_svl = results.get("S_svl", float('nan'))
                SSVL_outputs.append(S_svl)
            except ValueError:
                # If the solver fails, append NaN
                SSVL_outputs.append(float('nan'))
        
        SSVLs[param_name] = SSVL_outputs  # Store results in the dictionary
    return SSVLs


def plotSPV(UVR=45, LVR=35, PVR=10, HR=100, C_d=C_d, C_s=C_s, C_sa=C_sa, C_pv=C_pv, C_pa=C_pa, z0_flows=(3.1, 1.5, 1.5, 3.2, 75, 26, 2.5), S_sa=0.99, CVO2u=70, CVO2l=50, Hb=15, z0_sat=(0.55, 0.99, 0.55, 0.55)):
    # Parameters to vary
    parameters = {
        "Upper Body Resistance": UVR,
        "Lower Body Resistance": LVR,
        "Pulmonary Resistance": PVR,
        "Heart Rate": HR,
        "Compliance at Dia": C_d,
        "Compliance at Sys": C_s,
        "Compliance of Sys Artery Over Vol": C_sa,
        "Compliance of Plm Vein Over Vol": C_pv,
        "Compliance of Plm Artery Over Vol": C_pa,
        "Oxygen Consumption of Upper Body": CVO2u,
        "Oxygen Consumption of Lower Body": CVO2l,
        "Systemic Arterial Oxygen Saturation": S_sa,  # ✅ Added S_sa
        "Hemoglobin Concentration": Hb  # ✅ Added Hb
    }
    
    SPVs = {param: [] for param in parameters.keys()}  # Initialize a dictionary to store results

    # Normalized range for the x-axis (0.5 to 1.5)
    normalized_range = np.linspace(0.5, 1.5, 50)

    # Iterate through each parameter
    for param_name, base_value in parameters.items():
        SPV_outputs = []  # To store cardiac outputs for this parameter
        
        for factor in normalized_range:
            # Scale the parameter value
            scaled_value = base_value * factor
            
            # Create updated parameter set
            updated_params = {**parameters, param_name: scaled_value}
            
            try:
                # Calculate cardiac output
                results = complete_results(
                    updated_params["Upper Body Resistance"], updated_params["Lower Body Resistance"], updated_params["Pulmonary Resistance"], 
                    updated_params["Heart Rate"], updated_params["Compliance at Dia"], updated_params["Compliance at Sys"], 
                    updated_params["Compliance of Sys Artery Over Vol"], updated_params["Compliance of Plm Vein Over Vol"], updated_params["Compliance of Plm Artery Over Vol"], 
                    z0_flows, updated_params["Systemic Arterial Oxygen Saturation"], updated_params["Oxygen Consumption of Upper Body"], updated_params["Oxygen Consumption of Lower Body"], updated_params["Hemoglobin Concentration"], z0_sat
                )
                S_pv = results.get("S_pv", float('nan'))
                SPV_outputs.append(S_pv)
            except ValueError:
                # If the solver fails, append NaN
                SPV_outputs.append(float('nan'))
        
        SPVs[param_name] = SPV_outputs  # Store results in the dictionary
    return SPVs

    
def plotOER(UVR=45, LVR=35, PVR=10, HR=100, C_d=C_d, C_s=C_s, C_sa=C_sa, C_pv=C_pv, C_pa=C_pa, z0_flows=(3.1, 1.5, 1.5, 3.2, 75, 26, 2.5), S_sa=0.99, CVO2u=70, CVO2l=50, Hb=15, z0_sat=(0.55, 0.99, 0.55, 0.55)):
    # Parameters to vary
    parameters = {
        "Upper Body Resistance": UVR,
        "Lower Body Resistance": LVR,
        "Pulmonary Resistance": PVR,
        "Heart Rate": HR,
        "Compliance at Dia": C_d,
        "Compliance at Sys": C_s,
        "Compliance of Sys Artery Over Vol": C_sa,
        "Compliance of Plm Vein Over Vol": C_pv,
        "Compliance of Plm Artery Over Vol": C_pa,
        "Oxygen Consumption of Upper Body": CVO2u,
        "Oxygen Consumption of Lower Body": CVO2l,
        "Systemic Arterial Oxygen Saturation": S_sa,  # ✅ Added S_sa
        "Hemoglobin Concentration": Hb  # ✅ Added Hb
    }
    
    OERs = {param: [] for param in parameters.keys()}  # Initialize a dictionary to store results

    # Normalized range for the x-axis (0.5 to 1.5)
    normalized_range = np.linspace(0.5, 1.5, 50)

    # Iterate through each parameter
    for param_name, base_value in parameters.items():
        OER_outputs = []  # To store cardiac outputs for this parameter
        
        for factor in normalized_range:
            # Scale the parameter value
            scaled_value = base_value * factor
            
            # Create updated parameter set
            updated_params = {**parameters, param_name: scaled_value}
            
            try:
                # Calculate cardiac output
                results = complete_results(
                    updated_params["Upper Body Resistance"], updated_params["Lower Body Resistance"], updated_params["Pulmonary Resistance"], 
                    updated_params["Heart Rate"], updated_params["Compliance at Dia"], updated_params["Compliance at Sys"], 
                    updated_params["Compliance of Sys Artery Over Vol"], updated_params["Compliance of Plm Vein Over Vol"], updated_params["Compliance of Plm Artery Over Vol"], 
                    z0_flows, updated_params["Systemic Arterial Oxygen Saturation"], updated_params["Oxygen Consumption of Upper Body"], updated_params["Oxygen Consumption of Lower Body"], updated_params["Hemoglobin Concentration"], z0_sat
                )
                OER = results.get("OER", float('nan'))
                OER_outputs.append(OER)
            except ValueError:
                # If the solver fails, append NaN
                OER_outputs.append(float('nan'))
        
        OERs[param_name] = OER_outputs  # Store results in the dictionary
    return OERs
