# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 13:33:43 2023

@author: felipe
"""

import numpy as np
import numpy.random as rand
import csv
import matplotlib.pyplot as plt
import time

start = time.time()


max_speed = 5  # m s ^ -1
initial_density = 0.10  # cars per site
round_length = 40 # metres
road_length = 40 # meters
prob_of_deceleration = 0.3
#influx = 0.5 # cars per second
seconds = 50  # seconds
entry_point_1 = 5
entry_point_2 = 15
exit_point_1 = 25
exit_point_2 = 35
sample = rand.uniform(0, 1, size=100)


def translate_road(road, loc_cars):
    final_road = ['.' for i in range(len(road))]
    locs = list(map(int, loc_cars))
    for index in locs:
        final_road[index] = int(road[index])
    print(*final_road, sep='  ')

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

def find_next_car(location, locs):
    dummy = []
    dummy.extend(locs)
    dummy.append(location)
    dummy.sort()
    n = 0
    for val in dummy:
        if val == location:
            index = n
        else:
            n+=1
    return index

def accel_decel_linear(road, loc_cars, road_round, loc_round, entry_point):
    n = 0
    while n < len(loc_cars):
        location = int(loc_cars[n])
        speed = int(road[location])
        if location == loc_cars[-1]:
                next_car_round = find_next_car(entry_point, loc_round)
                car_behind_i = next_car_round - 1
                if car_behind_i == -1:
                    car_behind_loc = loc_round[-1]
                    distance_entry = round_length - car_behind_loc + entry_point
                else:
                    car_behind_loc = loc_round[car_behind_i]
                    distance_entry = entry_point - car_behind_loc
                car_behind_speed = road_round[car_behind_loc]
                if car_behind_speed >= distance_entry:
                    distance = len(road) - location
                else:
                    if next_car_round == len(loc_round):
                        next_loc = loc_round[0]
                        distance = round_length - entry_point + next_loc + len(road) - location
                    else:
                        next_loc = loc_round[next_car_round]
                        distance = next_loc - entry_point + len(road) - location
                if speed < max_speed and speed + 1 < distance:
                    road[location] += 1
                elif speed >= distance:
                    road[location] = distance - 1
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

def accel_decel_round(road, loc_round, locs, exits):
    choices = [0 for i in range(len(loc_round))]
    for car in enumerate(loc_round):
        index = car[0]
        location = int(car[1])
        speed = int(road[location])
        if location == loc_round[-1]:
            if speed < max_speed and (speed + 1) < (loc_round[0] - location + len(road)):
                road[location] += 1
            if speed >= (loc_round[0] - location + len(road)):
                road[location] = (loc_round[0] - location + len(road)) - 1
        else:
            next_veh = int(loc_round[index + 1])
            if speed < max_speed and (speed + 1 < next_veh - location):
                road[location] += 1
            if speed >= next_veh - location:
                road[location] = next_veh - location - 1
        if road[location] != 0:
            rand_num = rand.choice(sample)
            if rand_num < prob_of_deceleration:
                road[location] = road[location] - 1
        for _exit_ in enumerate(exits):
            exit_loc = _exit_[1]
            i = _exit_[0]
            if location < exit_loc and speed >= exit_loc - location:
                choices[index] = rand.randint(0,2)
                if choices[index] == 1:
                    road_locs = locs[i]
                    next_car = road_locs[0]
                    distance = exit_loc - location + next_car
                    if speed >= distance:
                        road[location] = distance - 1
    return road, choices

def accel_decel_exits(road, locs):
    for car in enumerate(locs):
        location = car[1]
        speed = int(road[location])
        if location == locs[-1]:
            if speed < max_speed:
                road[location] += 1
        else:
            next_veh = locs[car[0] + 1]
            if speed < max_speed and (speed + 1 < next_veh - location):
                road[location] += 1
            elif speed >= next_veh - location:
                road[location] = next_veh - location - 1
        if road[location] != 0:
            rand_num = rand.choice(sample)
            if rand_num < prob_of_deceleration:
                road[location] -= 1
    return road

def moving_cars_linear(road, locs, round_road, locs_round, entry_point):
    new_cars = []
    for location in locs:
        speed = int(road[location])
        new_location = location + speed
        if new_location >= len(road):
            new_loc = entry_point + new_location - len(road)
            index = find_next_car(new_loc, locs_round)
            round_road[new_loc] = speed
            locs_round.insert(index, new_loc)
            print("new car")
        else:
            new_cars.append(new_location)
            road[new_location] = speed
        road[location] = 0
    new_cars.sort()
    return road, new_cars, round_road, locs_round

def moving_cars_round(road, locs, exit_roads, exit_locs, exits, choices):
    new_cars = []
    for car in enumerate(locs):
        location = car[1]
        index = car[0]
        speed = int(road[location])
        new_location = location + speed
        if choices[index] == 1:
            for info in enumerate(exits):
                exit_loc = info[1]
                exit_i = info[0]
                if location < exit_loc:
                    new_loc = new_location - exit_loc
                    exit_locs[exit_i].insert(0,new_loc)
                    exit_roads[exit_i][new_loc] = speed
                    print("exit")
        else:
            if new_location >= round_length:
                new_location -= round_length
            new_cars.append(new_location)
            road[new_location] = speed
        road[location] = 0
    new_cars.sort()
    return road, new_cars, exit_roads, exit_locs

def moving_cars_exit(road, locs):
    new_cars = []
    for location in locs:
        speed = int(road[location])
        new_location = location + speed
        if new_location < len(road):
            new_cars.append(new_location)
            road[new_location] = speed
        road[location] = 0
    return road, new_cars

def car_flow(road, locs, length):
    n = len(locs)
    density = n/length
    v_avg = np.sum(road)/n
    return density*v_avg

def iterate_roads(total_time, density):
    time = 0

    road1, locs1 = generating_simple_road(road_length, density)
    road2, locs2 = generating_simple_road(road_length, density)
    roundabout, locs_round = generating_simple_road(round_length, density)
    exit_road1, exit_locs1 = generating_simple_road(road_length, density)
    exit_road2, exit_locs2 = generating_simple_road(road_length, density)

    stop_road = [' ' for i in range(len(roundabout))]
    stop_road[entry_point_1] = 'e'
    stop_road[entry_point_2] = 'e'
    stop_road[exit_point_1] = 'e'
    stop_road[exit_point_2] = 'e'

    flow = 0
    densit = 0
    while time < total_time:
        if len(locs1) == 0 and len(locs2) == 0 and len(locs_round) == 0 and len(exit_locs1) == 0 and len(exit_locs2):
            break
        exit_road1 = accel_decel_exits(exit_road1, exit_locs1)
        exit_road2 = accel_decel_exits(exit_road2, exit_locs2)
        roundabout, choices = accel_decel_round(roundabout, locs_round, [exit_locs1], [exit_point_1])
        road1 = accel_decel_linear(road1, locs1, roundabout, locs_round, entry_point_1)
        road2 = accel_decel_linear(road2, locs2, roundabout, locs_round, entry_point_2)


        translate_road(exit_road1, exit_locs1)
        translate_road(exit_road2, exit_locs2)
        print(*stop_road, sep='  ')
        translate_road(roundabout, locs_round)
        print(*stop_road, sep='  ')
        translate_road(road1, locs1)
        translate_road(road2, locs2)
        print("\n - - - - - - -\n")

        exit_road1, exit_locs1 = moving_cars_exit(exit_road1, exit_locs1)
        exit_road2, exit_locs2 = moving_cars_exit(exit_road2, exit_locs2)
        roundabout, locs_round, exit_roads, exit_locs = moving_cars_round(roundabout, locs_round, [exit_road1, exit_road2], [exit_locs1,exit_locs2], [exit_point_1, exit_point_2], choices)
        exit_road1 = exit_roads[0]
        exit_road2 = exit_roads[1]
        exit_locs1 = exit_locs[0]
        exit_locs2 = exit_locs[1]
        road1, locs1, roundabout, locs_round  = moving_cars_linear(road1, locs1, roundabout, locs_round, entry_point_1)
        road2, locs2, roundabout, locs_round = moving_cars_linear(road2, locs2, roundabout, locs_round, entry_point_2)

        #road1, locs1 = influx_gen(road1, locs1, density)
        #road2, locs2 = influx_gen(road2, locs2, density)
        roads = [road1, road2, exit_road1, exit_road2, roundabout]
        locs = [locs1, locs2, exit_locs1, exit_locs2, locs_round]
        for r in enumerate(roads):
            flow += car_flow(r[1], locs[r[0]], len(r[1]))
            densit += len(locs[r[0]]) / len(r[1])
        time += 1
    return time

def write_flows(time):
    densities = rand.uniform(low=0.01,high=1,size=10)
    times = []
    for rho in densities:
        t = iterate_roads(seconds, rho, 5)
        with open("flow_rate_intersection_7.csv", 'a', encoding='utf-8') as data:
            writer = csv.writer(data)
            writer.writerow(rho, t)

def plot_flows():
    data = np.genfromtxt("flow_rate_intersection_7.csv", dtype='float',
                         delimiter=',', skip_header=1)
    densities = data[:,0]
    times = data[:,1]
    for i in range(5):
        column = data[:,i]
        avg_t = np.average(column)
        avg_times.append(avg_t)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    ax.set_title('Management of traffic at an intersection', fontsize=20)
    ax.set_ylabel('Average time taken to empty roads (seconds)', fontsize=18)
    ax.set_xlabel('Interval of traffic light (seconds)', fontsize=18)
    plt.xticks(np.arange(0, 35, step=5),fontsize=16)
    plt.ylim(0,8000)
    plt.yticks(np.arange(0,9000,step=1000),fontsize=16)
    plt.grid()
    plt.scatter(intervals, avg_times, s=5, c='blue', label='Length = 5000m')
    """
    colours = ['red', 'blue', 'black', 'green', 'orange', 'yellow', 'purple', 'cyan', 'magenta', 'dodgerblue']
    for inter in range(1,11):
        x, y = iterate_roads(seconds, 0.3, inter)
        plt.scatter(x, y, s=1, c=colours[inter-1], alpha=1, label=inter)
    plt.legend(loc='best', title='interval times for traffic lights (sec)', markerscale=4)
    """
    plt.legend(title='Length of roads')
    plt.show()
    plt.savefig("intersection_times2.pdf", dpi=400)



end = time.time()
print((end - start)/60)