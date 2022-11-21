import random
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

        self.reward_store = []
        self.cumulative_wait_store = []
        self.avg_queue_length_store = []
        self.avg_waiting_time_store = []
        self.actions = []

        self.ep = 0

    # Function which is called for each episode starting sumo and then the simulation

    def run(self, episode, epsilon):

        # Starting SUMO
        traci.start(self.sumoCmd)
        print("Simulating...")

        # Inits
        self.step = 0
        self.waiting_times = {}

        self.total_wait_time_TL1 = 0
        self.total_wait_time_TL2 = 0
        self.total_wait_time_TL3 = 0
        self.total_wait_time_TL4 = 0
        self.total_wait_time_TL5 = 0

        self.sum_queue_length = 0
        self.sum_waiting_time = 0
        self.sum_neg_reward = 0
        self.sum_actions = 0

        old_total_wait = 0
        old_state = -1
        old_action = -1

        while self.step < self.max_steps:
            # Get Current State of the environment

            #  Get current total waiting time (sum of the power of each lane's waiting time)
            current_total_wait = self.collect_waiting_times()

            # Executing the selected action

            self.set_green_phase(action)
            green_dur = traci.trafficlight.getPhaseDuration("J7")
            self.simulate(green_dur)

            # Updating the state, action and reward
            old_state = current_state
            old_action = action
            old_total_wait = current_total_wait


        # SAVE EPISODE STATS

        self.reward_store.append(self.sum_neg_reward)  # how much negative reward in this episode
        self.cumulative_wait_store.append(self.sum_waiting_time)  # total number of seconds waited by cars in this episode
        self.avg_queue_length_store.append(self.sum_queue_length / self.max_steps)  # average number of queued cars per step, in this episode
        self.avg_waiting_time_store.append(self.cumulative_wait_store / self.max_steps)
        print("Negative Reward: ", self.sum_neg_reward, "Epsilon: ", epsilon)
        traci.close()

        simulation_time = round(timeit.default_timer() - start_sim_time, 1)

        # print("Training...")
        # start_time = timeit.default_timer()

        # Training -- Experience Replay
        # for _ in range(self.training_epochs):
        # self.replay()
        # training_time = round(timeit.default_timer() - start_time, 1)

        return simulation_time, training_time

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


    # Other possibility for the reward: Function which returns the total waiting time of all the junction

   # def collect_waiting_times(self):

     #   incoming_roads = ["E2TL1", "N2TL23", "W2TL45"]
     #   car_list = traci.vehicle.getIDList()
     #   for car_id in car_list:
      #      wait_time = traci.vehicle.getAccumulatedWaitingTime(car_id)
      #      road_id = traci.vehicle.getRoadID(car_id)  # get the road id where the car is located
      #      if road_id in incoming_roads:  # consider only the waiting times of cars in incoming roads
       #         self.waiting_times[car_id] = wait_time
       #     else:
       #         if car_id in self.waiting_times:  # a car that was tracked has cleared the intersection
       #             del self.waiting_times[car_id]
      #  total_waiting_time = sum(self.waiting_times.values())
      #  return total_waiting_time

    def collect_waiting_times(self):
        wait_N = traci.edge.getWaitingTime("N2TL23")
        wait_E = traci.edge.getWaitingTime("E2TL1")
        wait_W = traci.edge.getWaitingTime("W2TL45")
        total_waiting_time = wait_N + wait_E + wait_W
        # print("total waiting time: ", total_waiting_time)
        return total_waiting_time

    # Counts the number of cars halting, i.e, the cars with speed < 0.1m/s
    def get_queue_length(self):

        halt_N = traci.edge.getLastStepHaltingNumber("N2TL23")
        halt_E = traci.edge.getLastStepHaltingNumber("E2TL1")
        halt_W = traci.edge.getLastStepHaltingNumber("W2TL45")
        queue_length = halt_N + halt_E + halt_W
        return queue_length

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