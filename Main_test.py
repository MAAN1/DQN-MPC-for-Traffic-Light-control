from __future__ import absolute_import
from __future__ import print_function
from Model import Model_test
from Simulation_test import Simulation_test
from Sumo import set_sumo
from visual import Visualization
from utils import set_test_path
from fullgeneration import fullTrafficGenerator

if __name__ == "__main__":

    sumoCmd = set_sumo(True)

    model_path, path_plot = set_test_path(models_path_name='models', model_n=109)

    Model = Model_test(input_dim=15, model_path=model_path)

    fullTrafficGenerator = fullTrafficGenerator()

    Visualization = Visualization(
        path_plot,
        dpi=96
    )

    Simulation_test = Simulation_test(Model, fullTrafficGenerator, sumoCmd, max_steps=10800, num_states=15,
                                      num_actions=3)

    print('\n----- Test episode')
    simulation_time = Simulation_test.run(episode=10000)  # run the simulation
    print('Simulation time:', simulation_time, 's')

    print("----- Testing info saved at:", path_plot)

    Visualization.save_data_and_plot(data=Simulation_test.queue_length_episode, filename='queue', xlabel='Step',
                                     ylabel='Queue length (vehicles)')

    Visualization.save_data_and_plot(data=Simulation_test.cumulative_wait_store, filename='waiting', xlabel='Step',
                                     ylabel='Cumulative Waiting Time')

    Visualization.save_data_and_plot(data=fullTrafficGenerator.Traffic_Arrival, filename='Arrival Generation', xlabel='Step',
                                     ylabel='Number of vehicles Arriving')


