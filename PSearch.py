import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Search:
    """
    Search is a class that goes trough data and searches plateaus. It has different methods of doing
    so, all of them return a dictionnary who's keys are the starting index of the plateaus and who's
    items are ndarrays containing the points of the plateau.

    Arguments:
        - data_to_search (numpy ndarray): the data to search trough. Must be an ndarray to avoid the possibility of bugs
    
    Methods:
    - find_plateaus_diff(self, max_diff, minimal_ratio_in=0.8, plateau_lenght = 5):
        This method will go trough the data and search for a series of point (V_{i}, V_{i+1},...,V_{i+n}) 
        that satisfies the following condition:
        - The difference |V_{m+1} - V_{m}| between any two points in the series is smaller than max_diff
        - The series of point is at least plateau_lenght long
    
    - find_plateaus_box(self, plateu_height, plateau_lenght = 5):
        This method takes the points i to i+plateau_lenght, and checks if there are enough points within a plateau_height
        voltage interval. If yes, he considers those points to be a plateau.
        This method returns a plateau if there are at least minimal_ratio_in * plateau_lenght points in the interval.
    
    """
    def __init__(self, data_to_search):
        assert data_to_search.__class__.__name__ == "ndarray", "Error: data to search trough is not a ndarray"
        self.data = data_to_search

    def find_plateaus_diff(self, max_diff, plateau_lenght = 5) -> dict:
        assert max_diff.__class__.__name__ == "float", f"Error: max_diff is {type(max_diff)} insdtead of float"
        assert plateau_lenght.__class__.__name__ == "int", f"Error: plateau_lenght is {type(plateau_lenght)} instead of int"
        

        plateaus = {}
        
        diff = np.diff(self.data)

        on_plateau = False
        index = 0

        for i in range(len(diff)):
            if abs(diff[i]) <= max_diff and not on_plateau:
                on_plateau = True
                index=i
            if abs(diff[i]) > max_diff and on_plateau:
                on_plateau = False
                if i-index < plateau_lenght:
                    continue
                plateaus[f"{index}"] = self.data[index:i]
            
        return plateaus
    
    def count_points_in_box(self, box_height, box_minimum, data):
        assert data.__class__.__name__ == "ndarray", "Error: data to search trough is not a ndarray"
        assert box_height.__class__.__name__ in ["float", "float64"], f"Error: box_height is not a float"
        assert box_minimum.__class__.__name__ in ["float", "float64"], f"Error: box_height is not a float"

        points_in_box = 0

        for residue in data - box_minimum:
            if abs(residue) > box_height:
                continue
            points_in_box += 1
        
        return points_in_box

    def find_plateaus_box(self, plateu_height, minimal_ratio_in=0.8, plateau_lenght = 5) -> dict:
        plateaus = {}
        skip_to_index = -1

        for index, _ in enumerate(self.data):
            if index < skip_to_index:
                continue
            data_to_check = self.data[index: index+plateau_lenght]
            plateau = False
            for point in data_to_check:
                points_in_box = self.count_points_in_box(
                    box_height=plateu_height,
                    box_minimum=point,
                    data=data_to_check
                )
                if points_in_box >= minimal_ratio_in*plateau_lenght:
                    plateau = True
                    skip_to_index = index + plateau_lenght + 1
            
            if plateau:
                plateaus[f"{index}"] = data_to_check

        return plateaus
    


# data_file = pd.read_csv(r"prise_mesure_lab\filor_vibration1.csv", usecols=[3,4], names=['colA', 'colB'])
# Vwire = np.array(data_file["colB"])
# s = Search(data_to_search=Vwire)
# # plateaus = s.find_plateaus_box(
# #     plateau_lenght=7,
# #     plateu_height=0.005
# # )
# plateaus = s.find_plateaus_diff(
#     plateau_lenght=5,
#     max_diff=0.01
# )
# print(plateaus)
# plt.plot(
#     [i for i, _ in enumerate(Vwire)],
#     Vwire,
#     'o',
#     markersize=2.5,
#     color='black')

# for index in plateaus.keys():
#     data = plateaus[index]
#     plt.plot([float(index) + i for i, _ in enumerate(data)], data, 'o', markersize=3.5),


# plt.title("Les différents plateaux identifiés")
# plt.ylabel("Tension (V)")
# plt.xlabel("Temps (10 $\mu$s)")
# plt.grid(which='both')
# plt.show()
