"""Originally done for COMP6730

Coauthors: Atif Farooq, Rajkamal Dhull
Date: 15/10/2018
"""

from visualise import show_vegetation_type
from visualise import show_vegetation_density
from visualise import show_wind_speed
from visualise import show_bushfire
from visualise import show_fire_risk


import os
import math
import random

def load_dataset(filename):
    '''
        A generic function for loading datasets that are in .csv format.
        arguments:
                - filename: the filepath to the csv dataset (str)
        return value: list of lists (list)
    '''
    
    if os.path.exists(filename):
        dataset = []        
        file_object = open(filename, 'r')
        for line in file_object:
            line = line[:-1]
            sub_list = line.split(",")
            dataset.append(sub_list)
        file_object.close()
        return dataset
    else:
        raise FileNotFoundError("The specified file could not be found")

def load_vegetation_type(filename):
    '''
        Loads the 'vegetation type' map
        arguments:
                - filename: the filepath to vegetation_type.csv (str)
        return value: list of lists (list)
    '''
    dataset = load_dataset(filename)
    return dataset

def load_vegetation_density(filename):
    '''
        Loads the 'vegetation density' map
        arguments:
                - filename: the filepath to vegetation_density.csv
        return value: list of lists (list)
    '''
    dataset = load_dataset(filename)
    return dataset

def load_wind_speed(filename):
    '''
        Loads the 'wind speed' map
        arguments:
                - filename: the filepath to wind.csv (str)
        return value: list of lists (list)
    '''
    dataset = load_dataset(filename)
    return dataset

def load_bushfire(filename):
    '''
        Loads the 'bushfire' map

    '''
    dataset = load_dataset(filename)
    return dataset


def highest_wind_speed(wind_speed):
    ''' returns the highest wind speed value in the given wind speed map 
        arguments: 
                - wind_speed: the wind speed map in the form of a list of lists (list)
        return value: 
                - highest_speed: (float)
    '''
    highest_speed = max([max(sub_list) for sub_list in wind_speed])
    return highest_speed
    

def get_vegetation_type_dict(vegetation_type):
    '''
        Takes in a vegetation type map as an argument, reads it, 
        populates a vegetation type to frequency dictionary and
        returns that dictionary
        arguments:
                - vegetation_type: map (list)
        return value: 
                - veg_type_freq: a dictionary (dict)
    '''
    veg_type_freq = dict()
    for row in vegetation_type:
        for entry in row:
            if entry != "":
                if entry not in veg_type_freq:
                    veg_type_freq[entry] = 0    
                veg_type_freq[entry] += 1
    return veg_type_freq


def count_cells(vegetation_type):
    '''
       Counts the number of cells filled by each type of vegetation in the 
       given map. Assumption: This function will not print any types of 
       vegetation that are not present in the given map
       Arguments: 
               - vegetation_type: a map (list)
       return value: void
    '''
    veg_type_freq = get_vegetation_type_dict(vegetation_type)
    for key, value in veg_type_freq.items():
        print(key, ":", value)


def count_area(vegetation_type, vegetation_density):
    '''
        counts the area covered by each type of vegetation in the map based on its density
        Arguments: 
                - vegetation_type, vegetation_density: maps (list)
        return value: void
    '''
    veg_type_freq = get_vegetation_type_dict(vegetation_type)
    veg_type_list = list(veg_type_freq.keys())
    veg_type_area = dict()
    
    # while loop ensures that we don't iterate over vegetation_types
    # whose correspoding area entry we have already calculated
    while len(veg_type_list) != 0:
        for i in range(len(vegetation_type)):
            for j in range(len(vegetation_type[0])):
                entry = vegetation_type[i][j]
                if entry != "" and entry in veg_type_list:
                    if entry not in veg_type_area:
                        density = float(vegetation_density[i][j])
                        number_of_cells = float(veg_type_freq[entry])
                        area = density * 10000 * number_of_cells
                        veg_type_area[entry] = area
                        veg_type_list.remove(entry)
    
    for key, value in veg_type_area.items():
        print("{0}: {1:.2f} sq m".format(key, value))


def fire_risk_cell(vegetation_type_cell, vegetation_density_cell):
    ''' helper function that determines the type of the vegetation in a 
        given cell and assigns risk scores accordingly based in its density
    '''
    if (vegetation_type_cell == 'Shrubland' or vegetation_type_cell =='Pine Forest'):
        risk = math.sqrt(0.2 + vegetation_density_cell)
    elif (vegetation_type_cell == 'Arboretum'):
        risk = math.sqrt(0.1 + vegetation_density_cell)
    elif (vegetation_type_cell == 'Urban Vegetation' or vegetation_type_cell == 'Golf Course'):
        risk = math.sqrt(0.05 + vegetation_density_cell)
    else:
        risk = math.sqrt(0 + vegetation_density_cell)
    return risk

def get_boundary_coordinates(padding_length, x, y, x_max_length, y_max_length):
    '''
        given a cell with coordinates (x,y) in a grid and a padding_length, determines the 
        indices of 'boundary' coordinates. These are used in downstream tasks (such as spreading
        of the fire and estimating fire risk). The boundary coordinates can be thought of 
        as a 'sliding window' around the cell.
    '''
    x_max = x + padding_length
    if x_max > x_max_length:
        x_max = x_max_length
    
    # boundary case    
    x_min = x - padding_length
    if x_min < 0:
        x_min = 0
    
    y_max = y + padding_length
    if y_max > y_max_length:
        y_max = y_max_length                
    
    # boundary case
    y_min = y - padding_length
    if y_min < 0:
        y_min = 0
        
    return (x_max, x_min, y_max, y_min)

def fire_risk(x, y, vegetation_type, vegetation_density, wind_speed):
    '''
        returns a calculation of the 'fire risk' for each cell (x,y) based on the 
        'fire risk factors' of nearby cells
        Arguments:
            - x, y: coordinates of the cell. x=column and y=row (int)
            - vegetation_type, vegetation_density, wind_speed: maps (list)
        return value: total_risk: a number (float)
    '''
    y_max_length = len(wind_speed) - 1
    x_max_length = len(wind_speed[0]) - 1
    
    total_risk = 0
    if wind_speed[y][x] == "" or math.floor(float(wind_speed[y][x])) == 0:
        vegetation_type_cell = vegetation_type[y][x]
        if vegetation_type_cell != "":
            vegetation_density_cell = float(vegetation_density[y][x])
            risk_factor_cell = fire_risk_cell(vegetation_type_cell, vegetation_density_cell)
            total_risk = total_risk + risk_factor_cell
    else:
        wind_speed_cell = math.floor(float(wind_speed[y][x]))
        
        # get the critical 'boundary' coordinates for this cell (x,y)
        x_max, x_min, y_max, y_min = get_boundary_coordinates(wind_speed_cell, x, y, x_max_length, y_max_length)
        # we only want to consider the cells surrounding the current one
        for i in range(y_min, y_max+1):
            for j in range(x_min, x_max+1):
                if i == y and j == x:
                    risk_factor_cell = 0
                else:
                    vegetation_type_cell = vegetation_type[i][j]
                    if vegetation_type_cell != "":
                        vegetation_density_cell = float(vegetation_density[i][j])
                        risk_factor_cell = fire_risk_cell(vegetation_type_cell, vegetation_density_cell)
                        total_risk = total_risk + risk_factor_cell
    return total_risk
        

def simulate(initial_bushfire, vegetation_type, vegetation_density, steps, risk_factor_matrix, max_risk_factor, is_stochastic):
    '''
        Performs simulations of fire spreading across a map for a given number of timesteps
        
        Arguments:
                - initial_bushfire, vegetation_type, vegetation_density: maps (list)
                - steps: the number of timesteps that we want the simulation to run for (int)
                - risk_factor_matrix: list of lists populated with risk factor scores corresponding
                  to each cell (only needed for stochastic simulation) (list)
                - max_risk_factor: the max value in the risk_factor_matrix (only for stochastic simulation)(float)
                - is_stochastic: type of simulation (bool)
        return value: list of lists representing locations of map that are on fire with a '1' (list)
    '''
    # find the range of indices of the initial bushfire map
    x_max_length = len(initial_bushfire) - 1
    y_max_length = len(initial_bushfire[0]) - 1
    
    while steps > 0:
        
        cells_affected_by_fire = []
        
        for x in range(len(initial_bushfire)):
            for y in range(len(initial_bushfire[0])):
                # deterime which cell contains a '1', (or where there is a fire)
                if initial_bushfire[x][y] != "":
                    grid_boolean_value = bool(int(initial_bushfire[x][y]))
                    if grid_boolean_value:
                        # store these cell coordinates in a list
                        cells_affected_by_fire.append((x, y))
        
        # for each one of the affected cells in this timestep, 'spread' the fire around a padding
        # length of 1 (8 cells that surround it)
        for cell in cells_affected_by_fire:
            x = cell[0]
            y = cell[1]
            # get crital 'boundary' coordinates where the fire needs to spread
            x_max, x_min, y_max, y_min = get_boundary_coordinates(1, x, y, x_max_length, y_max_length)
            
            for i in range(x_min, x_max + 1):
                for j in range(y_min, y_max + 1): 
                    if is_stochastic:
                        # spread fire stochastically
                        threshold = random.uniform(0.1, 0.4)
                        risk_factor_stochastic = risk_factor_matrix[i][j]/ max_risk_factor
                        if x != i and y != j:
                            if initial_bushfire[i][j] != "" and initial_bushfire[i][j] != 1 and risk_factor_stochastic > threshold:
                                initial_bushfire[i][j] = 1
                    else:
                        # non stochastic simulation
                        if initial_bushfire[i][j] != "":    
                            initial_bushfire[i][j] = 1
        # clear the list and decrement timestep
        cells_affected_by_fire.clear()
        steps -= 1
    return initial_bushfire

def simulate_bushfire(initial_bushfire, vegetation_type, vegetation_density, steps):
    '''
       Given the initial_bushfire map, performs a 'simulation' of spreading the fire
       to a given number of integer steps, and returns the bushfire map at that timestep
       
       Arguments:
               - initial_bushfire, vegetation_type, vegetation_density: maps (list)
               - steps: the number of timesteps that we want the simulation to run for (int)
    '''

    return simulate(initial_bushfire, vegetation_type, vegetation_density, steps, risk_factor_matrix=None, max_risk_factor=None, is_stochastic=False)
                

def compare_bushfires(bushfire_a, bushfire_b):
    ''' returns the percentage of the cells that have the same float
        values in the two given maps, giving us a metric of 'overlap' 
        Arguments: 
            - bushfire_a, bushfire_b: two bushfire maps to be compared
              in the form of list of lists (list)
        return value: 
            - percentage_cell: percenage overlap (float)
    '''
    x_max = len(bushfire_b)
    y_max = len(bushfire_b[0])
    match_count_cell = 0
    total_count_cell = 0
    for i in range(0, x_max):
            for j in range(0, y_max):
                if bushfire_a[i][j] != "":
                    total_count_cell = total_count_cell + 1
                    if bushfire_a[i][j] == bushfire_b[i][j]:
                        match_count_cell = match_count_cell + 1
                
    percentage_cell = match_count_cell / total_count_cell
    return percentage_cell


def compute_risk_factor_matrix(m, n, vegetation_type, 
                               vegetation_density, wind_speed):
    '''
        Returns an m * n matrix populated with risk factor scores corresponding
        to each cell
    '''
    # initialize an m*n matrix with zeroes 
    risk_factor_matrix = [0] * m
    for i in range(m):
        risk_factor_matrix[i] = [0] * n
    
    # populate the matrix with corresponding risk factor scores
    for i in range(0, m):
            for j in range(0, n):
                risk_factor = fire_risk(j, i, vegetation_type, vegetation_density, wind_speed)
                risk_factor_matrix[i][j] = risk_factor
    max_risk_factor = max([max(sub_list) for sub_list in risk_factor_matrix])
    
    return (risk_factor_matrix, max_risk_factor)


def simulate_bushfire_stochastic(
        initial_bushfire, steps,
        vegetation_type, vegetation_density,
        wind_speed):
    '''
        Performs a 'stochastic' simulation of a bushfire where the fire spreads to nearby 
        cells based on their fire risk factor and randomness.
        Arguments: 
            - maps in the form of list of lists 
            - steps: the number of steps to which we want the simulation to run
        return value: a map of the result after the fire has been spread (list)
    '''
    
    m = len(initial_bushfire)
    n = len(initial_bushfire[0])
    risk_factor_matrix, max_risk_factor = compute_risk_factor_matrix(m, n, vegetation_type, 
                           vegetation_density, wind_speed)
    return simulate(initial_bushfire, vegetation_type, vegetation_density, steps, risk_factor_matrix, max_risk_factor, is_stochastic=True)


def count_blank_values(matrix):
    '''
        Helper function that counts the number of 'blank'
        entries in a given list of lists
        Arguments: 
                - matrix: a list of lists (list)
        return value: count (int)
    '''
    count = 0
    for row in matrix:
        for entry in row:
            if entry == "":
                count = count + 1
    return count
     

if __name__ == '__main__':
    # If you want something to happen when you run this file,
    # put the code in this `if` block.
    pass
