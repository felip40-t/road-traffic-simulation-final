# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 20:34:15 2023

@author: felip
"""

import numpy as np
import numpy.random as rand
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import time
import csv

start = time.time()

max_speed = 5  # m s ^ -1
#car_density = 0.3  # cars per site
#bus_density = 0.1 # busses per site
road_length = 1000  # metres / number of sites
prob_of_deceleration = 0.3
seconds = 5000  # seconds
influx = True
#influx_car = 0.3 # cars per second
#influx_bus = 0.5 # busses per second

def translate_road(road, locs):
    final_road = ['.' for i in range(len(road))]
    for j in locs:
        final_road[j] = int(road[j])
    print(*final_road, sep='  ')

def influx_gen(road, vehicle_locs, locs_car, locs_bus, influx_car, influx_bus):
    sample = rand.uniform(0,1, size=100)
    val1 = rand.choice(sample)
    val2 = rand.choice(sample)
    if rand.choice([val1,val2]) == val1:
        if (val1 < influx_car) and (vehicle_locs[0] != 0):
            speed = rand.randint(0,max_speed+1)
            road[0] = speed
            locs_car.insert(0, 0)
    else:
        if (val2 < influx_bus) and (vehicle_locs[0] != 0) and (vehicle_locs[0] != 1):
            speed = rand.randint(0,max_speed+1)
            road[0], road[1] = [speed, speed]
            locs_bus.insert(0, (0,1))
    return road, locs_car, locs_bus, vehicle_locs

def tuple_to_list(locs):
    locs_list = []
    for i in locs:
        locs_list.append(i[0])
        locs_list.append(i[1])
    return locs_list

def vehicle_loc_gen(cars, bus):
    vehicle_locs = []
    vehicle_locs.extend(cars)
    vehicle_locs.extend(tuple_to_list(bus))
    vehicle_locs.sort()
    return vehicle_locs

def generating_simple_road(rho_car, rho_bus):
    num_cars = int(np.floor(road_length * rho_car))
    num_bus = int(np.floor(road_length * rho_bus))
    # generating road array
    road = np.zeros(road_length)
    road_indices = []
    for i in range(road_length):
        road_indices.append(i)
    bus_indices = [] # list of tuples
    m = 0
    while m < num_bus:
        bus_index = rand.choice(road_indices[:-1])
        if (bus_index + 1) in road_indices:
            bus_indices.append((bus_index, bus_index + 1))
            bus_speed = rand.randint(0,max_speed+1)
            road_indices.remove(bus_index)
            road_indices.remove(bus_index + 1)
            road[bus_index], road[bus_index + 1] = [bus_speed, bus_speed]
            m += 1
        elif (bus_index - 1) in road_indices:
            bus_indices.append((bus_index - 1, bus_index))
            bus_speed = rand.randint(0,max_speed+1)
            road_indices.remove(bus_index)
            road_indices.remove(bus_index - 1)
            road[bus_index], road[bus_index - 1] = [bus_speed, bus_speed]
            m += 1
    # generating indices and speeds for cars
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
    bus_indices.sort()
    return road, car_indices, bus_indices

def accel_decel(road, loc_cars, loc_bus):
    vehicle_locs = vehicle_loc_gen(loc_cars, loc_bus)
    sample = rand.uniform(0, 1, size=100)
    for car in loc_cars:
        location = int(car)
        speed = road[location]
        if location == vehicle_locs[-1]:
            if speed < max_speed:
                road[location] += 1
        else:
            n = 0
            for val in vehicle_locs:
                if val == location:
                    veh_ind = n
                else:
                    n += 1
            next_veh_loc = vehicle_locs[veh_ind + 1]
            next_veh = next_veh_loc - location
            if speed >= (next_veh):
                road[location] = next_veh - 1
            elif speed < max_speed and (speed + 1) < next_veh:
                road[location] += 1

        if road[location] != 0:
            rand_num = rand.choice(sample)
            if rand_num < prob_of_deceleration:
                road[location] -= 1

    for bus in loc_bus:
        location1 = int(bus[1]) # front of bus
        location2 = int(bus[0])
        speed = road[location1]
        if location1 == vehicle_locs[-1]:
            if speed < max_speed:
                road[location1] += 1
                road[location2] += 1
        else:
            n = 0
            for val in vehicle_locs:
                if val == location1:
                    veh_ind = n
                else:
                    n += 1
            next_veh_loc = vehicle_locs[veh_ind + 1]
            next_veh = next_veh_loc - location1
            if speed >= (next_veh):
                road[location1] = next_veh - 1
                road[location2] = next_veh - 1
            elif speed < max_speed and (speed + 1) < next_veh:
                road[location1] += 1
                road[location2] += 1
        if road[location1] != 0:
            rand_num = rand.choice(sample)
            if rand_num < prob_of_deceleration:
                road[location1] -= 1
                road[location2] -= 1

    #translate_road(road, vehicle_locs)
    return road, vehicle_loc_gen(loc_cars, loc_bus)

def moving_cars(road, loc_cars, loc_bus):
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
    # moving busses
    new_bus = []
    for bus in loc_bus:
        location1 = int(bus[1]) # front of bus
        location2 = int(bus[0])
        speed = road[location1]
        new_location1 = int(location1 + speed)
        new_location2 = int(new_location1 - 1)
        if new_location1 < len(road):
            new_bus.append((new_location2, new_location1))
            road[location1], road[location2] = [0,0]
            road[new_location1], road[new_location2] = [speed, speed]
        else:
            road[location1], road[location2] = [0,0]
    return road, new_cars, new_bus, vehicle_loc_gen(new_cars, new_bus)

def car_flow(road, car_locs):
    n_cars = len(car_locs)
    density = n_cars/road_length
    v_avg = np.sum(road)/n_cars
    return density*v_avg

def iterate_road(tot_time, rho_car, rho_bus):
    t = 0
    flow = 0
    road, car_indices, bus_indices  = generating_simple_road(rho_car, rho_bus)
    # repeating whole process for certain amount of iterations
    while t < tot_time:
        if len(car_indices) == 0 and len(bus_indices) == 0:
            print("All vehicles have now left the road.")
            break
        road, vehicle_locs = accel_decel(road, car_indices, bus_indices)
        road, car_indices, bus_indices, vehicle_locs = moving_cars(road, car_indices, bus_indices)
        flow += car_flow(road, vehicle_locs)
        if influx:
            road, car_indices, bus_indices, vehicle_locs = influx_gen(road, vehicle_locs, car_indices, bus_indices, rho_car, rho_bus)
        t += 1
    return flow / t

def write_flows(time):
    density_car = rand.uniform(0,1,50)
    density_bus = rand.uniform(0, (1 - density_car)/2 , 50)
    densities = []
    for i in range(10):
        densities.append((density_car[i], density_bus[i]))
    for value in densities:
        if value == (0,0):
            densities.remove(value)
    flow_rates = []
    for rho in densities:
        flow_rate = iterate_road(time, rho[0], rho[1])
        flow_rates.append(flow_rate)
    with open("flow_rate_data_bus3.csv", 'a', encoding='utf-8') as data:
        writer = csv.writer(data)
        for index in enumerate(densities):
            writer.writerow([index[1][0],index[1][1], flow_rates[index[0]]])


def plot_flows():
    data = np.genfromtxt("flow_rate_data_bus3.csv", dtype='float',
                         delimiter=',', skip_header=1)
    density_car = data[:, 0]
    density_bus = data[:,1]
    flow_rates = data[:, 2]
    fig = plt.figure(figsize=(14, 10))
    ax = plt.axes(projection='3d')
    ax.set_title('Traffic Flow plot', fontsize=20)
    ax.set_xlabel('Initial density of cars', fontsize=16)
    ax.set_ylabel('Initial density of busses', fontsize=16)
    ax.set_zlabel('Flow of traffic', fontsize=16)
    ax.invert_xaxis()
    ax.scatter3D(density_car, density_bus, flow_rates, color='black', s=3)
    plt.show()
    plt.savefig("Flow_graph_busses3.pdf", dpi=400)

write_flows(seconds)
plot_flows()
#iterate_road(seconds, 0.1, 0.05)
end = time.time()
print((end - start)/60)
