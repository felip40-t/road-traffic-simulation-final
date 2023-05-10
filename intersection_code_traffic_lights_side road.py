# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 13:59:37 2023

@author: felipe
"""

import numpy as np
import numpy.random as rand

max_speed = 5  # m s ^ -1
initial_density = 0.2  # cars per site
length_main = 30  # metres / number of sites
length_side = 15
prob_of_deceleration = 0.3
influx = 0.5 # cars / second
seconds = 30  # seconds
int_index = 15

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

def accel_decel(road1, locs1, locs2, main, red):
    sample = rand.uniform(0, 1, size=100)
    n = 0
    before_light = []
    for car in locs1:
        if main:
            if car < int_index:
                before_light.append(car)
        else:
            before_light.extend(locs1)
    car_before = before_light[-1]
    while n < len(locs1):
        location = int(locs1[n])
        speed = road1[location]
        # if red light and car before red light
        if red and location == car_before:
            # in main road
            if main:
                if speed >= (int_index - location):
                    road1[location] = int_index - location - 1
                elif (speed < max_speed) and (speed + 1) < (int_index - location):
                    road1[location] += 1
            # in side road
            else:
                if speed >= (len(road1) - location):
                    road1[location] = len(road1) - location - 1
                elif (speed < max_speed) and (speed + 1) < (len(road1) - location):
                    road1[location] += 1
        # no red light / not car before red light
        else:
            # in main road
            if main:
                # if last car
                if location == locs1[-1]:
                    if speed < max_speed:
                        road1[location] += 1
                # every other car
                else:
                    next_veh_loc = locs1[n+1]
                    next_veh = next_veh_loc - location
                    if speed >= (next_veh):
                        road1[location] = next_veh - 1
                    elif speed < max_speed and (speed + 1) < next_veh:
                        road1[location] += 1
            # in side road
            else:
                # car at end of road
                if location == locs1[-1] and not red:
                    dummy_veh = []
                    dummy_veh.extend(locs2)
                    dummy_veh.append(int_index)
                    dummy_veh.sort()
                    n = 0
                    for val in dummy_veh:
                        if val == int_index:
                            veh_ind = n
                        else:
                            n += 1
                    if dummy_veh[veh_ind] == dummy_veh[-1]:
                        if speed < max_speed:
                            road1[location] += 1
                    else:
                        next_veh_loc = dummy_veh[veh_ind + 1]
                        next_veh = next_veh_loc - int_index + len(road1) - location
                        if speed >= (next_veh):
                            road1[location] = next_veh - 1
                        elif speed < max_speed and (speed + 1) < next_veh:
                            road1[location] += 1
                # every other car
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
    return road1

def moving_cars(road1, locs1, road2, locs2, main):
    new_cars1 = []
    new_cars2 = []
    new_cars2.extend(locs2)
    # moving cars
    for car in locs1:
        location = int(car)
        speed = int(road1[location])
        new_location = location + speed
        if new_location < len(road1):
            new_cars1.append(new_location)
            road1[new_location] = speed
        elif not main:
            new_loc = new_location - len(road1) + int_index
            if new_loc < len(road2):
                new_cars2.append(new_loc)
                road2[new_loc] = speed
        road1[location] = 0
    new_cars1.sort()
    new_cars2.sort()
    return road1, new_cars1, road2, new_cars2

def car_flow(road, car_locs, length):
    n_cars = len(car_locs)
    density = n_cars / length
    v_avg = np.sum(road) / n_cars
    return density * v_avg

def process_road(road1, locs1, road2, locs2, main, red_light):
    road1 = accel_decel(road1, locs1, locs2, main, red_light)
    if main:
        translate_road(road1, locs1)
    else:
        translate_road_transpose(road1, locs1)
    road1, locs1, road2, locs2 = moving_cars(road1, locs1, road2, locs2, main)
    road1, locs1 = influx_gen(road1, locs1, influx)
    return road1, locs1, road2, locs2


def iterate_roads(tot_time, density, x):
    side_road, locs_side = generating_simple_road(length_side, density)
    main_road, locs_main = generating_simple_road(length_main, density)
    time = 1
    red_light_main = True
    flow = 0
    # repeating whole process for certain amount of iterations
    while time < tot_time:
        red_light_side = not red_light_main
        main_road, locs_main, side_road, locs_side = process_road(main_road, locs_main, side_road, locs_side, main=True, red_light=red_light_main)
        side_road, locs_side, main_road, locs_main = process_road(side_road, locs_side, main_road, locs_main, main=False, red_light=red_light_side)
        main_flow = car_flow(main_road, locs_main,length_main)
        side_flow = car_flow(side_road, locs_side,length_side)
        flow += (main_flow + side_flow) / 2
        if time % x == 0:
            red_light_main = not red_light_main
        print("\n")
        time += 1
    return (- flow) / time

t = iterate_roads(seconds, 0.2, 6)


