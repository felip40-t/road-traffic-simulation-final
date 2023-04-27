# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 20:34:15 2023

@author: felipe
"""

import numpy as np
import numpy.random as rand
import csv
import matplotlib.pyplot as plt
import time

start = time.time()


max_speed = 5  # metres per second
#bus_density = 0.15 # busses per metre
road_length = 50  # metres
prob_of_deceleration = 0.3
seconds = 50 # seconds
influx = True
#influx_bus = 0.5 # busses per second
max_cap_bus = 10
influx_passengers = 0.1 # per second
stop_frequency = 0.05 # stops per metre

def translate_road(road, locs, stops, stop_caps):
    final_road = ['.' for i in range(len(road))]
    stop_road = [' ' for i in range(len(road))]
    caps_road = [' ' for i in range(len(road))]
    for j in locs:
        final_road[j[0]], final_road[j[1]] = int(road[j[0]]), int(road[j[1]])
    for i in enumerate(stops):
        stop_road[i[1]] = i[0] + 1
        caps_road[i[1] - i[0]] = '({})'.format(stop_caps[i[0]])
    print(*stop_road, sep='  ')
    print(*caps_road, sep='  ')
    print(*final_road, sep='  ')

def tuple_to_list(locs):
    locs_list = []
    for i in locs:
        locs_list.append(i[0])
        locs_list.append(i[1])
    return locs_list

def influx_gen(road, locs_bus, bus_caps, stop_caps, stops, passengers, influx_bus):
    vehicle_locs = tuple_to_list(locs_bus)
    sample = rand.uniform(0,1, size=100)
    val = rand.choice(sample)
    if (val < influx_bus) and (vehicle_locs[0] != 0) and (vehicle_locs[0] != 1):
        speed = rand.randint(0,max_speed+1)
        road[0], road[1] = [speed, speed]
        locs_bus.insert(0, (0,1))
        bus_caps.insert(0,rand.randint(0,max_cap_bus))
        pass_tup = calc_pass_single(speed, 0, 0, 0, bus_caps, stop_caps, stops)
        passengers.insert(0,pass_tup)
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
    n_stops = int(np.floor(road_length*stop_frequency))
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
    dummy = []
    dummy.extend(stops)
    dummy.append(location)
    dummy.sort()
    n = 0
    for val in dummy:
        if val == location:
            index = n
        else:
            n+=1
    return index

def calc_pass_single(speed, location, stop_index, bus_index, bus_caps, stop_caps, stops):
    if stop_index < len(stops):
        cap_stop = stop_caps[stop_index]
        cap_bus = bus_caps[bus_index]
        pass_off = rand.randint(0, cap_bus+1)
        pass_on = rand.randint(0, cap_stop+1)
        bus_space = max_cap_bus - (cap_bus - pass_off)
        if pass_on > bus_space:
            if bus_space > cap_stop:
                pass_on = cap_stop
            else:
                pass_on = bus_space
    else:
        pass_off, pass_on = (0,0)
    return (pass_off, pass_on)

def new_pass_calc(road, locs, bus_caps, stops, stop_caps, passengers):
    for bus in enumerate(locs):
        location = bus[1][1]
        speed = road[location]
        stop_index = find_next_stop(location, stops)
        bus_index = bus[0]
        if location < stops[-1]:
            passengers[bus_index] = calc_pass_single(speed, location, stop_index, bus_index, bus_caps, stop_caps, stops)
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

def passed_stop(road, bus, stops):
    location = bus[1]
    speed = int(road[location])
    index = find_next_stop(location, stops)
    last_stop = stops[index - 1]
    if speed >= location - last_stop:
        choice = True
    else:
        choice = False
    return choice

def new_process(road, locs, stops, bus_caps, stop_caps, passengers):
    for bus in enumerate(locs):
        location = bus[1][1]
        speed = road[location]
        bus_index = bus[0]
        stop_index = find_next_stop(location, stops)
        if passengers[bus_index] == (0,0):
            road = accel_decel(road, locs, bus[1])
            road = random_decel(road, bus[1])
        elif (location + 1) in stops and speed == 0:
              pass_off = passengers[bus[0]][0]
              pass_on = passengers[bus[0]][1]
              if pass_off > 0:
                  pass_off -= 1
                  bus_caps[bus[0]] -= 1
              elif pass_off == 0 and pass_on > 0:
                  pass_on -= 1
                  bus_caps[bus[0]] += 1
                  stop_caps[stop_index] -= 1
              passengers[bus[0]] = (pass_off, pass_on)
        else:
            road = accel_decel(road, locs, bus[1])
            road = random_decel(road, bus[1])
            road = decel_stops(road, bus[1], stops)
    return road, bus_caps, stop_caps, passengers

def adjust_buses(locs, stops, bus_caps, stop_caps, passengers):
    for bus in enumerate(locs):
        location = bus[1][1]
        bus_index = bus[0]
        stop_index = find_next_stop(location, stops)
        pass_off = passengers[bus_index][0]
        pass_on = passengers[bus_index][1]
        if stop_index < len(stops) and pass_on > stop_caps[stop_index]:
            passengers[bus_index] = (pass_off, stop_caps[stop_index])
    return passengers

def process_pass_stop(road, locs, stops, bus_caps, stop_caps, passengers):
    for bus in enumerate(locs):
        location = bus[1][1]
        speed = road[location]
        bus_index = bus[0]
        stop_index = find_next_stop(location, stops)
        if stop_index != 0 and stop_index != len(stops):
            if passed_stop(road, bus[1], stops):
                passengers[bus_index] = calc_pass_single(speed, location, stop_index, bus_index, bus_caps, stop_caps, stops)
    return passengers

def bus_flow(road, locs):
    n_bus = len(locs)
    density = n_bus/road_length
    v_avg = np.sum(road)/n_bus
    return density*v_avg

def iterate_road(tot_time, rho_bus):
    t = 0
    flow = 0
    road, locs, bus_caps, stops, stop_caps = generating_simple_road(rho_bus)
    passengers = [(0,0) for i in range(len(locs))]
    passengers = new_pass_calc(road, locs, bus_caps, stops, stop_caps, passengers)
    while t < tot_time:
        road, bus_caps, stop_caps, passengers = new_process(road, locs, stops, bus_caps, stop_caps, passengers)
        passengers = adjust_buses(locs, stops, bus_caps, stop_caps, passengers)
        for b_cap in enumerate(bus_caps):
            index = b_cap[0]
            cap = b_cap[1]
            print("bus {0} occupancy = {1}".format(index+1, cap))
        translate_road(road, locs, stops, stop_caps)
        print("\n")
        road, locs, bus_caps, passengers = moving_bus(road, locs, bus_caps, passengers)
        passengers = process_pass_stop(road, locs, stops, bus_caps, stop_caps, passengers)
        if influx:
            road, locs, bus_caps, passengers = influx_gen(road, locs, bus_caps, stop_caps, stops, passengers, rho_bus)
            stop_caps = generate_passengers(stop_caps)
        flow += bus_flow(road, locs)
        t += 1
    return flow/t

def write_flows(time):
    densities = rand.uniform(low=0.01, high=0.5, size=10)
    flow_rates = []
    for rho in densities:
        flow_rate = iterate_road(time, rho)
        flow_rates.append(flow_rate)
        with open("flow_rate_buses_1.csv", 'a', encoding='utf-8') as data:
            writer = csv.writer(data)
            writer.writerow([rho, flow_rate])

def plot_flows():
    data = np.genfromtxt("flow_rate_buses_1.csv", dtype='float',
                         delimiter=',', skip_header=1)
    densities = data[:, 0]
    flow_rates = data[:, 1]
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    ax.set_title('Traffic Flow for buses with stops', fontsize=22)
    ax.set_xlabel('Average density (buses per site)', fontsize=18)
    ax.set_ylabel('Average Flow rate (buses per time step)', fontsize=18)
    plt.xticks(np.arange(0, 0.6, step=0.1),fontsize=16)
    plt.ylim(0,0.4)
    plt.yticks(np.arange(0,0.4,step=0.05),fontsize=16)
    plt.grid()
    plt.scatter(densities, flow_rates, s=3, c='black', alpha=1)
    plt.show()
    plt.savefig("Flow_graph_buses_1.pdf", dpi=400)

#write_flows(seconds)
#plot_flows()

iterate_road(seconds, 0.1)

end = time.time()
print((end - start)/60)
