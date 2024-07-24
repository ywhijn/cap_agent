import traci
import sumolib

def run_simulation():
    # 启动 SUMO 仿真
    sumo_binary = sumolib.checkBinary('sumo')  # 或者 'sumo-gui' 如果你想看到 GUI
    traci.start([sumo_binary, "-c", "sumo.cfg"])

    step = 0
    while step < 1000:
        traci.simulationStep()
        print(f"Simulation step: {step}")
        step += 1

    traci.close()

if __name__ == "__main__":
    run_simulation()
