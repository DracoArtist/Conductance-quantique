import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from MathCore import G0

"""
General data acquisition data
"""

source_voltage = 2.5
resistance = 20000

data_file = pd.read_csv(r"acquisition_data_3.csv")
Vwire = -np.array(data_file["Voltage_wire"])

"""
Compute range in which plateaus are supposed to be
"""

def expected_plateau_voltage(n:int, Rres:float, V=source_voltage, R=resistance):
    """
    Uses Ohm's law to compute the theoritical voltage across the gold wires of the plateaus for a
    certain Rres residual resistance in the nanowires. This residual resistance is due to the
    disorder within the wire and is modeled as a resistance placed in series with a perfect
    nanowire.

    Arguments:
        - n: integer corresponding to the multiple of G0 the conductance is supposed to be
        - Rres: residual resistance
        - V: voltage of the source, considered to be perfectly stable
        - R: resistance placed in series with the gold wires
    """
    return V / (1 + R / (1/(n*G0) + Rres))

# list of values where the voltage is supposed to be
## the _min list considers Rres = 0
## the _max list considers Rres = 600
expected_plateau_voltages_min = np.array([expected_plateau_voltage(n=i+1, Rres=0) for i in range(5)])
expected_plateau_voltages_max = np.array([expected_plateau_voltage(n=i+1, Rres=600) for i in range(5)])

print(expected_plateau_voltages_min)
print(expected_plateau_voltages_max)

print("Update: expected plateaus computed")

"""
Filtering out every point that is not between the values of expected_plateau_voltages_min[i] and
expected_plateau_voltages_max[i] for some i
"""

# Initialise a list for all the points that fall into the criterias
filtered_data = []

# Check for each point in it is in between the min and max values of a plateau, as defined higher
out_of_range = True
for voltage in Vwire:
    for i in range(len(expected_plateau_voltages_max)):
        if voltage <= expected_plateau_voltages_max[i] and voltage >= expected_plateau_voltages_min[i]:
            out_of_range = False
    
    if not out_of_range:
        filtered_data.append(voltage)
    out_of_range=True

# Export the filtered data into a csv
df = pd.DataFrame(
    data=filtered_data
)
print("Update: data filtered")

df.to_csv(r"P_filtered_data_3.csv", index=False, header=["Voltage_wire"])
print("Update: filtered data exported")

"""
Graph filtered data, as well as cutoff values.
The golden lines on the graph are the minimum voltage at which we could expect a plateau
The red lines are the maximum voltage at which we could expect a plateau
"""

index_range = [i for i in range(len(filtered_data))]  # indexes to plot the filtered data
x_range = np.linspace(0,max(index_range),10)  # a range to be able to plot the cutoff values

plt.plot(index_range, filtered_data, 'o', markersize=1)
for i in range(len(expected_plateau_voltages_max)):
    plt.plot(
        x_range,
        [expected_plateau_voltages_min[i] for j in x_range],
        color=(255/255, (189 - i*85/5)/255, (136 - i*136/5)/255),  # Changing color tone so we can have a usefull legend
        label=f"Minimum voltage for n={i+1}"
    )  # plotting a line for expected_plateau_voltages_min[i]
    plt.plot(
        x_range,
        [expected_plateau_voltages_max[i] for j in x_range],
        color=((255 - 150*i/5)/255, 0, 0), # Changing color tone so we can have a usefull legend
        label=f"Maximum voltage for n={i+1}"
    )  # plotting a line for expected_plateau_voltages_max[i]`

plt.title("Filtered voltage measures, as well as cutoff values for the different plateaus")
plt.xlabel("Index")
plt.ylabel("Voltage (V)")
plt.legend(loc='best')
plt.show()