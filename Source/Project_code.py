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

max_speed = 10  # m s ^ -1
initial_density = 0.3  # cars per site
road_length = 1500  # metres / number of sites
prob_of_deceleration = 0.3
seconds = 400  # seconds
red_light = False
roundabout = False

def translate_road(road, loc_cars, red_light_index):
    final_road = ['.' for i in range(len(road))]
    locs = list(map(int, loc_cars))
    for index in locs:
        final_road[index] = int(road[index])
    if red_light:
        final_road[red_light_index] = 'red'
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
        # choosing traffic light index
        red_light_index = rand.choice(road_indices)
        # generating random speed
        car_speed = rand.randint(0, max_speed+1)
        # placing car on road
        road[car_index] = car_speed
        n += 1
    # sorting array for car indices
    car_indices = np.sort(car_indices)
    car_indices.tolist()
    return road, car_indices, red_light_index

def accel_decel(road, loc_cars, red_light_index):
    n = 0
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
                road[location] = next_veh - 1
        n += 1

    # traffic light case
    if red_light:
        cars_before_index = np.where(red_light_index - loc_cars > 0)[0]
        cars_before = np.sort(loc_cars[cars_before_index])
        if len(cars_before) != 0:
            car_distance = int(np.min(red_light_index - cars_before))
            car_before = int(cars_before[np.where(
                car_distance == red_light_index - cars_before)[0]])
            speed = road[car_before]
            if speed >= car_distance:
                road[car_before] = car_distance - 1
        else:
            if roundabout:
                car_before = int(loc_cars[-1])
                car_distance = red_light_index - car_before + len(road)
                speed = road[car_before]
                if speed >= car_distance:
                    road[car_before] = car_distance - 1
            else:
                print("There are no cars before the traffic light.")

    # generating random numbers for random deceleration
    n = 0
    sample = rand.uniform(0, 1, size=1000)
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
    # moving cars which aren't at the end of the road
    while n < len(loc_cars):
        location = int(loc_cars[n])
        speed = road[location]
        if n == len(loc_cars) - 1:
            if roundabout:
                if speed >= len(road) - location:
                    new_location = int(location + speed - len(road))
                else:
                    new_location = int(location + speed)
            else:
                if speed >= len(road) - location:
                    new_location = len(road)
                    road[location] = 0
                else:
                    new_location = int(location + speed)
        else:
            new_location = int(location + speed)
        if new_location < len(road):
            new_locs.append(new_location)
            road[new_location] = speed
        road[location] = 0
        n += 1
    new_locs = np.sort(new_locs)
    new_locs.tolist()
    return road, new_locs

def iterate_road_basic(tot_time, density):
    time = 0
    road, car_indices, red_light_index = generating_simple_road(density)
    # repeating whole process for certain amount of iterations
    while time < tot_time:
        if len(car_indices) == 0:
            print("All cars have now left the road.")
            break

        road, car_indices = accel_decel(
            max_speed, road, car_indices, red_light_index, roundabout)
        road, car_indices = moving_cars(road, car_indices, roundabout)
        car_indices.tolist()
        time += 1

def iterate_road_traffic_light(tot_time, density):
    time = 0
    road, car_indices, red_light_index = generating_simple_road(
        max_speed, road_length, density)
    # repeating whole process for certain amount of iterations
    while time < tot_time:
        if len(car_indices) == 0:
            print("All cars have now left the road.")
            break

        road, car_indices = accel_decel(road, car_indices, red_light_index)
        road, car_indices = moving_cars(road, car_indices)
        if time % 100 == 0:
            global red_light
            red_light = not red_light
        time += 1

def iterate_road_plot_worldlines(tot_time, density):
    time = 0
    total_indices = []
    road, car_indices, red_light_index = generating_simple_road(
        max_speed, road_length, density)
    # repeating whole process for certain amount of iterations
    while time < tot_time:
        if len(car_indices) == 0:
            print("All cars have now left the road.")
            break

        road, car_indices = accel_decel(
            max_speed, road, car_indices, red_light_index, roundabout)
        road, car_indices = moving_cars(road, car_indices, roundabout)
        car_indices.tolist()
        total_indices.extend([car_indices])
        time += 1
    return total_indices, time


def plot_world_lines(locs, time):

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)

    ax.set_title('World lines for cars', fontsize=11)
    ax.set_xlabel('Space (metres)', fontsize=8)
    ax.set_ylabel('Time (seconds)', fontsize=8)
    # plotting for linear road
    for i in range(time):
        xvals = locs[i]
        yvals = np.linspace(i, i, len(xvals))
        plt.scatter(xvals, yvals, color='black', s=0.6)
    plt.show()
    plt.savefig('World_lines_linear_lane_final2.pdf', dpi=100)


"""
SAVING AS PDF IS FASTER FOR LATEX COMPLILING AND RESULTS IN A
SMALLER FILE SIZE OF ONLY 120kB instead of 2MB
"""

def neighbour_finder(locs1, locs2):
    neighbours = []
    for i in locs1:
        if i in locs2:
            neighbours.append(i)
    return neighbours

def compare_2_lanes(locs1, locs2):
    """

    This function compares the cars in 2 lanes, with lane1 being the
    main one, so it will return the values for the cars in lane1.
    It returns the distances to the next car in each lane for each car in lane1
    in the form of an array of tuples.
    If there are any neighbours it will return (0,0) for this car.
    This can be used for either a lane on top of the central lane or one below.

    """
    # finding neighbour indices
    neighbours = neighbour_finder(locs1, locs2)
    # converting numpy.arrays to lists
    locs1 = locs1.tolist()
    locs2 = locs2.tolist()
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
                if roundabout:
                    # distance to next car in its current lane
                    next_car_d_1 = locs1[0] - car_loc + road_length
                    # case where car is last in other lane too
                    if locs2[test_car_index] == locs2[-1]:
                        # distance to next car in other lane
                        next_car_d_2 = locs2[0] - car_loc + road_length
                    else:
                        next_car_d_2 = locs2[test_car_index + 1] - car_loc
                    distances.append((next_car_d_1, next_car_d_2))
                else:
                    distances.append((0, 0))
            else:
                next_car_d_1 = locs1[index + 1] - car_loc
                if locs2[test_car_index] == locs2[-1]:
                    if roundabout:
                        next_car_d_2 = locs2[0] - car_loc + road_length
                    else:
                        next_car_d_2 = road_length - car_loc
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
                locs2 = np.sort(np.append(locs2, car_loc))
                locs1 = np.delete(locs1, np.where(car_loc == locs1)[0])
                distances = compare_2_lanes(locs1, locs2, roundabout)
        index += 1
    return lane1, lane2, locs1, locs2

def switch_process(road1, road2, locs1, locs2):
    distances_12 = compare_2_lanes(locs1, locs2, roundabout)
    road1, road2, locs1, locs2 = switch(
        road1, road2, locs1, locs2, distances_12, roundabout)
    distances_21 = compare_2_lanes(locs2, locs1, roundabout)
    road2, road1, locs2, locs1 = switch(
        road2, road1, locs2, locs1, distances_21, roundabout)
    return road1, road2, locs1, locs2

def iterating_switching(tot_time, density):
    time = 0
    road1, locs1 = generating_simple_road(density)
    road2, locs2 = generating_simple_road(density)

    while time < tot_time:
        road1, road2, locs1, locs2 = switch_process(
            road1, road2, locs1, locs2)
        road1, locs1 = accel_decel(road1, locs1)
        road2, locs2 = accel_decel(road2, locs2)
        print("\n----------\n")
        road1, locs1 = moving_cars(road1, locs1)
        road2, locs2 = moving_cars(road2, locs2)
        time += 1

def check_roundabout():
    # getting user to decided whether cars are in a roundabout or linear road
    valid = False
    while not valid:
        try:
            choice = int(
                input("Type 1 for roundabout model or 2 for linear road model:"))
            valid = True
        except ValueError:
            print("What you have entered is invalid."
                  "\nYou must input a number (1 or 2).")
    global roundabout
    if choice == 1:
        roundabout = True
    elif choice == 2:
        roundabout = False

def main(time):

    #iterating_switching(seconds, initial_density)
    #locs, time = iterate_road_plot_worldlines(time, initial_density)
    #plot_world_lines(locs, time)

iterate_road_basic(seconds)
