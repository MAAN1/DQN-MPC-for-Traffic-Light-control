from __future__ import absolute_import
from __future__ import print_function
from Model import Model
from Memory import Memory
from Simulation import Simulation
from Sumo import set_sumo
from visual import Visualization
from utils import set_train_path
from fullgeneration import fullTrafficGenerator

if __name__ == "__main__":

    sumoCmd = set_sumo(True)

    path = set_train_path(models_path_name='models')

    Model = Model(num_layers=5, width=800, batch_size=32, learning_rate=0.00025, input_dim=15, output_dim=3)

    Memory = Memory(size_min=400, size_max=5000000)

    fullTrafficGenerator = fullTrafficGenerator()

    Visualization = Visualization(
        path,
        dpi=96
    )

    Simulation = Simulation(Model, Memory, fullTrafficGenerator, sumoCmd, gamma=0.5, max_steps=10800, num_states=15,
                            num_actions=3, training_epochs=1, total_episodes=1200)

    episode = 0

    total_episodes = 1200
    # Running the simulation following an epsilon greedy policy

    while episode < total_episodes:
        print('\n----- Episode', str(episode+1), 'of', str(total_episodes))
        epsilon = 1.0 - (episode / total_episodes)  # epsilon-greedy policy
        simulation_time, training_time = Simulation.run(episode, epsilon)  # run the simulation
        print('Simulation time:', simulation_time, 's - Training time:',
              training_time, 's - Total:', round(simulation_time+training_time, 1), 's')
        episode += 1

    # Saving the model in a .h5 format for further testing

    Model.save_model(path)

    #  PLOTS

    Visualization.save_data_and_plot(data=Simulation.reward_store,
                                     filename='reward', xlabel='Episode', ylabel='Cumulative negative reward')
    Visualization.save_data_and_plot(data=Simulation.cumulative_wait_store,
                                     filename='delay', xlabel='Episode', ylabel='Cumulative waiting time (s)')
    Visualization.save_data_and_plot(data=Simulation.avg_queue_length_store,
                                     filename='queue', xlabel='Episode', ylabel='Average queue length (vehicles)')
    Visualization.save_data_and_plot(data=Simulation.avg_waiting_time_store,
                                     filename='avg waiting time', xlabel='Episode', ylabel='Average waiting time (seconds)')
    Visualization.save_data_and_plot(data=Simulation.cumulative_CO2Emission_store,
                                     filename='CO2Emission', xlabel='Episode', ylabel='Cumulative CO2 Emissions')
    Visualization.save_data_and_plot(data=Simulation.cumulative_fuelCons_store,
                                     filename='FuelCons', xlabel='Episode', ylabel='Cumulative Fuel Consumption')

    Visualization.save_data_and_plot()
