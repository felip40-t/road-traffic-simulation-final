# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 13:59:37 2023

@author: felipe
"""

import numpy as np
import numpy.random as rand

max_speed = 5  # m s ^ -1
initial_density = 0.2  # cars per site
length_main = 20  # metres / number of sites
length_side = 10
prob_of_deceleration = 0.2
politeness = 1 # metres
influx = 0.4 # cars / second
seconds = 15  # seconds
int_index = 10

def translate_road(road, locs):
    final_road = ['.' for i in range(len(road))]
    for index in locs:
        final_road[index] = int(road[index])
    print(*final_road, sep='  ')

def translate_road_transpose(road, locs):
    final_road = ['.' for i in range(len(road))]
    for index in locs:
        final_road[index] = int(road[index])
    adjust = ['  ' for i in range(int_index)]
    final_road = np.array(final_road)
    final_road = final_road[::-1]
    transpose = np.transpose(final_road)
    for x in transpose:
        print(*adjust, *x)

def generating_simple_road(length, density):
    num_cars = int(np.floor(length * density))
    # generating road array
    road = np.zeros(length)
    # generating indices and speeds for cars
    road_indices = []
    for i in range(length):
        road_indices.append(i)
    car_indices = []
    n = 0
    while n < num_cars:
        # generating random index for each car.
        car_index = rand.choice(road_indices)
        car_indices.append(car_index)
        # deleting this index from the original list of indices so that 2 cars
        # aren't generated in the same place
        road_indices.remove(car_index)
        # generating random speed
        car_speed = rand.randint(0, max_speed+1)
        # placing car on road
        road[car_index] = car_speed
        n += 1
    # sorting array for car indices
    car_indices.sort()
    return road, car_indices

def influx_gen(road, locs, influx):
    sample = rand.uniform(0,1, size=1000)
    val = rand.choice(sample)
    if (val < influx) and (locs[0] != 0):
        speed = rand.randint(0,max_speed+1)
        road[0] = speed
        locs.append(0)
        locs.sort()
    return road, locs

def accel_decel(road, loc_cars, main_road):
    sample = rand.uniform(0, 1, size=100)
    n = 0
    while n < len(loc_cars):
        location = int(loc_cars[n])
        speed = road[location]
        if location == loc_cars[-1]:
            if main_road:
                if speed < max_speed:
                    road[location] += 1
            else:
                if speed >= (len(road) - location):
                    road[location] = len(road) - location - 1
                elif (speed < max_speed) and (speed + 1) < (len(road) - location):
                    road[location] += 1
        else:
            next_veh_loc = loc_cars[n+1]
            next_veh = next_veh_loc - location
            if speed >= (next_veh):
                road[location] = next_veh - 1
            elif speed < max_speed and (speed + 1) < next_veh:
                road[location] += 1
        if road[location] != 0:
            rand_num = rand.choice(sample)
            if rand_num < prob_of_deceleration:
                road[location] -= 1
        n+=1
    return road, loc_cars

def moving_cars(road, loc_cars, main_road):
    new_cars = []
    # moving cars
    for car in loc_cars:
        location = int(car)
        speed = int(road[location])
        new_location = int(location + speed)
        if new_location < len(road):
            new_cars.append(new_location)
            road[new_location] = speed
        road[location] = 0
    new_cars.sort()
    return road, new_cars

def switch_int(main_road, side_road, locs_main, locs_side):
    switch = False
    # getting cars at end of side road to turn onto main road
    if (locs_side[-1] == (len(side_road) - 1)) and (not int_index in locs_main):
        locs_main.append(int_index)
        locs_main.sort()
        n = 0
        for val in locs_main:
            if val == int_index:
                veh_ind = n
            else:
                n += 1
        test_loc = locs_main[veh_ind]
        if test_loc == locs_main[0]:
            switch = True
        else:
            car_behind = locs_main[veh_ind - 1]
            if np.abs(car_behind - test_loc) > politeness:
                switch = True
        if switch:
            locs_side.remove(locs_side[-1])
        if not switch:
            locs_main.remove(test_loc)
    return main_road, side_road, locs_main, locs_side

def process_road(road, locs, main_road):
    road, locs = accel_decel(road, locs, main_road)
    if main_road:
        translate_road(road, locs)
    else:
        translate_road_transpose(road, locs)
    road, locs = moving_cars(road, locs, main_road)
    road, locs = influx_gen(road, locs, influx)
    return road,locs


def iterate_roads(tot_time, density):
    side_road, locs_side = generating_simple_road(length_side, density)
    main_road, locs_main = generating_simple_road(length_main, density)
    time = 0
    # repeating whole process for certain amount of iterations
    while time < tot_time:
        if (len(locs_side) == 0) and (len(locs_main) == 0):
            print("All cars have now left the road.")
            break
        main_road, locs_main = process_road(main_road, locs_main, main_road=True)
        side_road, locs_side = process_road(side_road, locs_side, main_road=False)

        main_road, side_road, locs_main, locs_side = switch_int(main_road, side_road, locs_main, locs_side)
        print("\n")
        time += 1

iterate_roads(seconds, initial_density)
