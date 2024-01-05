# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 15:19:46 2023

@authors:  Felipe Tcach and Joshua Fatimilehin-Tulip

Title:
    Road Traffic Simulation

Description:
    Simulation of road traffic and the effects of traffic lights on the distribution
    of traffic.

"""
import numpy as np
import numpy.random as rand
import matplotlib.pyplot as plt
import time
import csv

start = time.time()

max_speed = 5  # m s ^ -1
initial_density = 0.3  # cars per site
road_length_1 = 1500  # metres / number of sites
road_length_2 = 2000  # metres / number of sites
prob_of_deceleration = 0.3
seconds = 10000  # seconds
influx = False
influx_rate = 0.2 # cars per second

def translate_road(road, loc_cars):
    final_road = ['.' for i in range(len(road))]
    locs = list(map(int, loc_cars))
    for index in locs:
        final_road[index] = int(road[index])
    print(*final_road, sep='  ')

def influx_gen(road, locs, influx_p):
    sample = rand.uniform(0,1, size=100)
    val = rand.choice(sample)
    if len(locs) == 0:
        speed = rand.randint(0,max_speed+1)
        road[0] = speed
        locs.insert(0,0)
    if (val < influx_p) and (locs[0] != 0):
        speed = rand.randint(0,max_speed+1)
        road[0] = speed
        locs.insert(0, 0)
    return road, locs

def generating_simple_road(length, density):
    num_cars = int(np.floor(length * density))
    road = np.zeros(length)
    road_indices = []
    for i in range(length):
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
    # sorting array for car indices
    car_indices.sort()
    return road, car_indices

def accel_decel(road, loc_cars, obstr):
    sample = rand.uniform(0, 1, size=100)
    n = 0
    while n < len(loc_cars):
        location = int(loc_cars[n])
        speed = road[location]
        if location == loc_cars[-1]:
            if obstr:
                if speed >= len(road) - location:
                    road[location] = len(road) - location - 1
                elif speed < max_speed and speed + 1 < len(road) - location:
                    road[location] += 1
            elif speed < max_speed:
                road[location] += 1
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

    return road

def moving_cars(road, loc_cars):
    n = 0
    new_locs = []
    # moving cars
    while n < len(loc_cars):
        location = int(loc_cars[n])
        speed = road[location]
        new_location = int(location + speed)
        if new_location < len(road):
            new_locs.append(new_location)
            road[new_location] = speed
        road[location] = 0
        n += 1
    return road, new_locs

def neighbour_finder(locs1, locs2):
    neighbours = []
    for i in locs1:
        if i in locs2:
            neighbours.append(i)
    return neighbours

def compare_2_lanes(locs1, locs2, length_1, length_2):
    # finding neighbour indices
    neighbours = neighbour_finder(locs1, locs2)
    distances = []
    # iterating through each car
    index = 0
    while index < len(locs1):
        car_loc = locs1[index]
        # return 0s if car has a neighbour
        if car_loc in neighbours:
            distances.append((0, 0))
        else:
            # adding location of car into other lane
            locs2.append(car_loc)
            locs2.sort()
            # finding index of car in locs2
            test_car_index = int(np.where(car_loc == np.array(locs2))[0])
            # for last car in road
            if locs1[index] == locs1[-1]:
                next_car_d_1 = length_1 - car_loc
                if locs2[test_car_index] == locs2[-1]:
                    next_car_d_2 = length_2 - car_loc
                else:
                    next_car_d_2 = locs2[test_car_index + 1] - car_loc
            else:
                next_car_d_1 = locs1[index + 1] - car_loc
                if locs2[test_car_index] == locs2[-1]:
                    next_car_d_2 = length_2 - car_loc
                else:
                    next_car_d_2 = locs2[test_car_index + 1] - car_loc
            distances.append((next_car_d_1, next_car_d_2))
            locs2.remove(car_loc)
        index += 1
    return distances

def switch(lane1, lane2, locs1, locs2, distances):
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
                distances = compare_2_lanes(locs1, locs2, road_length_1, road_length_2)
        index += 1
    return lane1, lane2, locs1, locs2

def car_flow(road, car_locs):
    n_cars = len(car_locs)
    density = n_cars / len(road)
    v_avg = np.sum(road)/n_cars
    return density*v_avg

def iterating_switching(tot_time, density):
    time = 0
    road1, locs1 = generating_simple_road(road_length_1, density)
    road2, locs2 = generating_simple_road(road_length_2, density)
    flow = []
    times = []
    while time < tot_time:
        if len(locs1) == 0 and len(locs2) == 0:
            break
        distances_12 = compare_2_lanes(locs1, locs2, road_length_1, road_length_2)
        road1, road2, locs1, locs2 = switch(road1, road2, locs1, locs2, distances_12)
        road1 = accel_decel(road1, locs1, True)
        road2 = accel_decel(road2, locs2, False)
        #translate_road(road1, locs1)
        #translate_road(road2, locs2)
        #print("\n----------\n")
        road1, locs1 = moving_cars(road1, locs1)
        road2, locs2 = moving_cars(road2, locs2)
        if influx:
            road1, locs1 = influx_gen(road1, locs1, density)
            road2, locs2 = influx_gen(road2, locs2, density)
        flow.append(car_flow(road2, locs2))
        times.append(time)
        time += 1
    return flow, times

def iterating_switching_world(tot_time, density):
    time2 = 0
    road1, locs1 = generating_simple_road(road_length_1, density)
    road2, locs2 = generating_simple_road(road_length_2, density)
    total_locs_1 = []
    total_locs_2 = []
    while time2 < tot_time:
        if len(locs1) == 0 and len(locs2) == 0:
            print("All cars have left the road.")
            break
        distances_12 = compare_2_lanes(locs1, locs2, road_length_1, road_length_2)
        road1, road2, locs1, locs2 = switch(road1, road2, locs1, locs2, distances_12)
        road1 = accel_decel(road1, locs1, True)
        road2 = accel_decel(road2, locs2, False)
        #translate_road(road1, locs1)
        #translate_road(road2, locs2)
        #print("\n----------\n")
        road1, locs1 = moving_cars(road1, locs1)
        road2, locs2 = moving_cars(road2, locs2)
        if influx:
            road1, locs1 = influx_gen(road1, locs1, density)
            road2, locs2 = influx_gen(road2, locs2, density)
        if len(locs1) == 0:
            time1 = time2
        total_locs_2.extend([locs2])
        total_locs_1.extend([locs1])
        time2 += 1
    return time1, time2, total_locs_1, total_locs_2

def write_flows(time):
    densities = rand.uniform(low=0.01, high=1, size=20)
    flow_rates = []
    avg_densities = []
    for rho in densities:
        avg_density, flow_rate = iterating_switching(time, rho)
        flow_rates.append(flow_rate)
        avg_densities.append(avg_density)
        with open("flow_rate_bottleneck_2.csv", 'a', encoding='utf-8') as data:
            writer = csv.writer(data)
            writer.writerow([avg_density, flow_rate])

def plot_flows():
    """
    data = np.genfromtxt("flow_rate_bottleneck_2.csv", dtype='float',
                        delimiter=',', skip_header=1)
    densities = data[:, 0]
    flow_rates = data[:, 1]
    """
    flows, times = iterating_switching(seconds, initial_density)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    ax.set_title('Rate of Flow Graph for Unobstructed Lane\n     in Bottleneck Scenario', fontsize=18)
    ax.set_xlabel('Time (seconds)', fontsize=17)
    ax.set_ylabel('Rate of Flow (cars per second)', fontsize=17)
    plt.xticks(fontsize=16)
    plt.ylim(0,0.5)
    plt.yticks(np.arange(0,0.6,step=0.1),fontsize=16)
    plt.grid()
    plt.scatter(times, flows, s=1, c='black', alpha=1)
    plt.legend(title='        Road Length = 2000 m\n Obstruction location = 1500 m\n        Initial density = 0.3\nDeceleration probability = 0.3', title_fontsize=16)
    plt.show()
    plt.savefig("bottleneck_flow_graph_5.pdf", dpi=400)

def plot_world_lines():
    time1, time2, locs1, locs2 = iterating_switching_world(seconds, initial_density_of_cars)

    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111)

    ax.set_title('World lines for cars \n (initial density = 0.3, influx rate = 0.2, probability of deceleration = 0.3, road 1 length = 200m , road 2 length = 400m)', fontsize=12)
    ax.set_xlabel('Space (metres)', fontsize=8)
    ax.set_ylabel('Time (seconds)', fontsize=8)
    for i in range(time1):
        xvals1 = locs1[i]
        yvals1 = np.linspace(i, i, len(xvals1))
        plt.scatter(xvals1, yvals1, color='blue', s=1.5)
    for j in range(time2):
        xvals2 = locs2[j]
        yvals2 = np.linspace(j,j, len(xvals2))
        plt.scatter(xvals2, yvals2, color='red', s=0.4)
    plt.show()
    plt.savefig('World_lines_bottleneck_both.pdf', dpi=400)

plot_flows()
end = time.time()
print((end - start)/60)

#iterating_switching(seconds, initial_density_of_cars)