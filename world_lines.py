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

max_speed = 5  # m s ^ -1
initial_density = 0.2  # cars per site
road_length = 30  # metres / number of sites
prob_of_deceleration = 0.25
seconds = 20  # seconds
roundabout = False

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
    n = 0
    sample = rand.uniform(0, 1, size=100)
    while n < len(loc_cars):
        location = int(loc_cars[n])
        speed = road[location]
        if location == loc_cars[-1]:
            if roundabout:
                if speed < max_speed and (speed + 1) < (loc_cars[0] - location + len(road)):
                    road[location] += 1
                if speed >= (loc_cars[0] - location + len(road)):
                    road[location] = (loc_cars[0] - location + len(road)) - 1
            else:
                if speed < max_speed:
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
                road[location] = road[location] - 1
        n += 1
    return road

def moving_cars(road, loc_cars):
    new_locs = []
    for car in loc_cars:
        location = int(car)
        speed = int(road[location])
        new_location = int(location + speed)
        if new_location < len(road):
            new_locs.append(new_location)
            road[new_location] = speed
        road[location] = 0
    new_locs.sort()
    return road, new_locs

def iterate_road_plot_worldlines(tot_time, density):
    time = 0
    total_indices = []
    road, car_indices = generating_simple_road(density)
    # repeating whole process for certain amount of iterations
    while time < tot_time:
        if len(car_indices) == 0:
            print("All cars have now left the road.")
            break

        road = accel_decel(road, car_indices)
        translate_road(road, car_indices)
        road, car_indices = moving_cars(road, car_indices)
        total_indices.extend([car_indices])
        time += 1


def plot_world_lines(locs, time):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111)
    ax.set_title('World lines for cars', fontsize=20)
    ax.set_xlabel('Space (metres)', fontsize=18)
    ax.set_ylabel('Time (seconds)', fontsize=18)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    # plotting for linear road
    for i in range(time):
        xvals = locs[i]
        yvals = np.linspace(i, i, len(xvals))
        plt.scatter(xvals, yvals, color='black', s=0.3)
    plt.show()
    plt.savefig('World_lines_linear_lane_final6.pdf', dpi=100)

def main(time):

    iterate_road_plot_worldlines(time, initial_density)
    #plot_world_lines(locs, time)

main(seconds)
