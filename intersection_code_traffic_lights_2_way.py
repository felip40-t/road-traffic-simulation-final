# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 13:59:37 2023

@author: felipe
"""

import numpy as np
import numpy.random as rand

max_speed = 5  # m s ^ -1
initial_density = 0.2  # cars per site
length_1 = 45  # metres / number of sites
length_2 = 30
prob_of_deceleration = 0.3
influx = 0.5 # cars / second
seconds = 30  # seconds
int_index_1 = 25
int_index_2 = 15

def translate_road(road, locs):
    final_road = ['.' for i in range(len(road))]
    for index in locs:
        final_road[index] = int(road[index])
    print(*final_road, sep='  ')

def translate_road_transpose(road, locs):
    final_road = ['.' for i in range(len(road))]
    for index in locs:
        final_road[index] = int(road[index])
    adjust = ['  ' for i in range(int_index_2)]
    final_road = np.array(final_road)
    final_road = final_road[::-1]
    transpose = np.transpose(final_road)
    return transpose, adjust

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

def accel_decel(road1, locs1, locs2, locs3, int_index, red):
    sample = rand.uniform(0, 1, size=100)
    choices = []
    n = 0
    before_light = []
    for car in locs1:
        if car < int_index:
            before_light.append(car)
    car_before = before_light[-1]
    while n < len(locs1):
        switch = rand.randint(0,2)
        choices.append(switch)
        location = int(locs1[n])
        speed = road1[location]
        # if red light - slowing down cars
        if red and location == car_before:
            if speed >= (int_index - location):
                road1[location] = int_index - location - 1
            elif (speed < max_speed) and (speed + 1) < (int_index - location):
                road1[location] += 1
        # green light and deciding wether to switch or not
        else:
            # if last car
            if location == locs1[-1]:
                if speed < max_speed:
                    road1[location] += 1
            # every other car
            else:
                # stay in same road
                if switch == 0:
                    next_veh_loc = locs1[n+1]
                    next_veh = next_veh_loc - location
                    if speed >= (next_veh):
                        road1[location] = next_veh - 1
                    elif speed < max_speed and (speed + 1) < next_veh:
                        road1[location] += 1
                # turn onto other road
                elif switch == 1 and location == car_before:
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
                elif switch == 2 and location == car_before:
                    dummy_veh = []
                    dummy_veh.extend(locs3)
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
        # random deceleration
        if road1[location] > 0:
            rand_num = rand.choice(sample)
            if rand_num < prob_of_deceleration:
                road1[location] -= 1
        n+=1
    return road1, choices

def moving_cars(road1, locs1, road2, locs2, road3, locs3, choices, int_index1, int_index2):
    new_cars1 = []
    new_cars2 = []
    new_cars2.extend(locs2)
    # moving cars
    for car in enumerate(locs1):
        location = int(car[1])
        speed = int(road1[location])
        new_location = location + speed
        if new_location < len(road1):
            if new_location < int_index1:
                new_cars1.append(new_location)
                road1[new_location] = speed
            elif choices[car[0]] == 0:
                new_cars1.append(new_location)
                road1[new_location] = speed
            elif choices[car[0]] == 1:
                new_loc = new_location - int_index1 + int_index2
                if new_loc < len(road2):
                    new_cars2.append(new_loc)
                    road2[new_loc] = speed
            elif choices[car[0]] == 2:
                new_loc = new_location - int_index1 + int_index2
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

def iterate_roads(tot_time, density):
    road_1, locs_1 = generating_simple_road(length_1, density)
    road_2, locs_2 = generating_simple_road(length_1, density)
    road_3, locs_3 = generating_simple_road(length_2, density)
    road_4, locs_4 = generating_simple_road(length_2, density)

    time = 1
    red_lights = [True, False, False, False]
    # repeating whole process for certain amount of iterations
    while time < tot_time:

        road_1, choices_1 = accel_decel(road_1, locs_1, locs_2, int_index_1, red_light_1)
        road_2, choices_2 = accel_decel(road_2, locs_2, locs_1, int_index_2, red_light_2)

        _locs_ = []
        for val in locs_2:
            if val < int_index_2:
                _locs_.append(val)

        transpose, adjust = translate_road_transpose(road_2, locs_2)
        for x in transpose[:(len(road_2) - int_index_2)]:
            print(*adjust, *x)
        translate_road(road_1, locs_1)
        for x in transpose[(len(road_2) - int_index_2):]:
            print(*adjust, *x)

        road_1, locs_1, road_2, locs_2 = moving_cars(road_1, locs_1, road_2, locs_2, choices_1, int_index_1, int_index_2)
        road_1, locs_1 = influx_gen(road_1, locs_1, influx)

        road_2, locs_2, road_1, locs_1 = moving_cars(road_2, locs_2, road_1, locs_1, choices_2, int_index_2, int_index_1)
        road_2, locs_2 = influx_gen(road_2, locs_2, influx)

        if time % 7 == 0:
            red_light_1 = not red_light_1
        print(*['-' for i in range(len(road_1))], sep='  ')
        time += 1

iterate_roads(seconds, initial_density)

