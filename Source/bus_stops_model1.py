# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 12:48:51 2023

@author: felipe
"""

import numpy as np
import numpy.random as rand

max_speed = 5  # m s ^ -1
bus_density = 0.1 # busses per site
road_length = 50  # metres / number of sites
prob_of_deceleration = 0.3
seconds = 15  # seconds
influx = True
influx_bus = 0.5 # busses per second
max_cap_bus = 15
influx_passengers = 0.3

def translate_road(road, locs, stops):
    final_road = ['.' for i in range(len(road))]
    stop_road = [' ' for i in range(len(road))]
    for j in locs:
        final_road[j[0]], final_road[j[1]] = int(road[j[0]]), int(road[j[1]])
    for i in enumerate(stops):
        stop_road[i[1]] = i[0] + 1
    print(*stop_road, sep='  ')
    print(*final_road, sep='  ')

def tuple_to_list(locs):
    locs_list = []
    for i in locs:
        locs_list.append(i[0])
        locs_list.append(i[1])
    return locs_list

def influx_gen(road, locs_bus, bus_caps, passengers):
    vehicle_locs = tuple_to_list(locs_bus)
    sample = rand.uniform(0,1, size=100)
    val = rand.choice(sample)
    if (val < influx_bus) and (vehicle_locs[0] != 0) and (vehicle_locs[0] != 1):
        speed = rand.randint(0,max_speed+1)
        road[0], road[1] = [speed, speed]
        locs_bus.insert(0, (0,1))
        bus_caps.insert(0,rand.randint(0,10))
        passengers.insert(0,(0,0))
    return road, locs_bus, bus_caps, passengers

def generating_simple_road(rho_bus):
    num_bus = int(np.floor(road_length * rho_bus))
    road = np.zeros(road_length)
    road_indices = []
    for i in range(road_length):
        road_indices.append(i)
    bus_indices = [] # list of tuples
    stops = []
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
    bus_indices.sort()
    first_stop = rand.choice(range(2,int(np.floor(road_length*0.1))))
    n_stops = int(np.floor(road_length*0.05))
    stop_density = n_stops / road_length
    for k in range(n_stops):
        stops.append(first_stop + int(np.floor(k / stop_density)))
    stop_capacities = []
    for i in range(len(stops)):
        stop_capacities.append(rand.randint(0,max_cap_bus))
    bus_capacities = []
    for j in range(num_bus):
        bus_capacities.append(rand.randint(0, max_cap_bus))
    return road, bus_indices, bus_capacities, stops, stop_capacities

def accel_decel(road, locs, bus):
    vehicle_locs = tuple_to_list(locs)
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
        if speed < max_speed and (speed + 1) < (next_veh):
            road[location1] += 1
            road[location2] += 1
        if speed >= (next_veh):
            road[location1] = next_veh - 1
            road[location2] = next_veh - 1
    return road

def random_decel(road,bus):
    sample = rand.uniform(0, 1, size=100)
    location1 = bus[1]
    location2 = bus[0]
    if road[location1] != 0:
        rand_num = rand.choice(sample)
        if rand_num < prob_of_deceleration:
            road[location1] -= 1
            road[location2] -= 1
    return road

def decel_stops(road, bus, stops):
    location1 = int(bus[1]) # front of bus
    location2 = int(bus[0])
    speed = road[location1]
    dummy_veh = []
    dummy_veh.extend(stops)
    dummy_veh.append(location1)
    dummy_veh.sort()
    n = 0
    for val in dummy_veh:
        if val == location1:
            veh_ind = n
        else:
            n += 1
    if location1 != dummy_veh[-1]:
        next_stop = dummy_veh[veh_ind + 1]
        distance = next_stop - location1
        if speed >= distance and distance > 0:
            road[location1] = distance - 1
            road[location2] = distance - 1
    return road

def find_next_stop(location, stops):
    dummy_stop = []
    dummy_stop.extend(stops)
    dummy_stop.append(location)
    dummy_stop.sort()
    n = 0
    for val in dummy_stop:
        if val == location:
            index = n
        else:
            n+=1
    return index

def pass_calc(road, locs, bus_caps, stops, stop_caps, passengers):
    m = 0
    for bus in enumerate(locs):
        location = bus[1][1]
        speed = road[location]
        if (location + 1) in stops and speed == 0 and passengers[bus[0]] == (0,0):
            index = find_next_stop(location, stops)
            cap_stop = stop_caps[index]
            bus_cap = bus_caps[m]
            pass_off = rand.randint(0, bus_cap+1)
            pass_on = rand.randint(0, cap_stop+1)
            bus_space = bus_cap - pass_off
            if pass_on > bus_space:
                pass_on = bus_space
            passengers[bus[0]] = (pass_off, pass_on)
            if pass_on == 0 and pass_off == 0:
                passengers[bus[0]] = (-1,-1)
        m += 1
    return passengers

def generate_passengers(stop_caps):
    sample = rand.uniform(0,1, size=100)
    for stop in enumerate(stop_caps):
        val = rand.choice(sample)
        if val < influx_passengers:
            stop_caps[stop[0]] += 1
    return stop_caps

def moving_bus(road, loc_bus, bus_caps, passengers):
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
            bus_caps = bus_caps[:-1]
            passengers = passengers[:-1]
    return road, new_bus, bus_caps, passengers

def process(road, locs, stops, bus_caps, stop_caps, passengers):
    for bus in enumerate(locs):
        index = find_next_stop(bus[1][1], stops)
        if passengers[bus[0]] == (0,0):
            road = accel_decel(road, locs, bus[1])
            road = random_decel(road, bus[1])
            road = decel_stops(road, bus[1], stops)
        elif passengers[bus[0]] == (0,1) or passengers[bus[0]] == (1,0):
            road = accel_decel(road, locs, bus[1])
            dummy_stops = []
            dummy_stops.extend(stops)
            index = find_next_stop(bus[1][1], stops)
            if index < len(stops):
                dummy_stops.remove(stops[index])
            else:
                dummy_stops.remove(stops[-1])
            road = decel_stops(road, bus[1], dummy_stops)
            if passengers[bus[0]] == (0,1):
                stop_caps[index] -= 1
                bus_caps[bus[0]] += 1
            if passengers[bus[0]] == (1,0):
                bus_caps[bus[0]] -= 1
            passengers[bus[0]] = (0,0)
        elif passengers[bus[0]] == (-1,-1):
            road = accel_decel(road, locs, bus[1])
            road = random_decel(road, bus[1])
            dummy_stops = []
            dummy_stops.extend(stops)
            index = find_next_stop(bus[1][1], stops)
            if index < len(stops):
                dummy_stops.remove(stops[index])
            else:
                dummy_stops.remove(stops[-1])
            road = decel_stops(road, bus[1], dummy_stops)
        else:
            pass_off = passengers[bus[0]][0]
            pass_on = passengers[bus[0]][1]
            if pass_off > 0:
                pass_off -= 1
                bus_caps[bus[0]] -= 1
            elif pass_off == 0 and pass_on > 0:
                pass_on -= 1
                bus_caps[bus[0]] += 1
                stop_caps[index] -= 1
            passengers[bus[0]] = (pass_off, pass_on)
    return road, bus_caps, stop_caps, passengers

def iterate_road(tot_time, rho_bus):
    t = 0
    road, locs, bus_caps, stops, stop_caps = generating_simple_road(rho_bus)
    passengers = [(0,0) for i in range(len(locs)) ]
    while t < tot_time:
        passengers = pass_calc(road, locs, bus_caps, stops, stop_caps, passengers)
        road, bus_caps, stop_caps, passengers = process(road, locs, stops, bus_caps, stop_caps, passengers)
        print(bus_caps)
        print(stop_caps)
        translate_road(road, locs, stops)
        print("\n")
        road, locs, bus_caps, passengers = moving_bus(road, locs, bus_caps, passengers)
        if influx:
            road, locs, bus_caps, passengers = influx_gen(road, locs, bus_caps, passengers)
            stop_caps = generate_passengers(stop_caps)
        t += 1
iterate_road(seconds, bus_density)