import timeit
import numpy as np
import traci

# Dictionary of all the actions

PHASE1G2R3R4R5G5 = 0  # TL1 Green, TL2 Red, TL3 Red, TL4 Red, TL5 Green for 40 seconds
PHASE1Y2R3R4R5Y5 = 1
PHASE1R2G3G4R5R5 = 2
PHASE1R2Y3Y4R5R5 = 3
PHASE1R2R3G4G5G5 = 4
PHASE1R2R3Y4Y5Y5 = 5


class Simulation_test:

    def __init__(self, Model, fullTrafficGenerator, sumoCmd, max_steps, num_actions, num_states):

        self.Model = Model

        self.fullTrafficGenerator = fullTrafficGenerator

        self.sumoCmd = sumoCmd

        self.max_steps = max_steps
        self.num_actions = num_actions
        self.num_states = num_states

        self.reward_store = []
        self.queue_length_episode = []
        self.wait_time = []


        self.cumulative_wait_store = []
        self.avg_queue_length_store = []
        self.avg_waiting_time_store = []
        self.actions = []

        self.ep = 0

    # Function which is called for each episode starting sumo and then the simulation

    def run(self, episode):

        start_sim_time = timeit.default_timer()

        self.fullTrafficGenerator.routes(seed=episode)

        # Starting SUMO
        traci.start(self.sumoCmd)
        print("Simulating...")

        # Inits
        self.step = 0
        self.waiting_times = {}

        old_total_wait = 0
        old_action = -1

        while self.step < self.max_steps:
            # Get Current State of the environment
            current_state = self.get_state()

            #  Get current total waiting time (sum of the power of each lane's waiting time)
            current_total_wait = self.collect_waiting_times()

            # print("Current total waiting time: ", current_total_wait)

            # Compute reward
            reward = (old_total_wait - current_total_wait)

            # Select the action to be performed based on epsilon policy
            action = self.choose_action(current_state)

            # Selecting the yellow phase if the new action is different from the old one
            if self.step != 0 and old_action != action:
                self.set_yellow_phase(old_action)
                yellow_dur = traci.trafficlight.getPhaseDuration("J7")
                self.simulate(yellow_dur)
                # self.switch += 1
                # print("Number of switches: ", self.switch)

            # Executing the selected action
            self.set_green_phase(action)
            green_dur = traci.trafficlight.getPhaseDuration("J7")
            self.simulate(green_dur)


            old_action = action
            old_total_wait = current_total_wait

            self.reward_store.append(reward)

        traci.close()

        simulation_time = round(timeit.default_timer() - start_sim_time, 1)

        return simulation_time

    # Function which selects the right yellow phase when the new action is different from the old one
    def set_yellow_phase(self, old_action):
        yellow_phase_code = (old_action * 2) + 1
        traci.trafficlight.setPhase("J7", yellow_phase_code)
        traci.trafficlight.setPhase("J9", yellow_phase_code)
        traci.trafficlight.setPhase("J12", yellow_phase_code)

    # Setting the new phase
    def set_green_phase(self, action_number):
        if action_number == 0:
            traci.trafficlight.setPhase("J7", PHASE1G2R3R4R5G5)
            traci.trafficlight.setPhase("J9", PHASE1G2R3R4R5G5)
            traci.trafficlight.setPhase("J12", PHASE1G2R3R4R5G5)

        elif action_number == 1:
            traci.trafficlight.setPhase("J7", PHASE1R2G3G4R5R5)
            traci.trafficlight.setPhase("J9", PHASE1R2G3G4R5R5)
            traci.trafficlight.setPhase("J12", PHASE1R2G3G4R5R5)

        elif action_number == 2:
            traci.trafficlight.setPhase("J7", PHASE1R2R3G4G5G5)
            traci.trafficlight.setPhase("J9", PHASE1R2R3G4G5G5)
            traci.trafficlight.setPhase("J12", PHASE1R2R3G4G5G5)

    def get_state(self):
        state = np.zeros(self.Model.input_dim)

        state[0] = traci.lane.getLastStepHaltingNumber("E2TL1_0")
        state[1] = traci.lane.getLastStepHaltingNumber("N2TL23_1")
        state[2] = traci.lane.getLastStepHaltingNumber("N2TL23_0")
        state[3] = traci.lane.getLastStepHaltingNumber("W2TL45_1")
        state[4] = traci.lane.getLastStepHaltingNumber("W2TL45_0")

        state[5] = traci.lane.getWaitingTime("E2TL1_0")
        state[6] = traci.lane.getWaitingTime("N2TL23_1")
        state[7] = traci.lane.getWaitingTime("N2TL23_0")
        state[8] = traci.lane.getWaitingTime("W2TL45_1")
        state[9] = traci.lane.getWaitingTime("W2TL45_0")

        #  Medium Arrival rate
        state[10] = self.fullTrafficGenerator.lane_1 / (self.fullTrafficGenerator.total_num_vehic)
        state[11] = self.fullTrafficGenerator.lane_2 / (self.fullTrafficGenerator.total_num_vehic)
        state[12] = self.fullTrafficGenerator.lane_3 / (self.fullTrafficGenerator.total_num_vehic)
        state[13] = self.fullTrafficGenerator.lane_4 / (self.fullTrafficGenerator.total_num_vehic)
        state[14] = self.fullTrafficGenerator.lane_5 / (self.fullTrafficGenerator.total_num_vehic)

        # print("state", state)
        return state

    # Other possibility for the reward: Function which returns the total waiting time of all the junction

    def collect_waiting_times(self):

        incoming_roads = ["E2TL1", "N2TL23", "W2TL45"]
        car_list = traci.vehicle.getIDList()
        for car_id in car_list:
            wait_time = traci.vehicle.getAccumulatedWaitingTime(car_id)
            road_id = traci.vehicle.getRoadID(car_id)  # get the road id where the car is located
            if road_id in incoming_roads:  # consider only the waiting times of cars in incoming roads
                self.waiting_times[car_id] = wait_time
            else:
                if car_id in self.waiting_times:  # a car that was tracked has cleared the intersection
                    del self.waiting_times[car_id]
        total_waiting_time = sum(self.waiting_times.values())
        return total_waiting_time

    # Counts the number of cars halting, i.e, the cars with speed < 0.1m/s
    def get_queue_length(self):

        halt_N = traci.edge.getLastStepHaltingNumber("N2TL23")
        halt_E = traci.edge.getLastStepHaltingNumber("E2TL1")
        halt_W = traci.edge.getLastStepHaltingNumber("W2TL45")
        queue_length = halt_N + halt_E + halt_W
        return queue_length

    # Choose which action to perform (explorative or exploative) based on epsilon greedy policy
    def choose_action(self, state):

            return np.argmax(self.Model.predict_one(state))  # the best action given the current state

    #  Function which makes a single step in SUMO, the variable steps_todo is important to tell SUMO how much the actual TL phase lasts
    def simulate(self, steps_todo):
        if (self.step + steps_todo) >= self.max_steps:
            steps_todo = self.max_steps - self.step

        while steps_todo > 0:
            traci.simulationStep()
            self.step += 1
            steps_todo -= 1

            queue_length = self.get_queue_length()
            self.queue_length_episode.append(queue_length)
            waiting_time = self.collect_waiting_times()
            self.cumulative_wait_store.append(waiting_time)



