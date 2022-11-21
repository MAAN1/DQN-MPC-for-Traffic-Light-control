import os
import sys
from sumolib import checkBinary

# Setting the sumo-gui path

max_steps = 10800


def set_sumo(gui):

    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")

    # setting the cmd mode or the visual mode
    if gui == False:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # setting the cmd command to run sumo at simulation time
    sumo_cmd = [sumoBinary, "-c", 'main.sumocfg', "--no-step-log", "true", "--waiting-time-memory", str(max_steps)]

    return sumo_cmd
