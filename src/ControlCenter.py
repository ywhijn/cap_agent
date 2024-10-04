from collections import defaultdict

from .ActionSystem import ActionSystem
from .RTVSystem import RTVSystem
from .EvaluationSystem import EvaluationSystem
from .PostProcessSystem import PostProcessSystem
from .LogSystem import  TrackerSystem
import numpy as np


'''
The control center is just like a ride-hailing platform
All requests and vehicles are handled here
The control center consists of 4 subsystems:
1. RTV System: handles requests, vehicles and trips
2. Evaluation System: evaluates and chooses trips
3. Action System: simulates actions and manages all vehicles
4. Post Process System: count and visulize results

See each object for detailed information
'''
from typing import List, Dict, Tuple, Set, Any, Optional, Callable

class ControlCenter:
    def __init__(self,
                cfg,
                environment
                ):
        self.cfg = cfg
        self.environment = environment
        self.step_time = self.cfg.SIMULATION.STEP_TIME
        self.start_timepoint = self.cfg.SIMULATION.START
        self.end_timepoint = self.cfg.SIMULATION.END
        self.total_steps = int((self.end_timepoint + self.cfg.SIMULATION.TIME2FINISH - self.start_timepoint) / self.step_time - 1)
        self.simulation_steps = int((self.end_timepoint - self.start_timepoint) / self.step_time)
        
        self.consider_itinerary = self.cfg.ENVIRONMENT.CONSIDER_ITINERARY.TYPE

        self.RTV_system = RTVSystem(cfg = cfg, environment = self.environment)
        self.evaluation_system = EvaluationSystem(cfg = cfg, environment=self.environment)

        self.current_timepoint = self.start_timepoint
        self.step = 0

        # Initialize requests and vehicles, see class RTVSystem for detailed information
        self.requests_all = None
        self.requests_step = None
        self.vehicles_all = None

        self.action_system = ActionSystem(cfg = self.cfg,
                                        vehicles = None,
                                        requests = None,
                                        environment = self.environment,
                                        current_timepoint = self.current_timepoint,
                                        step_time = self.step_time,
                                        RTV_system = self.RTV_system,
                                        consider_itinerary = self.consider_itinerary)

        self.post_process_system = PostProcessSystem(vehicles = None,
                                                    requests = None,
                                                    environment = self.environment,
                                                    current_timepoint = self.current_timepoint
                                                    )
        self.cur_step_states=defaultdict()
        self.empty_decision_steps = defaultdict()
        self.tracker_system = TrackerSystem(cfg = self.cfg,environment = self.environment, current_timepoint = self.current_timepoint, step_time = self.step_time)
        # self.agent_system = AgentSystem(cfg = self.cfg, env = self.environment)

    # Initialize the requests and vehicles
    def Initialize(self, requests, vehicles):
        self.requests_all = requests
        self.vehicles_all = vehicles
        self.requests_step = requests[self.step]
        self.action_system.vehicles = vehicles
        self.action_system.requests = requests[self.step]
        self.action_system.reposition.past_requests = requests[self.step]
        self.post_process_system.requests = requests[self.step]
        self.post_process_system.vehicles = vehicles

        # if self.agent_system.agent==None:
        #     self.agent_system.initialize()




    def get_scanned_UVpair(self,requests_for_each_vehicle,vehicles):
        pair_list= []
        req_set = set()
        veh_set = set()
        for i in range(len(requests_for_each_vehicle)):
            for scanned_req in requests_for_each_vehicle[i]:
                pair_list.append((scanned_req.id,i))
                req_set.add(scanned_req)
                veh_set.add(vehicles[i])
        return pair_list,req_set,veh_set

    '''RTV System'''
    # Allocate requests to each vehicle, see class RTVSystem for detailed information    
    def AllocateRequest2Vehicles(self, max_num_vehicles = 30, max_match_distance = 3000):
        requests_for_each_vehicle=None
        # self.agent_system.trytools("test")
        # self.agent_system.test_agent("test")
        requests_for_each_vehicle = self.RTV_system.AllocateRequest2Vehicles(self.requests_step, self.vehicles_all, max_num_vehicles, max_match_distance)
        # scanned_UVpairs,req_set,veh_set = self.get_scanned_UVpair(requests_for_each_vehicle,self.vehicles_all)
        # UV_loc_string=self.agent_system.getUV_loc_Prompt(list(req_set), list(veh_set))
        # # save UV_loc_string  to file immediately
        # with open('UV_loc_string.txt', 'w') as f:
        #     f.write(UV_loc_string)
        # agent_response=self.agent_system.agent.agent_run(UV_loc_string)
        # print(f'agent response Output, {agent_response}')
        # agent_action = self.agent_system.parse_output(agent_response)
        # print(f'parsed response Output, {agent_action}')
        #
        # print(f'scanned_UVpairs, {scanned_UVpairs}')
        # self.tracker_system.fill_step_requests_id(self.requests_step)
        # exit()
        return requests_for_each_vehicle

    def scan_requests_by_vehicles(self, max_num_vehicles = 30, max_match_distance = 3000):
        requests_for_each_vehicle,scanned_req_ids,idle_req_ids = self.RTV_system.scan_requests_by_vehicles(self.requests_step, self.vehicles_all,
                                                                             max_num_vehicles, max_match_distance)
        return requests_for_each_vehicle,scanned_req_ids,idle_req_ids

    # Generate feasible trips and the corresponding paths, see class RTVSystem for detailed information
    def GenerateFeasibleTrips(self, requests_for_each_vehicle, MAX_IS_FEASIBLE_CALLS = 150, MAX_TRIPS = 30):
        feasible_trips, feasible_paths = self.RTV_system.GenerateFeasibleTrips(self.vehicles_all, requests_for_each_vehicle, MAX_IS_FEASIBLE_CALLS, MAX_TRIPS)
        # self.tracker_system.compare_scan_feasible(requests_for_each_vehicle,self.vehicles_all,feasible_trips)
        return feasible_trips, feasible_paths

    # Initialize requests in each batch, see class RTVSystem for detailed information
    def IniReqsBatch(self, reqs, update_all = False):
        return self.RTV_system.IniReqsBatch(reqs=reqs, update_all=update_all)


    '''Evaluation System'''
    # Score feasible trips, see class EvaluationSystem for detailed information
    def ScoreTrips(self, feasible_trips, feasible_paths, pre_values):
        scored_feasible_trips = self.evaluation_system.ScoreTrips(feasible_trips, feasible_paths, pre_values)
        return scored_feasible_trips
    
    # Score feasible trips based on Reinforcement Learning, see class EvaluationSystem for detailed information
    # todo...
    def ScoreTripsRL(self, feasible_trips):
        return self.evaluation_system.ScoreTripsRL(feasible_trips)

    # Choose a trip and the corresponding path for each vehicle, see class EvaluationSystem for detailed information
    def ChooseTrips(self, scored_feasible_trips, feasible_paths):
        final_trips, final_paths, rewards = self.evaluation_system.ChooseTrips(scored_feasible_trips, feasible_paths)
        # self.tracker_system.compare_feasible_final(final_trips, self.vehicles_all,scored_feasible_trips)
        # self.tracker_system.check_repeated_req(final_trips, final_paths)
        return final_trips, final_paths, rewards
    
    def ChooseTripsbyPairs(self, scored_feasible_trips, feasible_paths, uv_decision_pairs):
        trip_to_id = {}
        id_to_trip = {}
        current_trip_id = 0
        requests_dict = {}
        UV2trip_id= {} # all UV pair from trips
        # self.tracker_system.compare_feasible_final(final_trips, self.vehicles_all,scored_feasible_trips)
        # self.tracker_system.check_repeated_req(final_trips, final_paths)
        for vehicle_idx, scored_trips in enumerate(scored_feasible_trips):
            for trip, score, reward in scored_trips:
                # Convert trip -> id if it hasn't already been done
                if trip not in trip_to_id:
                    trip_to_id[trip] = current_trip_id
                    id_to_trip[current_trip_id] = trip
                    current_trip_id += 1
                    trip_id = current_trip_id - 1
                else:
                    trip_id = trip_to_id[trip]

                # Update set of requests in trips
                for request in trip.requests:
                    uv_pair = (int(request.id), int(vehicle_idx))
                    if request.id not in requests_dict:
                        requests_dict[request.id] = request
                    if uv_pair not in UV2trip_id:
                        UV2trip_id[uv_pair] = [trip_id]
                    else:
                        UV2trip_id[uv_pair].append(trip_id)


        final_trips = []
        scores = []
        final_paths = []


        assigned_trips={}
        # print("##Function：ChooseTripsbyPairs：\n\tall of possible UV pairs to the trip_id ", UV2trip_id)
        # Get vehicle specific trips from the decision pairs
        for uv_decision_pair in uv_decision_pairs:
            uid,vid = uv_decision_pair
            # failed decision for this vehicle
            if uv_decision_pair not in UV2trip_id.keys():
                print(f'##Function：ChooseTripsbyPairs：\n\tuv pair has no trips ! uv_decision_pair, {uv_decision_pair}')
                paired_req=[]
                for trip_uv in UV2trip_id.keys():
                    if vid == trip_uv[1]:
                        paired_req.append(trip_uv[0])
                print(f"##Function：ChooseTripsbyPairs：\n\tbut the vehicle {vid} requests are: ",paired_req) # debug
                # TODO log this for LLM to distinguish the failed reason # prepared trip options for LLM
                continue
            if len(UV2trip_id[uv_decision_pair]) > 1: # check the trip condition, expand the trip in detail
                self.tracker_system.log_multi_trips(self,uv_decision_pair, UV2trip_id,id_to_trip)
                # raise Exception(f'Function：ChooseTripsbyPairs：\nuv pair has more trips ! uv_decision_pair, {uv_decision_pair}, {UV2trip_id[uv_decision_pair]}')
            assigned_trip_id = UV2trip_id[uv_decision_pair][0]
            assigned_trips[vid] = assigned_trip_id # one trip for one vehicle

        for vehicle_idx in range(len(scored_feasible_trips)):
            try:
                assigned_trip_id = assigned_trips[vehicle_idx]
                assigned_trip = id_to_trip[assigned_trip_id]
            except:
                # if the vehicle has no assigned trip, then assign the first empty trip
                assigned_trip = scored_feasible_trips[vehicle_idx][0][0]
            scored_final_trip = None  # The final trip is None if there are no assigned trips

            for trip_idx, (trip, score, reward) in enumerate(scored_feasible_trips[vehicle_idx]):
                if (trip == assigned_trip):
                    scored_final_trip = trip
                    final_score = score
                    final_reward = reward
                    final_path = feasible_paths[vehicle_idx][trip_idx]
                    break

            assert scored_final_trip is not None
            final_trips.append(scored_final_trip)
            if final_reward is not None:
                scores.append(final_score)
            final_paths.append(final_path)

        return final_trips, final_paths, scores
        # Update the system's parameters

    def UpdateParameters(self, timepoint, step):
        self.current_timepoint = timepoint
        self.RTV_system.current_timepoint = timepoint
        self.action_system.current_timepoint = timepoint
        self.post_process_system.current_timepoint = timepoint
        self.step = step

        # Update requests at next time step
        # params: Unmatched_requests: requests that haven't been allocated to any vehicles and don't cancel

    def UpdateRequests(self, unmatched_requests):
        if self.step >= self.total_steps - 1 or self.step >= len(self.requests_all) - 1:
            new_requests = []
        else:
            new_requests = self.requests_all[self.step + 1]  # New requests at next time step
        requests = list(set(unmatched_requests) | set(new_requests))  # Union
        # self.tracker_system.fill_step_requests_id(requests,self.step+1)
        self.action_system.requests = requests
        self.post_process_system.requests = requests
        self.requests_step = requests
        # Update distribution of requests and vehicles that will be used to guide repositioning
        self.environment.UpdateDistributions(new_requests, self.vehicles_all)

    '''Action System'''
    # Update the trip and the path of the vehicle, see class ActionSystem for detailed information
    def UpdateVehicles(self, final_trips, final_paths, vehicles = None):
        vehicles2reposition = self.action_system.UpdateVehicles(final_trips, final_paths, vehicles)
        return vehicles2reposition
    def RepositionVehicles(self, vehicles_to_reposition):
        if self.cfg.VEHICLE.REPOSITION.TYPE and len(vehicles_to_reposition) > 0 :
            self.action_system.reposition.Reposition(vehicles_to_reposition)
        # Update path (including itinerary nodes)
        if self.consider_itinerary:
            for vehicle in vehicles_to_reposition:
                if vehicle.path is not None:
                    self.RTV_system.PlanPath.UpdateItineraryNodes(vehicle.path)
                    # The path of the vehicle may change, so we need to update the traffic density for the road
                    if self.action_system.consider_congestion:
                        self.action_system.UpdateSpeed(vehicle)
    
    # Simulate the action of each vehicle and manage all vehicles, see class ActionSystem for detailed information
    def SimulateVehicleAction(self, vehicles = None):
        self.action_system.SimulateVehicleActions(vehicles)

    # Remove the finished requests, and the unmatched requests are returned and will be merged with the requests at next time step, see class ActionSystem for detailed information
    def ProcessRequests(self):
        unmatched_requests = self.action_system.ProcessRequests()
        return unmatched_requests


    '''PostProcess System'''
    # Draw the time distribution of sending requests, see class PostProcessSystem for detailed information
    def ReqTimeSta(self, ax, requests):
        ax = self.post_process_system.ReqTimeSta(ax = ax, requests = requests)
        return ax
    
    # Draw the distance distribution of requests, see class PostProcessSystem for detailed information
    def ReqDisSta(self, ax, requests, MaxDis = None, nor_fit = True):
        ax = self.post_process_system.ReqDisSta(ax = ax, requests = requests, MaxDis = MaxDis, nor_fit = nor_fit)
        return ax
    
    # Draw road network of New York model, see class PostProcessSystem for detailed information
    def DrawRoadNetwork(self, ax, TIME = False, congestion = False, speed_lim = [0,20], axis_lim = None):
        ax = self.post_process_system.DrawRoadNetwork(ax, TIME = TIME, congestion = congestion, speed_lim = speed_lim, axis_lim = axis_lim)
        return ax
    
    # Draw the distribution of vehicles, see class PostProcessSystem for detailed information
    def DrawVehicles(self, ax, vehicles, v_size = 0.002):
        ax = self.post_process_system.DrawVehicles(ax = ax, vehicles = vehicles, v_size = v_size)
        return ax
    
    # Draw the distribution of requests, see class PostProcessSystem for detailed information
    def DrawRequests(self, ax, requests, type = 'pickup', s = 10, count = False, cmap = 'viridis', cmax = 10, color = 'red', draw_grid = False):
        ax = self.post_process_system.DrawRequests(ax = ax, requests = requests, type = type, s = s, count = count, cmap = cmap, cmax = cmax, color = color, draw_grid = draw_grid)
        return ax
    
    # Draw vehicles and requests of at a specific time point, see class PostProcessSystem for detailed information
    def DrawSnapshot(self, ax, v_size = 0.002, s = 100, colors = [], draw_route = True, draw_road_network = True, speed_lim = [0, 20], axis_lim = None):
        ax = self.post_process_system.DrawSnapshot(ax, v_size = v_size, s = s, colors=colors, draw_route = draw_route, draw_road_netwrod=draw_road_network, speed_lim=speed_lim, axis_lim = axis_lim)
        return ax
    def DrawPooledSnapshot(self, ax,chosen_v, v_size = 0.002, s = 100, colors = [], draw_route = True, draw_road_network = True, speed_lim = [0, 20], axis_lim = None):
        # ax = self.post_process_system.DrawSnapshot(ax, v_size = v_size, s = s, colors=colors, draw_route = draw_route, draw_road_netwrod=draw_road_network, speed_lim=speed_lim, axis_lim = axis_lim)
        ax = self.post_process_system.DrawSoloSnapshot(ax,chosen_v=chosen_v,v_size = v_size, s = s, colors=colors, draw_route = draw_route, draw_road_netwrod=draw_road_network, speed_lim=speed_lim, axis_lim = axis_lim)
        return ax

    # Calculate the aspect ratio of the figure, see class PostProcessSystem for detailed information
    def FigAspectRatio(self, box = None):
        return self.post_process_system.FigAspectRatio(box = box)

    # Draw road network of toy model, see class PostProcessSystem for detailed information
    def DrawRoadNetworkToyModel(self, ax):
        return self.post_process_system.DrawRoadNetworkToyModel(ax)

    # Draw vehicles and requests of toy model, see class PostProcessSystem for detailed information
    def DrawVehiclesandRequestsToyModel(self, ax):
        ax = self.post_process_system.DrawVehiclesandReuqestsToyModel(ax)
        return ax
    # Integrate all result images to a vedio, see class PostProcessSystem for detailed information
    def MakeVedio(self, imgs = None, img_path = 'Output/tmp', vedio_fps = 30, vedio_path = 'Output', vedio_name = 'result.mp4', del_img = False):
        self.post_process_system.MakeVedio(imgs = imgs, img_path = img_path, vedio_fps = vedio_fps, vedio_path = vedio_path, vedio_name=vedio_name, del_img = del_img)


    ''' 
    Once the simulation finished, we calculate:
    (1) REQUEST
        0.  Service rate (non-ride-pooling)
        1.  Service rate (ride-pooling)
        2.  The average assigning time
        3.  The average waiting time of requests
        4.  The average detour time
        5.  The average detour time ratio
        6.  The average total time ratio
        7.  The average detour distance
        8.  The average detour distance ratio
        9. Cancellation rate (assign)
        10. Cancallation rate (pickup)
        11. ft1
        12. ft2
    (2) VEHICLE
        1. The number of vehicles
        2. The average idle time
        3. The total income of all vehicles
        4. The total travel distance of all vehicles
    '''
    def CalculateResults(self):
        requests_results = np.zeros((13))
        vehicles_results = np.zeros((4))
        # Requests' results
        num_req = 0
        num_req_pool = 0
        num_req_non = 0
        for requests in self.requests_all:
            for request in requests:
                num_req += 1
                if request.max_tol_num_person == 1:
                    num_req_non += 1
                else:
                    num_req_pool += 1
                # The request has been served
                if request.finish_dropoff:
                    if request.max_tol_num_person == 1:
                        requests_results[0] += 1
                    else:
                        requests_results[1] += 1
                    requests_results[2] += request.assign_timepoint - request.send_request_timepoint
                    requests_results[3] += request.pickup_timepoint - request.assign_timepoint
                    requests_results[4] += max(0, request.time_on_vehicle - request.original_travel_time)
                    requests_results[5] += max(0, request.time_on_vehicle - request.original_travel_time) / request.original_travel_time
                    requests_results[6] += (request.time_on_vehicle + request.pickup_timepoint - request.send_request_timepoint) / request.original_travel_time
                    requests_results[7] += max(0, request.distance_on_vehicle - request.original_travel_distance)
                    requests_results[8] += max(0, request.distance_on_vehicle - request.original_travel_distance) / request.original_travel_distance
                    requests_results[11] += request.time_on_vehicle
                    requests_results[12] += request.time_on_vehicle + request.pickup_timepoint - request.assign_timepoint
                    #requests_results[4] += request.dropoff_timepoint - request.pickup_timepoint - request.original_travel_time
                    # requests_results[5] += request.distance_on_vehicle - request.original_travel_distance
                # The request has been cancelled
                # Note: Here, we assume that there is no passenger at any vehicles. In other words, all trips are finished at the end of simulation
                else:
                    if request.finish_assign:
                        requests_results[9] += 1
                    else:
                        requests_results[10] += 1
        
        print('*'*50)
        print('The number of requests: ', num_req)
        print('The number of non-ride-pooling requests: ', num_req_non)
        print('The number of ride-pooling requests: ', num_req_pool)
        print('Service rate: ', (requests_results[0] + requests_results[1]) / num_req)
        print('*'*50)
        
        # mean value
        requests_results[2:9] /= (requests_results[0]+requests_results[1])
        requests_results[11:] /= (requests_results[0]+requests_results[1])
        requests_results[0] /= num_req_non
        requests_results[1] /= num_req_pool
        requests_results[9:11] /= num_req
        # Vehicles' results
        for vehicle in self.vehicles_all:
            vehicles_results[0] += 1
            vehicles_results[1] += vehicle.total_idle_time
            # Here, we calculate the total income and travel distance to evaluate the system's income and energy consumption
            vehicles_results[2] += vehicle.total_income
            vehicles_results[3] += vehicle.total_distance
        vehicles_results[1] /= vehicles_results[0]

        return requests_results, vehicles_results


    # function: calculate the average number of requests in each vehicle
    # params: all vehicles
    # return: the average number of reuqests in a vehicle at this simulation step
    def VehicleUtility(self):
        req_num = 0
        for vehicle in self.vehicles_all:
            req_num += vehicle.current_capacity
            req_num += sum(req.num_person for req in vehicle.next_requests)
        
        ave_req_num = req_num / len(self.vehicles_all)

        return ave_req_num

    