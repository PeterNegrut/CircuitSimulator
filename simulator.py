import numpy as np

def one_node_sim(resistance_ohms, current_amps):
    conductance = 1/resistance_ohms
    A = np.array([[conductance]])
    b = np.array([current_amps])
    x = np.linalg.solve(A, b)
    return float(x[0])

def voltage_divider(resistance_ohms, voltagesource_volts):
    conductance = 1/resistance_ohms
      
 
if __name__ == "__main__":
    voltage = one_node_sim(1000, 0.001)
    print(f"Node voltage is: {voltage} V")
