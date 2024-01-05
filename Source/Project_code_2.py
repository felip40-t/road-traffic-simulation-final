# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 17:17:59 2023

@authors:  Felipe Tcach and Joshua Fatimilehin-Tulip

Title:
    Road Traffic Simulation

Description:
    Simulation of road traffic.
"""

import numpy as np
import numpy.random as rand
import turtle

v_max = 5  # m s ^ -1
initial_density_of_cars = 0.4  # cars per site
road_length = 30  # metres / number of sites
num_cars = int(np.floor(road_length * initial_density_of_cars))
prob_of_deceleration = 0.3
seconds = 100  # seconds
num_of_lanes = 2


class simple_lane:

    def __init__(self):
        # generating road array
        self.lane = np.zeros(road_length)
        # generating car indices
        self.car_locs = []
        # starting red light
        self.red_light = False

    def choose_roundabout(self):
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
        if choice == 1:
            self.roundabout = True
        elif choice == 2:
            self.roundabout = False

    def generating_lane(self):
        # generating indices and speeds for car
        road_indices = range(road_length)
        n = 0
        while n < num_cars:
            # generating random index for each car.
            car_index = rand.choice(road_indices)
            self.car_locs.append(car_index)
            # deleting this index from the original list of indices so that 2 cars
            # aren't generated in the same place
            road_indices = np.delete(
                road_indices, np.where(car_index == road_indices)[0])
            # choosing traffic light index
            self.red_light_index = rand.choice(road_indices)
            # generating random speed
            car_speed = rand.randint(0, v_max+1)
            # placing car on road
            self.lane[car_index] = car_speed
            n += 1
        # sorting array for car indices
        self.car_locs = np.sort(self.car_locs)

    def get_locs_speed(self):
        return self.lane,self.car_locs

    def translate_road(self):
        self.lane_translated = ['.' for i in range(self.l)]
        self.car_locs = list(map(int, self.car_locs))
        for i in self.car_locs:
            self.lane_translated[i] = self.lane[i]
        if self.red_light:
            self.lane_translated[self.red_light_index] = 'red'
        print(*self.lane_translated,  sep='  ')

    def accel_decel(self):
        n = 0
        # loop for the cars which aren't at the end of the road
        while n < (len(self.car_locs) - 1):
            location = int(self.car_locs[n])
            speed = self.lane[location]
            if speed < v_max and (speed + 1) < (self.car_locs[n+1] - location):
                self.lane[location] += 1
            if speed >= (self.car_locs[n+1] - location):
                self.lane[location] = self.car_locs[n+1] - location - 1
            n += 1
        # case for the last car
        loc_last = int(self.car_locs[-1])
        speed_last = self.lane[loc_last]
        if self.roundabout:
            if speed_last < v_max and (speed_last + 1) < (self.car_locs[0] - loc_last + road_length):
                self.lane[loc_last] += 1
            if speed_last >= (self.car_locs[0] - loc_last + road_length):
                self.lane[loc_last] = (self.car_locs[0] - loc_last + road_length) - 1
        else:
            if speed_last < v_max:
                self.lane[loc_last] += 1

        # generating random numbers
        m = 0
        sample = rand.uniform(0, 1, size=1000)
        while m < len(self.car_locs):
            location = int(self.car_locs[m])
            if self.lane[location] != 0:
                rand_num = rand.choice(sample)
                if rand_num < prob_of_deceleration:
                    self.lane[location] = self.lane[location] - 1
            m += 1

        # traffic light case
        if self.red_light:
            cars_before_index = np.where(self.red_light_index - self.car_locs > 0)[0]
            cars_before = np.sort(self.car_locs[cars_before_index])
            if len(cars_before) != 0:
                car_distance = int(np.min(self.red_light_index - cars_before))
                car_before = int(cars_before[np.where(car_distance == self.red_light_index - cars_before)[0]])
                speed = self.lane[car_before]
                if speed >= car_distance:
                    self.lane[car_before] = car_distance - 1
            else:
                if self.roundabout:
                    car_before = int(self.car_locs[-1])
                    car_distance = self.red_light_index - car_before + road_length
                    speed = self.lane[car_before]
                    if speed >= car_distance:
                        self.lane[car_before] = car_distance - 1
                else:
                    print("There are no cars before the traffic light.")

    def move_cars(self):
        n = 0
        self.new_locs = []
        # moving cars which aren't at the end of the road
        try:
            while n < len(self.car_locs):
                location = int(self.car_locs[n])
                speed = self.lane[location]
                new_location = int(location + speed)
                self.lane[new_location] = speed
                self.lane[location] = 0
                self.new_locs = np.append(self.new_locs,new_location)
                n += 1
        except:
            # case for last car in roundabout
            if self.roundabout:
                # case for last car
                loc_last = int(self.car_locs[-1])
                speed_last = self.lane[loc_last]
                # moving last car if it goes off the end of the road
                # and placing it back at the start of the road
                new_location = int(loc_last + speed_last - road_length)
                self.new_locs = np.append(self.new_locs,new_location)
                self.lane[new_location] = speed_last
                self.lane[loc_last] = 0
            # case for last car in linear
            else:
                # case for last car
                loc_last = int(self.car_locs[-1])
                # removing last car if it goes off the end of the road
                self.lane[loc_last] = 0
        self.car_locs = np.sort(self.new_locs)

    def iterate(self, lane):

        self.lane_obj = lane
        time = 0
        while time < seconds:
            if len(self.car_locs) == 0:
                print("All cars have now left the road.")
                break
            self.lane_obj.accel_decel()
            self.lane_obj.translate_road()
            self.lane_obj.move_cars()
            if time % 5 == 0:
                self.red_light = not self.red_light
            time += 1

def main():

    lane1 = simple_lane()
    lane1.choose_roundabout()
    lane1.generating_lane()
    lane1.iterate(lane1)

main()