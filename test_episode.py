import copy
from tqdm import tqdm
import numpy as np
import time
import matplotlib.pyplot as plt
import os
import copy

from src.RL.states import States

running_time_for_print = 20

'''
    (1) agent=None and train=False mean running the simulation without RL model
    (2) One can find anything in the control_centrol
'''


def TestEpisode(requests, vehicles, control_center, agent=None, train=False, train_step=0, draw_veh_req=False,
               draw_fre=60, img_path='exp'):
    # Initialization
    control_center.Initialize(requests, vehicles)
    if agent:
        states = States(cfg=control_center.cfg,
                        environment=control_center.environment,
                        requests_record_time=1800)  # We record requests in the previous 30 mins
    imgs = []
    img_cnt = 0
    req_num = 0

    # Run the simulation
    for step in tqdm(range(control_center.total_steps), desc='Running simulation steps: '):
        # Upadate parameters of the control center
        current_timepoint = control_center.start_timepoint + step * control_center.step_time
        control_center.UpdateParameters(current_timepoint, step)



        control_center.UpdateRequests([])


    req_num /= control_center.simulation_steps

    return req_num