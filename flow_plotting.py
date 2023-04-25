# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 17:41:57 2023

@author: felipe
"""

import numpy as np
import numpy.random as rand
import matplotlib.pyplot as plt
import csv
import time

start = time.time()

max_speed = 5  # m s ^ -1
road_length = 2000  # metres / number of sites
prob_of_deceleration = 0.4
seconds = 15000  # seconds


def generating_simple_road(v_max, length, density):
    num_cars = int(np.floor(length * density))
    # generating road array
    road = np.zeros(length)
    # generating indices and speeds for cars
    road_indices = range(length)
    car_indices = []
    n = 0
    while n < num_cars:
        # generating random index for each car.
        car_index = rand.choice(road_indices)
        car_indices = np.append(car_indices, car_index)
        # deleting this index from the original list of indices so that 2 cars
        # aren't generated in the same place
        road_indices = np.delete(
            road_indices, np.where(car_index == road_indices)[0])
        # generating random speed
        car_speed = rand.randint(0, v_max+1)
        # placing car on road
        road[car_index] = car_speed
        n += 1
    # sorting array for car indices
    car_indices = np.sort(car_indices)
    return road, car_indices

def accel_decel(v_max, road, loc_cars):
    n = 0
    # loop for the cars which aren't at the end of the road
    while n < (len(loc_cars) - 1):
        location = int(loc_cars[n])
        speed = road[location]
        if speed < v_max and (speed + 1) < (loc_cars[n+1] - location):
            road[location] += 1
        if speed >= (loc_cars[n+1] - location):
            road[location] = loc_cars[n+1] - location - 1
        n += 1
    # case for the last car
    loc_last = int(loc_cars[-1])
    speed_last = road[loc_last]
    if speed_last < v_max and (speed_last + 1) < (loc_cars[0] - loc_last + len(road)):
        road[loc_last] += 1
    if speed_last >= (loc_cars[0] - loc_last + len(road)):
        road[loc_last] = (loc_cars[0] - loc_last + len(road)) - 1
    # generating random numbers for random deceleration
    n = 0
    sample = rand.uniform(0, 1, size=100)
    while n < len(loc_cars):
        location = int(loc_cars[n])
        if road[location] != 0:
            rand_num = rand.choice(sample)
            if rand_num < prob_of_deceleration:
                road[location] = road[location] - 1
        n += 1
    return road, loc_cars

def moving_cars(road, loc_cars):
    n = 0
    new_locs = []
    # moving cars which aren't at the end of the road
    while n < len(loc_cars):
        try:
            location = int(loc_cars[n])
            new_location = int(location + road[location])
            new_locs = np.append(new_locs, new_location)
            road[new_location] = road[location]
            road[location] = 0
            n += 1
        except IndexError:
            new_locs = np.delete(new_locs, np.where(
                new_location == new_locs)[0])
            # case for last car
            loc_last = int(loc_cars[-1])
            speed_last = road[loc_last]
            new_loc = int(loc_last + speed_last - len(road))
            new_locs = np.append(new_locs, new_loc)
            road[new_loc] = speed_last
            road[loc_last] = 0
            n += 1
    new_locs = np.sort(new_locs)
    return road, new_locs

def car_flow(road, car_locs, density):
    n_cars = len(car_locs)
    v_avg = np.sum(road)/n_cars
    return density*v_avg

def iterate_road_flows(tot_time, density):
    time = 1
    road, car_indices = generating_simple_road(
        max_speed, road_length, density)
    flow = 0
    # repeating whole process for certain amount of iterations
    while time < tot_time:
        road, car_indices = accel_decel(
            max_speed, road, car_indices)
        road, car_indices = moving_cars(road, car_indices)
        if time > len(road):
            flow += car_flow(road, car_indices, density)
        time += 1
    flow_rate = flow / time
    return flow_rate

def write_flows(time):
    densities = rand.uniform(low=0.01, high=1, size=10)
    flow_rates = []
    for rho in densities:
        flow_rate = iterate_road_flows(time, rho)
        flow_rates.append(flow_rate)
    with open("flow_rate_data_2.csv", 'a', encoding='utf-8') as data:
        writer = csv.writer(data)
        for index in enumerate(densities):
            writer.writerow([densities[index[0]], flow_rates[index[0]]])

def plot_flows():
    data = np.genfromtxt("flow_rate_data_2.csv", dtype='float',
                         delimiter=',', skip_header=1)
    densities = data[:, 0]
    flow_rates = data[:, 1]
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    ax.set_title('Traffic Flow for 1 lane', fontsize=22)
    ax.set_xlabel('Density (cars per site)', fontsize=18)
    ax.set_ylabel('Average Flow (cars per time step)', fontsize=18)
    plt.xticks(np.arange(0, 1.1, step=0.1), fontsize=14)
    plt.yticks(fontsize=14)
    plt.scatter(densities, flow_rates, color='black', s=1)

    plt.grid()
    plt.show()
    plt.savefig("Flow_graph_single_lane_final.pdf", dpi=400)

#write_flows(seconds)
plot_flows()

end = time.time()

print((end - start)/60)