# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 17:28:46 2023

This code is just to practice switching before putting it in the main code

@author: felipe
"""
import numpy as np
import numpy.random as rand
import csv
import matplotlib.pyplot as plt
import time

start = time.time()

max_speed = 5  # m s ^ -1
road_length = 500  # metres / number of sites
prob_of_deceleration = 0.4
seconds = 1200  # seconds


def translate_road(road, loc_cars):
    final_road = ['.' for i in range(len(road))]
    locs = list(map(int, loc_cars))
    for index in locs:
        final_road[index] = int(road[index])
    print(*final_road, sep='  ')


def generating_simple_road(density):
    num_cars = int(np.floor(road_length * density))
    road = np.zeros(road_length)
    road_indices = []
    for i in range(road_length):
        road_indices.append(i)
    car_indices = []
    n = 0
    while n < num_cars:
        car_index = rand.choice(road_indices)
        car_indices.append(car_index)
        road_indices.remove(car_index)
        car_speed = rand.randint(0, max_speed+1)
        road[car_index] = car_speed
        n += 1
    car_indices.sort()
    return road, car_indices


def accel_decel(road, loc_cars):
    sample = rand.uniform(0, 1, size=100)
    n = 0
    while n < len(loc_cars):
        location = int(loc_cars[n])
        speed = road[location]
        if location == loc_cars[-1]:
            if speed < max_speed and (speed + 1) < (loc_cars[0] - location + len(road)):
                road[location] += 1
            if speed >= (loc_cars[0] - location + len(road)):
                road[location] = (loc_cars[0] - location + len(road)) - 1
        else:
            next_veh = int(loc_cars[n + 1])
            if speed < max_speed and (speed + 1 < next_veh - location):
                road[location] += 1
            if speed >= next_veh - location:
                road[location] = next_veh - location - 1
        if road[location] != 0:
            rand_num = rand.choice(sample)
            if rand_num < prob_of_deceleration:
                road[location] -= 1
        n += 1
    return road, loc_cars


def moving_cars(road, loc_cars):
    n = 0
    new_locs = []
    # moving cars
    while n < len(loc_cars):
        location = int(loc_cars[n])
        speed = road[location]
        if (speed >= len(road) - location):
            new_location = int(location + speed - len(road))
        else:
            new_location = int(location + speed)
        new_locs.append(new_location)
        road[new_location] = speed
        road[location] = 0
        n += 1
    new_locs.sort()
    return road, new_locs


def neighbour_finder(locs1, locs2):
    neighbours = []
    for i in locs1:
        if i in locs2:
            neighbours.append(i)
    return neighbours


def compare_2_lanes(locs1, locs2):
    neighbours = neighbour_finder(locs1, locs2)
    distances = []
    index = 0
    while index < len(locs1):
        car_loc = locs1[index]
        # return 0s if car has a neighbour
        if car_loc in neighbours:
            distances.append((0, 0))
        else:
            locs2.append(car_loc)
            locs2.sort()
            test_car_index = int(np.where(car_loc == np.array(locs2))[0])
            if locs1[index] == locs1[-1]:
                next_car_d_1 = locs1[0] + road_length - car_loc
                if locs2[test_car_index] == locs2[-1]:
                    next_car_d_2 = locs2[0] + road_length - car_loc
                else:
                    next_car_d_2 = locs2[test_car_index + 1] - car_loc
            else:
                next_car_d_1 = locs1[index + 1] - car_loc
                if locs2[test_car_index] == locs2[-1]:
                    next_car_d_2 = locs2[0] + road_length - car_loc
                else:
                    next_car_d_2 = locs2[test_car_index + 1] - car_loc
            distances.append((next_car_d_1, next_car_d_2))
            locs2.remove(car_loc)
        index += 1
    return distances


def switch(lane1, lane2, locs1, locs2, distances):
    """
    This just swiches the cars from lane1 to lane2 using the distances list of tuples
    """
    index = 0
    while index < len(locs1):
        tup = distances[index]
        car_loc = int(locs1[index])
        if tup[0] != 0:
            if tup[1] > tup[0]:
                lane2[car_loc] = lane1[car_loc]
                lane1[car_loc] = 0
                locs2.append(car_loc)
                locs2.sort()
                locs1.remove(car_loc)
                distances = compare_2_lanes(locs1, locs2)
        index += 1
    return lane1, lane2, locs1, locs2


def switch_process(road1, road2, locs1, locs2):
    distances_12 = compare_2_lanes(locs1, locs2)
    road1, road2, locs1, locs2 = switch(
        road1, road2, locs1, locs2, distances_12)
    distances_21 = compare_2_lanes(locs2, locs1)
    road2, road1, locs2, locs1 = switch(
        road2, road1, locs2, locs1, distances_21)
    return road1, road2, locs1, locs2


def car_flow(road, car_locs):
    n_cars = len(car_locs)
    density = n_cars/road_length
    v_avg = np.sum(road)/n_cars
    return density*v_avg


def iterating_switching(tot_time, density):
    time = 0
    road1, locs1 = generating_simple_road(density)
    road2, locs2 = generating_simple_road(density)
    flow_avg = 0
    while time < tot_time:
        road1, road2, locs1, locs2 = switch_process(road1, road2, locs1, locs2)
        road1, locs1 = accel_decel(road1, locs1)
        road2, locs2 = accel_decel(road2, locs2)
        road1, locs1 = moving_cars(road1, locs1)
        road2, locs2 = moving_cars(road2, locs2)
        flow_avg += (car_flow(road1, locs1) + car_flow(road2, locs2))/2
        time += 1
    return flow_avg / time


def write_flows(time):
    densities = rand.uniform(low=0.01, high=0.1, size=5)
    flow_rates = []
    for rho in densities:
        flow_rate = iterating_switching(time, rho)
        flow_rates.append(flow_rate)
    with open("flow_rate_data_2_lanes3.csv", 'a', encoding='utf-8') as data:
        writer = csv.writer(data)
        for index in enumerate(densities):
            writer.writerow([densities[index[0]], flow_rates[index[0]]])


def plot_flows():
    data = np.genfromtxt("flow_rate_data_2_lanes3AAA.csv", dtype='float',
                         delimiter=',', skip_header=1)
    densities = data[:, 0]
    flow_rates = data[:, 1]
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    ax.set_title('Traffic Flow for 2 lanes', fontsize=22)
    ax.set_xlabel('Density (cars per site)', fontsize=18)
    ax.set_ylabel('Average Flow (cars per time step)', fontsize=18)
    plt.xticks(np.arange(0, 1.1, step=0.1), fontsize=16)
    plt.yticks(fontsize=16)
    plt.scatter(densities, flow_rates, color='black', s=1)
    plt.grid()
    plt.show()
    plt.savefig("Flow_graph_2_lanes_final.pdf", dpi=600)


#write_flows(seconds)
plot_flows()
end = time.time()
print((end - start)/60)
