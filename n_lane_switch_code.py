# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 16:34:56 2023

@author: felip
"""

import numpy as np
import numpy.random as rand

max_speed = 5  # m s ^ -1
road_length = 10  # metres / number of sites
initial_density = 0.3 # cars / site
prob_of_deceleration = 0.3
prob_switch_down = 0.5
seconds = 2 # seconds
num_of_lanes = 3


def translate_road(road, loc_cars):
    final_road = ['.' for i in range(len(road))]
    locs = list(map(int, loc_cars))
    for index in locs:
        final_road[index] = int(road[index])
    print(*final_road, sep='  ')

def generating_simple_road(density):
    num_cars = int(np.floor(road_length * density))
    # generating road array
    road = np.zeros(road_length)
    # generating indices and speeds for cars
    road_indices = range(road_length)
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
        car_speed = rand.randint(0, max_speed+1)
        # placing car on road
        road[car_index] = car_speed
        n += 1
    # sorting array for car indices
    car_indices = np.sort(car_indices)
    car_indices.tolist()
    return road, car_indices

def accel_decel(road, loc_cars):
    n = 0
    # loop for the cars which aren't at the end of the road
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
                road[location] = next_veh - 1
        n += 1

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
    #translate_road(road, loc_cars, red_light_index)
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
    new_locs = np.sort(new_locs)
    new_locs.tolist()
    return road, new_locs

def neighbour_finder(locs1, locs2):
    neighbours = []
    for i in locs1:
        if i in locs2:
            neighbours.append(i)
    return neighbours

def compare_2_lanes(locs1, locs2):
    """

    This function compares the cars in 2 lanes, with locs1 being the
    main one, so it will return the values for the cars in locs1.
    It returns the distances to the next car in each lane for each car in lane1
    in the form of an array of tuples.
    If there are any neighbours it will return (0,0) for this car.

    """
    # finding neighbour indices
    neighbours = neighbour_finder(locs1, locs2)
    # converting numpy.arrays to lists
    locs1 = locs1.tolist()
    locs2 = locs2.tolist()
    distances = []
    switching = []
    # iterating through each car
    index = 0
    while index < len(locs1):
        car_loc = locs1[index]
        # return 0s if car has a neighbour
        if car_loc in neighbours:
            distances.append((0, 0))
            switching.append(0)
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
            switching.append(1)
            locs2.remove(car_loc)
        index += 1
    return distances

def switch_2_lanes(lane1, lane2, locs1, locs2, switch):
    """
    This just swiches the cars from lane1 to lane2 using the distances list of tuples
    """
    index = 0
    while index < len(locs1):
        s = switch[index]
        car_loc = int(locs1[index])
        if s != 0:
            lane2[car_loc] = lane1[car_loc]
            lane1[car_loc] = 0
            locs2 = np.sort(np.append(locs2, car_loc))
            locs1 = np.delete(locs1, np.where(car_loc == locs1)[0])
            _, switch = compare_2_lanes(locs1, locs2)
        index += 1
    return lane1, lane2, locs1, locs2

def switch_3_lanes(ds_up, ds_down,switch_up, switch_down, lanes, locs, prob_switch_down):
    sample = rand.uniform(0, 1, size=1000)
    lane_c = lanes[1]
    lane_up = lanes[0]
    lane_down = lanes[2]
    locs_c = locs[1]
    locs_up = locs[0]
    locs_down = locs[2]
    move_up = False
    move_down = False
    index = 0
    while index < len(locs_c):
        tup_up = ds_up[index]
        tup_down = ds_down[index]
        s_up = switch_up[index]
        s_down = switch_down[index]
        car_loc = int(locs_c[index])
        if (s_up == 1) and (s_down == 1):
            if tup_up[1] > tup_down[1]:
                move_up = True
            if tup_down[1] > tup_up[1]:
                move_down = True
            else:
                rand_num = rand.choice(sample)
                if rand_num < prob_switch_down:
                    move_down = True
                else:
                    move_up = True
        elif (s_up == 1) and (s_down == 0):
            move_up = True
        elif s_down == 1 and (s_up == 0):
            move_down = True
        if move_up:
            lane_up[car_loc] = lane_c[car_loc]
            lane_c[car_loc] = 0
            locs_up = np.sort(np.append(locs_up, car_loc))
            locs_c = np.delete(locs_c, np.where(car_loc == locs_c)[0])
            ds_up, switch_up = compare_2_lanes(locs_c, locs_up)
        if move_down:
            lane_down[car_loc] = lane_c[car_loc]
            lane_c[car_loc] = 0
            locs_down = np.sort(np.append(locs_down, car_loc))
            locs_c = np.delete(locs_c, np.where(car_loc == locs_c)[0])
            ds_down, switch_down = compare_2_lanes(locs_c, locs_down)
        index += 1
    lanes = [lane_up, lane_c, lane_down]
    locs = [locs_up, locs_c, locs_down]
    return lanes, locs

def iterating_switching_2_lanes(tot_time):
    time = 0
    road1, locs1 = generating_simple_road(max_speed, road_length)
    road2, locs2 = generating_simple_road(max_speed, road_length)
    while time < tot_time:
        road1, road2, locs1, locs2 = switch_2_lanes(road1, road2, locs1, locs2)
        road1, locs1 = accel_decel(max_speed, road1, locs1)
        road2, locs2 = accel_decel(max_speed, road2, locs2)
        print("\n")
        road1, locs1 = moving_cars(road1, locs1)
        road2, locs2 = moving_cars(road2, locs2)
        time += 1

def generate_n_lanes(n_lanes, density):
    road_matrix = []
    locs_matrix = []
    for i in range(n_lanes):
        road, indices = generating_simple_road(max_speed, road_length, density)
        road_matrix.append(road)
        locs_matrix.append(indices)
        translate_road(road, indices)
    return road_matrix, locs_matrix

def switch_n_lanes(n_lanes, road_matrix, loc_matrix):
    for lane in range(n_lanes):
        if lane == 0:
            lane_top = road_matrix[0]
            lane_down = road_matrix[1]
            locs_top = loc_matrix[0]
            locs_down = loc_matrix[1]
            _,switch = compare_2_lanes(locs_top, locs_down)
            road_matrix[0], road_matrix[1], loc_matrix[0], loc_matrix[1] = switch_2_lanes(lane_top, lane_down, locs_top, locs_down, switch)
        if (lane == (n_lanes - 1)):
            lane_bottom = road_matrix[-1]
            lane_up = road_matrix[-2]
            locs_bottom = loc_matrix[-1]
            locs_up = loc_matrix[-2]
            _, switch = compare_2_lanes(locs_bottom, locs_up)
            road_matrix[-1], road_matrix[-2], loc_matrix[-1], loc_matrix[-2] = switch_2_lanes(lane_bottom, lane_up, locs_bottom, locs_up, switch)
        elif (lane > 0) & (lane < (n_lanes - 1)):
            lanes = road_matrix[lane-1:lane+2]
            locs = loc_matrix[lane-1:lane+2]

            distances_up, switch_up = compare_2_lanes(locs[1], locs[0])
            distances_down, switch_down = compare_2_lanes(locs[1], locs[2])

            lanes, locs = switch_3_lanes(distances_up, distances_down, switch_up, switch_down, lanes, locs, prob_switch_down)
            road_matrix[lane] = lanes[1]
            road_matrix[lane + 1] = lanes[2]
            road_matrix[lane - 1] = lanes[0]
            loc_matrix[lane] = locs[1]
            loc_matrix[lane + 1] = locs[2]
            loc_matrix[lane - 1] = locs[0]
    print(road_matrix)
    print(loc_matrix)
    return road_matrix, loc_matrix

def translate_n_lanes(road, locs):
    for index in range(len(road)):
        translate_road(road[index], locs[index])

def main(n, density):
    road, locs = generate_n_lanes(n, density)
    road, locs = switch_n_lanes(n, road, locs)
    print("\n")
    translate_n_lanes(road, locs)



main(num_of_lanes, initial_density)