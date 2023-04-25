# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 13:59:37 2023

@author: felipe
"""

import numpy as np
import numpy.random as rand
import csv
import matplotlib.pyplot as plt
import time

start = time.time()

max_speed = 5  # m s ^ -1
initial_density = 0.2  # cars per site
length_1 = 1000 # metres / number of sites
length_2 = 1000
prob_of_deceleration = 0.3
#influx = 0.3 # cars / second
seconds = 10000  # seconds
int_index_1 = 500
int_index_2 = 500
interval = 6 # seconds

def translate_road(road, locs, red):
    final_road = ['.' for i in range(len(road))]
    for index in locs:
        final_road[index] = int(road[index])
    if red:
        final_road.insert(int_index_1, "r")
    print(*final_road, sep='  ')

def translate_road_transpose(road, locs, red):
    final_road = ['.' for i in range(len(road))]
    for index in locs:
        final_road[index] = int(road[index])
    if red:
        final_road.insert(int_index_2, "r")
        adjust = ['  ' for i in range(int_index_1)]
    elif not red:
        adjust = ['  ' for i in range(int_index_1 + 1)]
    final_road = np.array(final_road)
    final_road = final_road[::-1]
    transpose = np.transpose(final_road)
    return transpose, adjust

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
    car_indices.sort()
    return road, car_indices

def influx_gen(road, locs, influx):
    sample = rand.uniform(0,1, size=100)
    val = rand.choice(sample)
    if len(locs) == 0:
        speed = rand.randint(0,max_speed+1)
        road[0] = speed
        locs.insert(0,0)
    if (val < influx) and (locs[0] != 0):
        speed = rand.randint(0,max_speed+1)
        road[0] = speed
        locs.insert(0,0)
    return road, locs

def accel_decel(road1, locs1, locs2, int_index_1, int_index_2, red):
    sample = rand.uniform(0, 1, size=100)
    n = 0
    before_light = []
    choices = [0 for i in range(len(locs1))]
    for car in locs1:
        if car < int_index_1:
            before_light.append(car)
    try:
        car_before = before_light[-1]
    except IndexError:
        car_before = -1
    while n < len(locs1):
        location = locs1[n]
        speed = road1[location]
        # if red light - slowing down cars
        if red and location == car_before:
            if speed >= (int_index_1 - location):
                road1[location] = int_index_1 - location - 1
            elif (speed < max_speed) and (speed + 1) < (int_index_1 - location):
                road1[location] += 1
        # green light and deciding wether to switch or not
        elif location == car_before and speed >= int_index_1 - location:
            switch = rand.randint(0,2)
            choices[n] = switch
            if switch == 0:
                if location == locs1[-1]:
                    if speed < max_speed:
                        road1[location] += 1
                else:
                    next_veh_loc = locs1[n+1]
                    next_veh = next_veh_loc - location
                    if speed >= (next_veh):
                        road1[location] = next_veh - 1
                    elif speed < max_speed and (speed + 1) < next_veh:
                        road1[location] += 1
            # turn onto other road
            elif switch == 1:
                dummy_veh = []
                dummy_veh.extend(locs2)
                dummy_veh.append(int_index_2)
                dummy_veh.sort()
                m = 0
                for val in dummy_veh:
                    if val == int_index_2:
                        veh_ind = m
                    else:
                        m += 1
                if dummy_veh[veh_ind] == dummy_veh[-1]:
                    if speed < max_speed:
                        road1[location] += 1
                else:
                    next_veh_loc = dummy_veh[veh_ind + 1]
                    next_veh = next_veh_loc - int_index_2 + int_index_1 - location
                    if speed >= (next_veh):
                        road1[location] = next_veh - 1
                    elif speed < max_speed and (speed + 1) < next_veh:
                        road1[location] += 1
        else:
            if location == locs1[-1]:
                if speed < max_speed:
                    road1[location] += 1
            else:
                next_veh_loc = locs1[n+1]
                next_veh = next_veh_loc - location
                if speed >= (next_veh):
                    road1[location] = next_veh - 1
                elif speed < max_speed and (speed + 1) < next_veh:
                    road1[location] += 1
        # random deceleration
        if road1[location] > 0:
            rand_num = rand.choice(sample)
            if rand_num < prob_of_deceleration:
                road1[location] -= 1
        n+=1
    return road1, choices

def moving_cars(road1, locs1, road2, locs2, choices1, choices2, int_index1, int_index2):
    new_cars1 = []
    new_cars2 = []
    new_cars2.extend(locs2)
    # moving cars
    for car in enumerate(locs1):
        switch = choices1[car[0]]
        location = int(car[1])
        speed = int(road1[location])
        new_location = location + speed
        if new_location < len(road1):
            if switch == 1:
                new_loc = new_location - int_index1 + int_index2
                new_cars2.append(new_loc)
                road2[new_loc] = speed
                choices2.append(0)
            else:
                new_cars1.append(new_location)
                road1[new_location] = speed
        road1[location] = 0
    new_cars1.sort()
    new_cars2.sort()
    return road1, new_cars1, road2, new_cars2, choices2

def car_flow(road, locs, length):
    n = len(locs)
    density = n/length
    v_avg = np.sum(road)/n
    return density*v_avg

def iterate_roads(tot_time, density, interval):
    road_1, locs_1 = generating_simple_road(length_1, density)
    road_2, locs_2 = generating_simple_road(length_2, density)
    time = 1
    red_light_1 = True
    flow = 0
    dens = []
    # repeating whole process for certain amount of iterations
    while time < tot_time:
        if len(locs_1) == 0 and len(locs_2) == 0:
            break
        red_light_2 = not red_light_1
        road_1, choices_1 = accel_decel(road_1, locs_1, locs_2, int_index_1, int_index_2, red_light_1)
        road_2, choices_2 = accel_decel(road_2, locs_2, locs_1, int_index_2, int_index_1, red_light_2)
        """
        transpose, adjust = translate_road_transpose(road_2, locs_2, red_light_2)
        for x in transpose[:(length_2 - int_index_2)]:
            print(*adjust, *x)
        translate_road(road_1, locs_1, red_light_1)
        for x in transpose[(length_2 - int_index_2):]:
            print(*adjust, *x)
        """
        if red_light_1:
            road_1, locs_1, road_2, locs_2, choices_2 = moving_cars(road_1, locs_1, road_2, locs_2, choices_1, choices_2, int_index_1, int_index_2)
            #road_1, locs_1 = influx_gen(road_1, locs_1, density)
            road_2, locs_2, road_1, locs_1, choices_1 = moving_cars(road_2, locs_2, road_1, locs_1, choices_2, choices_1, int_index_2, int_index_1)
            #road_2, locs_2 = influx_gen(road_2, locs_2, density)
        if red_light_2:
            road_2, locs_2, road_1, locs_1, choices_1 = moving_cars(road_2, locs_2, road_1, locs_1, choices_2, choices_1, int_index_2, int_index_1)
            #road_2, locs_2 = influx_gen(road_2, locs_2, density)
            road_1, locs_1, road_2, locs_2, choices_2 = moving_cars(road_1, locs_1, road_2, locs_2, choices_1, choices_2, int_index_1, int_index_2)
            #road_1, locs_1 = influx_gen(road_1, locs_1, density)

        if time % interval == 0:
            red_light_1 = not red_light_1

        test_road = road_1[:int_index_1]
        test_locs = []
        for loc in locs_1:
            if loc < int_index_1:
                test_locs.append(loc)

        #flow += car_flow(test_road, test_locs, len(test_road))
        dens.append(len(locs_1) / len(road_1))
        time += 1
    times = list(range(1,time))
    return times, dens

def write_flows(time):
    densities = rand.uniform(low=0.01, high=1, size=10)
    flow_rates = []
    avg_densities = []
    for rho in (densities):
        for inter in range(1,11):
            y, x = iterate_roads(seconds, 0.3, interval)
        flow_rate, avg_density = iterate_roads(time, rho, 6)
        flow_rates.append(flow_rate)
        avg_densities.append(avg_density)
        with open("flow_rate_intersection_4.csv", 'a', encoding='utf-8') as data:
            writer = csv.writer(data)
            writer.writerow([avg_density, flow_rate])

def plot_flows():
    #data = np.genfromtxt("flow_rate_intersection_4.csv", dtype='float',
     #                    delimiter=',', skip_header=1)
    #time = data[:, 0]
    #densities = data[:, 1]
    #times = list(range(1,seconds))
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    ax.set_title('Densities for one of the roads at an intersection', fontsize=18)
    ax.set_xlabel('Time (seconds)', fontsize=18)
    ax.set_ylabel('Density of cars (cars per site)', fontsize=18)
    plt.xticks(fontsize=16)
    #plt.ylim(0.15,0.35)
    plt.yticks(fontsize=16)
    plt.grid()
    colours = ['red', 'blue', 'black', 'green', 'orange', 'yellow', 'purple', 'cyan', 'magenta', 'dodgerblue']
    for inter in range(11,21):
        x, y = iterate_roads(seconds, 0.3, inter)
        plt.scatter(x, y, s=1, c=colours[inter-11], alpha=1, label=inter)
    plt.legend(loc='best', title='interval times for traffic lights (sec)', markerscale=4)
    plt.show()
    plt.savefig("intersection_test7.pdf", dpi=400)

#write_flows(seconds)
plot_flows()

end = time.time()
print((end - start)/60)