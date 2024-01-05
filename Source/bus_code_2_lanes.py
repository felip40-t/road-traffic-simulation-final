# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 20:34:15 2023

@author: felipe

This code is a 2 lane system where there are busses in both lanes

"""

import numpy as np
import numpy.random as rand
import matplotlib.pyplot as plt
import time
import csv
import bus_code

max_speed = 5  # m s ^ -1
car_density = 0.3  # cars per site
bus_density = 0.1 # busses per site
road_length = 30  # metres / number of sites
prob_of_deceleration = 0.3
seconds = 10  # seconds
influx = True
influx_car = 0.2 # cars per second
influx_bus = 0.4 # busses per second


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
            # adding location of car into other lane
            locs2.append(car_loc)
            locs2.sort()
            # finding index of car in locs2
            test_car_index = int(np.where(car_loc == np.array(locs2))[0])
            # for last car in road
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

def iterate_switching(tot_time, rho_car, rho_bus):
    t = 0
    road, car_indices, bus_indices = bus_code.generating_simple_road(rho_car, rho_bus)
    # repeating whole process for certain amount of iterations
    while t < tot_time:

        road, vehicle_locs = bus_code.accel_decel(road, car_indices, bus_indices)
        bus_code.translate_road(road, vehicle_locs)
        road, car_indices, bus_indices, vehicle_locs = bus_code.moving_cars(road, car_indices, bus_indices)
        if influx:
            road, car_indices, bus_indices, vehicle_locs = bus_code.influx_gen(road, vehicle_locs, car_indices, bus_indices)
        t += 1