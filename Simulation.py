import random
import timeit
import numpy as np
import traci

# Dictionary of all the actions

PHASE1G2R3R4R5G5 = 0  # TL1 Green, TL2 Red, TL3 Red, TL4 Red, TL5 Green for 5 seconds
PHASE1Y2R3R4R5Y5 = 1
PHASE1R2G3G4R5R5 = 2
PHASE1R2Y3Y4R5R5 = 3
PHASE1R2R3G4G5G5 = 4
PHASE1R2R3Y4Y5Y5 = 5


class Simulation:

    def __init__(self, Model, Memory, fullTrafficGenerator, sumoCmd, max_steps, num_actions, num_states,
                 training_epochs, gamma, total_episodes):

        self.Model = Model
        self.Memory = Memory

        self.fullTrafficGenerator = fullTrafficGenerator

        self.sumoCmd = sumoCmd

        self.max_steps = max_steps
        self.num_actions = num_actions
        self.num_states = num_states
        self.training_epochs = training_epochs
        self.gamma = gamma

        self.total_episodes = total_episodes

        # PLOTS

        self.reward_store = []  # Cumulative Reward
        self.avg_queue_length_store = []  # Average queue length
        self.cumulative_wait_store = []  # Cumulative wait store
        self.avg_waiting_time_store = []  # Average waited time for each car

        self.cumulative_CO2Emission_store = []
        self.cumulative_fuelCons_store = []

    # Function which is called for each episode starting sumo and then the simulation

    def run(self, episode, epsilon):

        start_sim_time = timeit.default_timer()  # Starting timer

        self.fullTrafficGenerator.routes(seed=episode)  # Generating the route file, choosing seed=episode in order to provide a different scenario every time

        # Starting SUMO
        traci.start(self.sumoCmd)  # Simulation starts
        print("Simulating...")

        # Inits
        self.step = 0
        self.waiting_times = {}


        self.sum_queue_length = 0
        self.sum_waiting_time = 0
        self.sum_neg_reward = 0
        self.sum_actions = 0

        self.sum_CO2Emissions = 0
        self.sum_fuelConsum = 0
        old_total_wait = 0
        old_state = -1
        old_action = -1


        while self.step < self.max_steps:
            # Get Current State of the environment
            current_state = self.get_state()

            #  Get current total waiting time
            current_total_wait = self.collect_waiting_times()

            # Compute reward
            reward = (old_total_wait - current_total_wait)

            # Saving this data into the Memory
            if self.step != 0:
                self.Memory.add_sample((old_state, old_action, reward, current_state))

            # Select the action to be performed based on epsilon policy
            action = self.choose_action(current_state, epsilon)

            # Selecting the yellow phase if the new action is different from the old one
            if self.step != 0 and old_action != action:
                self.set_yellow_phase(old_action)
                yellow_dur = traci.trafficlight.getPhaseDuration("J7")
                self.simulate(yellow_dur)

            # Executing the selected action
            self.set_green_phase(action)
            green_dur = traci.trafficlight.getPhaseDuration("J7")
            self.simulate(green_dur)

            # print("Training...")
            start_train_time = timeit.default_timer()
            self.replay()
            training_time = round(timeit.default_timer() - start_train_time, 1)

            # Updating the state, action and reward
            old_state = current_state
            old_action = action
            old_total_wait = current_total_wait

            if reward < 0:
                self.sum_neg_reward += reward

        # SAVE EPISODE STATS

        self.reward_store.append(self.sum_neg_reward)  # how much negative reward in this episode
        self.cumulative_wait_store.append(self.sum_waiting_time)  # total number of seconds waited by cars in this episode
        self.avg_queue_length_store.append(self.sum_queue_length / self.max_steps)  # average number of queued cars per step, in this episode
        self.avg_waiting_time_store.append(self.sum_waiting_time / self.fullTrafficGenerator.total_num_vehic) # Average waited time for each vehicle

        self.cumulative_CO2Emission_store.append(self.sum_CO2Emissions)
        self.cumulative_fuelCons_store.append(self.sum_fuelConsum)


        print("Negative Reward: ", self.sum_neg_reward, "Epsilon: ", epsilon)
        traci.close()  # Simulation ends

        simulation_time = round(timeit.default_timer() - start_sim_time, 1)

        return simulation_time, training_time

    # Function which selects the right yellow phase when the new action is different from the old one
    def set_yellow_phase(self, old_action):
        yellow_phase_code = (old_action * 2) + 1
        traci.trafficlight.setPhase("J7", yellow_phase_code)
        traci.trafficlight.setPhase("J9", yellow_phase_code)
        traci.trafficlight.setPhase("J12", yellow_phase_code)

    # Setting the new phase chosen based on the epsilon greedy policy
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

        #  Halting vehicles at each TL
        state[0] = traci.lane.getLastStepHaltingNumber("E2TL1_0")
        state[1] = traci.lane.getLastStepHaltingNumber("N2TL23_1")
        state[2] = traci.lane.getLastStepHaltingNumber("N2TL23_0")
        state[3] = traci.lane.getLastStepHaltingNumber("W2TL45_1")
        state[4] = traci.lane.getLastStepHaltingNumber("W2TL45_0")

        #  Waiting time at each TL
        state[5] = traci.lane.getWaitingTime("E2TL1_0")
        state[6] = traci.lane.getWaitingTime("N2TL23_1")
        state[7] = traci.lane.getWaitingTime("N2TL23_0")
        state[8] = traci.lane.getWaitingTime("W2TL45_1")
        state[9] = traci.lane.getWaitingTime("W2TL45_0")

        #  Medium Arrival rate
        state[10] = self.fullTrafficGenerator.lane_1/(self.fullTrafficGenerator.total_num_vehic)
        state[11] = self.fullTrafficGenerator.lane_2/(self.fullTrafficGenerator.total_num_vehic)
        state[12] = self.fullTrafficGenerator.lane_3/(self.fullTrafficGenerator.total_num_vehic)
        state[13] = self.fullTrafficGenerator.lane_4/(self.fullTrafficGenerator.total_num_vehic)
        state[14] = self.fullTrafficGenerator.lane_5/(self.fullTrafficGenerator.total_num_vehic)
        #print("state", state)
        return state

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

    def get_CO2Emissions(self):
        Emission_N = traci.edge.getCO2Emission("N2TL23")
        Emission_E = traci.edge.getCO2Emission("E2TL1")
        Emission_W = traci.edge.getCO2Emission("W2TL45")
        CO2Emission = Emission_N + Emission_E + Emission_W
        return CO2Emission

    def get_fuelCons(self):
        fuelCons_N = traci.edge.getFuelConsumption("N2TL23")
        fuelCons_E = traci.edge.getFuelConsumption("E2TL1")
        fuelCons_W = traci.edge.getFuelConsumption("W2TL45")
        fuelConsum = fuelCons_N + fuelCons_E + fuelCons_W
        return fuelConsum

    # Choose which action to perform (explorative or exploative) based on epsilon greedy policy
    def choose_action(self, state, epsilon):

        if random.random() < epsilon:
            return random.randint(0, self.num_actions - 1)  # random action
        else:
            return np.argmax(self.Model.predict_one(state))  # the best action given the current state

    #  Function which makes a single step in SUMO, the variable steps_todo is important to tell SUMO how much the actual TL phase lasts
    def simulate(self, steps_todo):
        if (self.step + steps_todo) >= self.max_steps:
            steps_todo = self.max_steps - self.step

        while steps_todo > 0:
            traci.simulationStep()
            self.step += 1
            steps_todo -= 1

            self.sum_queue_length += self.get_queue_length()
            self.sum_waiting_time += self.collect_waiting_times()

            self.sum_CO2Emissions += self.get_CO2Emissions()
            self.sum_fuelConsum += self.get_fuelCons()



    # Experience Replay: Function that extracts a group of samples from the memory and for each of these updates the lerning equation and trains

    def replay(self):

        batch = self.Memory.get_samples(self.Model.batch_size)

        if len(batch) > 0:  # If the memory is sufficiently full
            states = np.array([val[0] for val in batch])  # Extracts states from the batch
            next_states = np.array([val[3] for val in batch])  # Extract the next states from the batch

            # PREDICTION

            q_s_a = self.Model.predict_batch(states)  # Computation of the Q-values Q(st,at)
            q_s_a_d = self.Model.predict_batch(next_states)  # Computation of the Q-values Q(st+1, at+1), represents next state

            # TRAINING ARRAYS
            x = np.zeros((len(batch), self.num_states))
            y = np.zeros((len(batch), self.num_actions))

            for i, b in enumerate(batch):
                state, action, reward, _ = b[0], b[1], b[2], b[3]

                current_q = q_s_a[i]
                current_q[action] = reward + self.gamma * np.amax(q_s_a_d[i])  # UPDATE Q(STATE, ACTION)

                x[i] = state
                y[i] = current_q

            self.Model.train_batch(x, y)  # TRAINS THE NEURAL NETWORK
