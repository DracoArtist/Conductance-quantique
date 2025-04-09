import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from MathCore import compute_conductance_order, compute_conductance
import csv

"""
Matplotlib math latex update
"""
params = {'mathtext.default': 'regular' }          
plt.rcParams.update(params)

path_to = r"P_superpose_plateau.csv"
data_OG = pd.read_csv(r"acquisition_data_1.csv")
Vwire = data_OG["Voltage_wire"]

filtered = []
for v in Vwire:
    if -2.35 < v < -0.15:
        filtered.append(v)

with open(path_to, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Voltage_wire"])
    for V in filtered:
        writer.writerow([V])

"""
This file will search trough the filtered data in P_filtered_data.csv and search for a series of point 
(V_{i}, V_{i+1},...,V_{i+n}) that satisfies the following condition:
The difference |V_{m+1} - V_{m}| between any two points in the series is smaller than a certain threshold.
It then plot the plateaus found, as well as multiple other variants (conductance, averages, etc.)
"""

"""
Define the data to search in
"""

data_file = pd.read_csv(path_to)
Vwire = data_file["Voltage_wire"]

"""
Define plateau caracteristics
"""

points_per_plateau = 5

diff = np.diff(Vwire)
max_diff = 1*10**(-2)  # The maximum difference between to points before we consider they are not on the same plateau

"""
Search on plateau and add the points on the plateau to a dictionnary. The key in the dicionnary is the index of the first point
on the plateau
"""

plateaus = {}

on_plateau = False
index = 0

for i in range(len(diff)):
    if abs(diff[i]) <= max_diff and not on_plateau:
        on_plateau = True
        index=i
    if abs(diff[i]) > max_diff and on_plateau:
        on_plateau = False
        if i-index < 5:
            continue
        plateaus[index] = Vwire[index:i]

"""
Print out all the plateaus so that we can can search for it manually trought the data
"""
# for index in plateaus.keys():
#     print(f"plateaus starts at {index}: \n {plateaus[index]}")

"""
Plot the plateaus
"""

# If we want to overlap the plateaus to the data
plt.plot(
    Vwire.index.to_list(),
    Vwire,
    'o',
    markersize=2.5,
    color='black')

for index in plateaus.keys():
    indexes = plateaus[index].index.tolist()
    plt.plot(indexes, [Vwire[index] for index in indexes], 'o', markersize=3.5),


plt.title("Les différents plateaux identifiés")
plt.ylabel("Tension (V)")
plt.xlabel("Temps (10 $\mu$s)")
plt.grid(which='both')
plt.show()

"""
Plots the average voltage found for each plateau
"""

plateau_values = [np.mean(plateaus[key]) for key in plateaus.keys()]
plt.plot(
    plateaus.keys(),
    plateau_values,
    'o',
    markersize=2
)
plt.title("Les valeurs moyennes des divers plateaus identifiés")
plt.ylabel("Tension (V)")
plt.xlabel("Temps auquel le premier point sur le plateau a été identifié (10 microsecondes)")
plt.grid(which='both')
plt.show()

"""
Plot the plateaus as conductance
"""

conductance_plateaus = {}

for index in plateaus.keys():
    conductance_plateaus[index] = compute_conductance(
        voltage=plateaus[index],
        source_voltage=2.5,
        resistance=20000
    )


for index in conductance_plateaus.keys():
    indexes = conductance_plateaus[index].index.tolist()
    plt.plot(indexes, conductance_plateaus[index], 'o', markersize=2)

plt.title("Les différents plateaux identifiés")
plt.ylabel("Conductance")
plt.xlabel("Temps (10 microsecondes)")
plt.grid(which='both')
plt.show()

n_plateaus = {}

for index in plateaus.keys():
    n_plateaus[index] = compute_conductance_order(
        voltage=plateaus[index],
        source_voltage=2.5,
        resistance=20000
    )

for index in n_plateaus.keys():
    indexes = n_plateaus[index].index.tolist()
    plt.plot(indexes, n_plateaus[index], 'o', markersize=2),


plt.title("Les différents plateaux identifiés et leur ordre correspondant")
plt.ylabel("Ordre n de la conductance")
plt.xlabel("Temps (10 microsecondes)")
plt.grid(which='both')
plt.show()

