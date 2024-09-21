import random
from collections import defaultdict
from datetime import datetime

from src.Environment import EnvironmentToyModel, ENVIRONMENT
from src.ControlCenter import ControlCenter


import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import logging
import argparse
import yaml
from easydict import EasyDict as edict
import numpy as np
import copy
from src.utils import data_process
def parse_args():
    parser = argparse.ArgumentParser(description='Ride-pooling simulator')
    # general
    parser.add_argument('--cfg',
                        help='experiment configure file name',
                        required=True,
                        type=str)
    parser.add_argument('--OutputDir',
                        help='output directory',
                        type=str,
                        default='./simuLog')
    parser.add_argument('--device',
                        help='GPU or CPU',
                        type=str,
                        default='cuda')
    parser.add_argument('--DrawResult',
                        help='Draw the result image of each step',
                        type=bool,
                        default=False)
    parser.add_argument('--DrawDistribution',
                        help='Draw the distribution of vehicles and requests',
                        type=bool,
                        default=False)
    args = parser.parse_args()

    return args


class Simulation:
    def __init__(self):

        self.args = parse_args()
        with open(self.args.cfg) as f:
            self.cfg = edict(yaml.load(f, Loader=yaml.FullLoader))
        self.logger=self.initilize_logging(self.args, self.cfg)
        self.control_center,self.environment =self.initialize_simulation(self.cfg)
        self.initialize_UV(self.cfg,self.control_center,self.environment)
        self.control_center.cur_step_states['requests_step_dict'] = defaultdict(list)


    def initialize_simulation(self,cfg):
        start_timepoint = cfg.SIMULATION.START
        end_timepoint = cfg.SIMULATION.END
        step_time = cfg.SIMULATION.STEP_TIME
        # For environment
        velocity = cfg.VEHICLE.VELOCITY
        consider_itinerary = cfg.ENVIRONMENT.CONSIDER_ITINERARY.TYPE
        env_type = cfg.ENVIRONMENT.TYPE

        # Initialize environment
        if env_type == 'CITY':
            # Initialize the environment
            environment = ENVIRONMENT(cfg=cfg)
        # elif env_type == 'TOY':
        #     # Initilize the Toy Model
        #     environment = EnvironmentToyModel(num_nodes=cfg.ENVIRONMENT.TOY.NumNode,
        #                                       distance_per_line=cfg.ENVIRONMENT.TOY.DisPerLine,
        #                                       vehicle_velocity=velocity,
        #                                       consider_congestion=False)
        # Initilize the control center
        control_center = ControlCenter(cfg=cfg, environment=environment)

        # Record the number of requests and vehicles
        self.total_steps = int((end_timepoint - start_timepoint) / step_time - 1)
        self.total_grids = int(cfg.ENVIRONMENT.CITY.X_GRID_NUM * cfg.ENVIRONMENT.CITY.Y_GRID_NUM)

        self.logger.info('The number of steps: {}'.format(self.total_steps))
        self.logger.info('The number of grids: {}'.format(self.total_grids))
        self.logger.info('******************************')
        return control_center,environment

    def initialize_UV(self,cfg,control_center,environment):
        pooling_rates = cfg.REQUEST.POOLING_RATE
        # simulation
        # for pooling_rate in pooling_rates:
        # Load requests for test
        pooling_rate = cfg.REQUEST.POOLING_RATE[0]
        test_data_path = cfg.REQUEST.DATA.TEST
        requests, req_num, avg_trip_dis = control_center.RTV_system.InitializeRequests(test_data_path,
                                                                                       pooling_rate=pooling_rate)
        self.logger.info('The number of test requests: {} '.format(req_num))

        veh_num = cfg.VEHICLE.NUM
        # Load vehicles
        vehicles = control_center.RTV_system.InitializeVehicles(cfg.VEHICLE.DATA, num_vehicles=veh_num,
                                                                requests=requests)
        environment.vehicles = vehicles
        epoch_num = 1
        req_num_avg = 0
        requests_results_all = []
        vehicles_results_all = []

        # STEP INITIALIZATION
        control_center.Initialize(requests, vehicles)
    def initilize_logging(self,args, cfg):
        logger = logging.getLogger('')

        # New output filefold
        if not os.path.exists(args.OutputDir):
            os.makedirs(args.OutputDir)
        # New the output filefold of the current experiment
        cfg_file_name = os.path.basename(args.cfg).split('.')[0]
        if not os.path.exists(os.path.join(args.OutputDir, cfg_file_name)):
            os.makedirs(os.path.join(args.OutputDir, cfg_file_name))
        # New the image path
        img_path = os.path.join(args.OutputDir, cfg_file_name, 'tmp')
        if not os.path.exists(img_path):
            os.makedirs(img_path)

        # set the log file path

        file_name_time = f"{datetime.now().strftime('%m-%d-%H-%M')}.log"
        filehandler = logging.FileHandler(os.path.join(args.OutputDir, cfg_file_name, file_name_time))
        streamhandler = logging.StreamHandler()
        logger.setLevel(logging.WARNING)
        logger.addHandler(filehandler)
        logger.addHandler(streamhandler)

        # Write config information
        logger.info('******************************')
        logger.info(cfg)
        logger.info('******************************')
        return logger


    def run_epoch(self,epoch_num, requests, vehicles, control_center, logger):
        vehicles_tmp = copy.deepcopy(vehicles)
        requests_tmp = copy.deepcopy(requests)

        #                              img_path=img_path)
        # for i in range(epoch_num):
        #     vehicles_tmp = copy.deepcopy(vehicles)
        #     requests_tmp = copy.deepcopy(requests)
        #     if args.DrawResult:
        #         img_path = os.path.join(args.OutputDir, cfg_file_name, 'pooled')
        #         req_num = RunEpisode(requests_tmp, vehicles_tmp, control_center, draw_veh_req=True, draw_fre=60,
        #                              img_path=img_path)

    def LogResults(self,logger, requests_results, vehicles_results):
        # Requests
        logger.info('Service rate (non-ride-pooling):  {}'.format(requests_results[0]))
        logger.info('Service rate (ride-pooling):      {}'.format(requests_results[1]))
        logger.info('The average assigning time (s):   {}'.format(requests_results[2]))
        logger.info('The average pick-up time (min):   {}'.format(requests_results[3] / 60))
        logger.info('The average detour time (min):    {}'.format(requests_results[4] / 60))
        logger.info('The average detour time ratio:    {}'.format(requests_results[5]))
        logger.info('The average total time ratio:     {}'.format(requests_results[6]))
        logger.info('The average detour distance (km): {}'.format(requests_results[7] / 1000))
        logger.info('The average detour distance ratio:{}'.format(requests_results[8]))
        logger.info('Cancellation rate (pickup):       {}'.format(requests_results[9]))
        logger.info('Cancellation rate (assign):       {}'.format(requests_results[10]))
        logger.info('Ratio of delivering time to shortest time(ft1):{}'.format(requests_results[11]))
        logger.info('Ratio of delivering time to shortest time(ft2):{}'.format(requests_results[12]))
        logger.info('******************************')

        # Vehicles
        logger.info('The average idle time(min):                     {}'.format(vehicles_results[1] / 60))
        logger.info('The total income of all vehicles (USD):         {}'.format(vehicles_results[2]))
        logger.info('The total travel distance of all vehicles (km): {}'.format(vehicles_results[3] / 1000))
    def reset_step(self):
        """if failed during simulation, all past step should be reset"""
        pass
    def getCurrentVehicles(self):
        return self.control_center.vehicles_all
    def ScanRequests(self):
        # Get the requests in the current step in dict format, id as key
        requests_step_dict = self.control_center.cur_step_states['requests_step_dict'] 
        for idx, request in enumerate(self.control_center.requests_step):
            if request.id not in requests_step_dict:
                requests_step_dict[int(request.id)]=request

        requests_for_each_vehicle,scanned_req_ids,idle_req_ids = self.control_center.scan_requests_by_vehicles()

        self.control_center.cur_step_states['scanned_req_ids'] = scanned_req_ids
        self.control_center.cur_step_states['idle_req_ids'] = idle_req_ids
        self.control_center.cur_step_states['requests_for_each_vehicle'] = requests_for_each_vehicle

    # called after getScannedRequests
    def getFeasibleTrips(self):
        requests_for_each_vehicle = self.control_center.cur_step_states['requests_for_each_vehicle']
        from types import SimpleNamespace
        trip_type_indices = SimpleNamespace()
        #nopool may have multi requests to make a single trip
        trip_type_indices.idle, trip_type_indices.busy, trip_type_indices.nopool, trip_type_indices.normal = [], [], [], []

        feasible_trips, feasible_paths,trip_type_indices = self.control_center.RTV_system.geneTripsBeforeDecision(self.control_center.vehicles_all,requests_for_each_vehicle,trip_type_indices)
        self.control_center.cur_step_states['feasible_trips'] = feasible_trips
        self.control_center.cur_step_states['feasible_paths'] = feasible_paths
        self.control_center.cur_step_states['trip_type_indices'] = trip_type_indices
        return feasible_trips, feasible_paths, trip_type_indices
    def getScoredTrips(self):
        feasible_trips = self.control_center.cur_step_states['feasible_trips']
        feasible_paths = self.control_center.cur_step_states['feasible_paths']
        # trip_type_indices = self.control_center.cur_step_states['trip_type_indices']
        pre_values=None
        scored_trips = self.control_center.evaluation_system.ScoreTrips(feasible_trips, feasible_paths, pre_values)
        self.control_center.cur_step_states['scored_trips'] = scored_trips
        return scored_trips
    # return the conditions of candidate vehicles and requests in the feasible trips before decision
    # split the vehicle and request in trips so that uv can be paired from scratch. v are filtered by the idle vehicles
    # called after getFeasibleTrips
    def formateUV4Trips(self,):  #TODO API input for the decision maker, LLM
        candidate_V = {}      # the vehicle with paired trip
        candidate_U = {}          # the request with paired trip
        idle_V_beforeDecision = {} # the vehicle is obviously idle before the decision
        idle_U_beforeDecision = {} # the req is obviously waiting before the decision
        feasible_trips = self.control_center.cur_step_states['feasible_trips']
        feasible_paths = self.control_center.cur_step_states['feasible_paths']
        trip_type_indices = self.control_center.cur_step_states['trip_type_indices']
        scanned_req_ids = self.control_center.cur_step_states['scanned_req_ids']
        idle_req_ids = self.control_center.cur_step_states['idle_req_ids']



        for idx, feasible_trip in enumerate(feasible_trips):
            v_id, v_info = self.formatVinfo(self.control_center.vehicles_all[idx])
            if idx in trip_type_indices.idle:
                idle_V_beforeDecision[v_id]=v_info
            elif idx in trip_type_indices.normal or idx in trip_type_indices.nopool:
                candidate_V[v_id]=v_info

        for scanned_req_id in scanned_req_ids:
            current_req = self.control_center.cur_step_states["requests_step_dict"]
            u_id, u_info = self.formatUinfo(current_req[scanned_req_id])
            candidate_U[u_id] = u_info
        idle_sampled_v = random.sample(trip_type_indices.idle,min(2, len(trip_type_indices.idle)))
        sampled_v = list(set(candidate_V.keys()) | set(idle_sampled_v))
        return candidate_U, candidate_V, sampled_v

    # if u considered by more v, u paired with multiple v candidates  # TODO u can be rejected as the reward is too low
    # if v considered by more u, v paired with multiple u candidates  # TODO which u is suitable for the v
    def formateDemandNeed4Trips(self,):
        #  TODO construct SFT data for hard decision
        candidate_V = {}      # the vehicle with paired trip
        candidate_U = {}          # the request with paired trip
        idle_V_beforeDecision = {} # the vehicle is obviously idle before the decision
        idle_U_beforeDecision = {} # the req is obviously waiting before the decision
        feasible_trips = self.control_center.cur_step_states['feasible_trips']
        feasible_paths = self.control_center.cur_step_states['feasible_paths']
        trip_type_indices = self.control_center.cur_step_states['trip_type_indices']
        scanned_req_ids = self.control_center.cur_step_states['scanned_req_ids']
        idle_req_ids = self.control_center.cur_step_states['idle_req_ids']


        V2MultiU =defaultdict(set)
        U2MultiV =defaultdict(set)
        for idx, trips in enumerate(feasible_trips): # the candidate trips for v, each trip has different combination of scanned reqs
            for trip in trips:
                if len(trip.requests)>0:
                    for req in trip.requests:
                        v_id,u_id=int(idx),int(req.id)
                        V2MultiU[v_id].add(u_id)
                        U2MultiV[u_id].add(v_id)

            v_id, v_info = self.formatVinfo(self.control_center.vehicles_all[idx])

            if idx in trip_type_indices.idle:
                idle_V_beforeDecision[v_id]=v_info
            elif idx in trip_type_indices.normal or idx in trip_type_indices.nopool:
                candidate_V[v_id]=v_info

        for scanned_req_id in scanned_req_ids:
            current_req = self.control_center.cur_step_states["requests_step_dict"]
            u_id, u_info = self.formatUinfo(current_req[scanned_req_id])
            candidate_U[u_id] = u_info
        idle_sampled_v = random.sample(trip_type_indices.idle,min(2, len(trip_type_indices.idle)))
        sampled_v = list(set(candidate_V.keys()) | set(idle_sampled_v))

        # convert set to list for dict
        V2MultiU_lst = defaultdict(list)
        U2MultiV_lst = defaultdict(list)
        for v in V2MultiU.keys():
            V2MultiU_lst[v] = list(V2MultiU[v])
        for u in U2MultiV.keys():
            U2MultiV_lst[u] = list(U2MultiV[u])
        # print(candidate_U)
        # print(candidate_V)
        # print("idle vehicles ",idle_sampled_v)
        # for u in candidate_U.items():
        #     print("u",u)
        return U2MultiV_lst, V2MultiU_lst, candidate_U, candidate_V, sampled_v


    def decision2Trips(self,decisions): #

        scored_trips = self.control_center.cur_step_states['scored_trips']
        feasible_paths = self.control_center.cur_step_states['feasible_paths']
        final_trips, final_paths, scores = self.control_center.ChooseTripsbyPairs(scored_trips,feasible_paths,decisions)

        self.control_center.cur_step_states['final_trips'] = final_trips
        self.control_center.cur_step_states['final_paths'] = final_paths
        self.control_center.cur_step_states['scores'] = scores


    def formatVinfo(self,v): # TODO add more info, e.g. idle time and total income
        # v_info={"current position":data_process.map_npTuple(v.current_position),"available seats":v.max_capacity - v.current_capacity}
        v_info = {"current position": data_process.map_npTuple(v.current_position)}
        if len(v.current_requests) > 0 :
            current_requests_info = {}
            for u in v.current_requests:
                u_id, u_info = self.formatUinfo(u)
                current_requests_info[u_id] = u_info
            v_info["current_requests"] = current_requests_info

        if len(v.next_requests) > 0:
            next_requests_info = {}
            for u in v.next_requests:
                u_id, u_info = self.formatUinfo(u)
                next_requests_info[u_id] = u_info
            v_info["next_requests"] = next_requests_info
        return  int(v.id), v_info


    def formatUinfo(self,u):
        u_info = {"origin":data_process.map_npTuple(u.pickup_position),"destination":data_process.map_npTuple(u.dropoff_position),
                  "state": self.control_center.tracker_system.get_state_text(u)}
        return int(u.id), u_info

    # input the two id lists of vehicles and requests, output the pairs of vehicles and requests randomly
    # each request can only be paired with at most one vehicle
    def decision_random_pairs(self,u_ids,v_ids):
        pairs = []
        # the number of requests that can be matched, at least 0.6
        num_matched_u = int( len(u_ids) * min(1.0, random.random() + 0.8) )
        #choose v randomly withou replacement
        random.shuffle(v_ids)
        random.shuffle(u_ids)
        for i in range(num_matched_u):
            pairs.append((u_ids[i],v_ids[i]))
        return pairs

    def action_step(self):
        final_trips, final_paths = self.control_center.cur_step_states['final_trips'], self.control_center.cur_step_states['final_paths']
        vehicles_to_reposition = self.control_center.UpdateVehicles(final_trips, final_paths)
        self.control_center.RepositionVehicles(vehicles_to_reposition)
        self.control_center.SimulateVehicleAction()
        # Process the requests that unassigned: cancel or wait
        unmatched_requests = self.control_center.ProcessRequests()
        # Update requests, allocate new requests for next step
        self.control_center.UpdateRequests(unmatched_requests)

        self.control_center.step+=1

        current_timepoint = self.control_center.start_timepoint + self.control_center.step * self.control_center.step_time
        self.control_center.UpdateParameters(current_timepoint, self.control_center.step)

    def run_simulation_step(self):
        self.ScanRequests()
        self.getFeasibleTrips()
        candidate_U, candidate_V, sampled_v = self.formateUV4Trips()

        decisions = self.decision_random_pairs(list(candidate_U.keys()), sampled_v)

        self.getScoredTrips()
        self.implementDecision(decisions)

    def getUVInfo_BeforeDecision(self):
        self.ScanRequests()
        self.getFeasibleTrips()
        candidate_U, candidate_V, sampled_v = self.formateUV4Trips()
        self.getScoredTrips()
        return candidate_U, candidate_V, sampled_v

    def getDemandNeed_BeforeDecision(self):
        self.ScanRequests()
        self.getFeasibleTrips()
        U2MultiV, V2MultiU, candidate_U, candidate_V, sampled_v = self.formateDemandNeed4Trips()
        self.getScoredTrips()
        print("#\n\tBeforeDecision:")
        self.control_center.tracker_system.log_BeforeDemandNeedDecision(self.control_center, U2MultiV, V2MultiU)

        return self.control_center.step,candidate_U, candidate_V, U2MultiV, V2MultiU

    def implementDecision(self,decisions):
        print("#\n\timplementDecision: ",decisions)
        self.decision2Trips(decisions)
        self.action_step()
        self.control_center.tracker_system.flow_track(self.control_center)

    # function: Calculate the travel distance and time between origin and destination according to the type
    # params: The origin and destination position, type: 'Linear', 'Manhattan' or 'Itinerary'
    # return: the travel distance and time
    def getDTw2Loc(self,origin, destination):
        if not isinstance(origin, tuple) or not isinstance(destination, tuple):
            raise ValueError('The origin and destination should be tuple')
        dis, time=self.environment.GetDistanceandTime(origin, destination)
        round_digit = 2
        return {"Distance":round(dis, round_digit),"Time":round(time, round_digit) }
    # pairs of vehicle and request

    def getUV_loc_prompt(self):
        requests, vehicles=self.control_center.requests_step, self.control_center.vehicles_all
        return self.control_center.agent_system.getUV_loc_prompt(requests,vehicles)
    def setConstraints4FeasibleTrips(self,constraints):
        self.control_center.setConstraints4FeasibleTrips(constraints)

from flask import Flask, request, jsonify

app = Flask(__name__)
app.logger.setLevel(logging.ERROR)

# @app.route('/run', methods=['POST'])
# def run():
#     data = request.get_json()
#     simu.run(data)
#     return jsonify(data)

@app.route('/getCurrentRequests', methods=['GET'])
def getCurrentRequests():
    return jsonify(simu.control_center.requests_step)

@app.route('/getCurrentVehicles', methods=['GET'])
def getCurrentVehicles():
    return jsonify(simu.getCurrentVehicles())

@app.route('/getScanedRequests', methods=['GET'])
def getScanedRequests():
    return jsonify(simu.control_center.AllocateRequest2Vehicles())

@app.route('/get1stUVlocText', methods=['GET'])
def getUV_loc_prompt():
    return jsonify(simu.getUV_loc_prompt())

@app.route('/get_dt_w2_loc', methods=['POST'])
def get_dt_w2_loc():
    data = request.get_json()
    origin = tuple(data.get('origin'))
    destination = tuple(data.get('destination'))
    result = simu.getDTw2Loc(origin, destination)
    return jsonify(result)
@app.route('/getUVinfo', methods=['GET'])
def getGetFlow_UVinfo():
    Uinfo, Vinfo, idleVs= simu.getUVInfo_BeforeDecision()
    return jsonify({"Passengers":Uinfo,"Taxis":Vinfo})
@app.route('/getDemandNeed', methods=['GET'])
def getgetDemandNeedInfo():
    step, candidate_U, candidate_V, U2MultiV, V2MultiU = simu.getDemandNeed_BeforeDecision()
    return jsonify({"step":step,"Passengers":candidate_U,"Taxis":candidate_V, "U2MultiV":U2MultiV, "V2MultiU":V2MultiU})
@app.route('/implementDecision', methods=['POST'])
def implementDecision():
    data = request.get_json()
    decisions = list(data.get('decisions'))
    decisions = data_process.strList2intList(decisions)
    simu.implementDecision(decisions)
    return jsonify({"status":"success"})


@app.route('/getGetPool_UVinfo', methods=['GET'])
def getGetPool_UVinfo():
    for _ in range(40):
        simu.run_simulation_step()
    return jsonify(simu.getUVinfo())

@app.route('/GetItinerary', methods=['POST'])
def get_itinerary():
    data = request.get_json()
    origin = tuple(data.get('origin'))
    destination = tuple(data.get('destination'))
    itinerary,dis,time = simu.environment.GetItinerary(origin, destination)
    return jsonify(itinerary)



if __name__ == '__main__':
    simu = Simulation()
    # for _ in range(10):
    #     simu.run_simulation_step()
    app.run(host='localhost', port=10086, debug=True)