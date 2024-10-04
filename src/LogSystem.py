"""
select pooled vehicle to track
each trip and path at least has an empty
"""
import json
from collections import defaultdict
from datetime import datetime

from src.llm.LLM_options import  cfg as log_cfg
TESTING = False
import logging
import matplotlib.pyplot as plt
import os
import copy
import re
from src.utils import data_process
class SingleLineKeyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indent = 2
        self.current_indent = 0

    def encode(self, obj):
        if isinstance(obj, dict):
            if not obj:
                return '{}'
            self.current_indent += self.indent
            lines = []
            for key, value in obj.items():
                key_str = json.dumps(key, ensure_ascii=False)
                value_str = self.encode(value)
                lines.append(f"{self.current_indent * ' '}{key_str}: {value_str}")
            result = '{\n' + ',\n'.join(lines) + '\n'
            self.current_indent -= self.indent
            result += self.current_indent * ' ' + '}'
            return result
        elif isinstance(obj, (list, tuple)):
            if len(obj) == 0:
                return '[]'
            elif len(obj) == 1:
                return '[' + self.encode(obj[0]) + ']'
            else:
                self.current_indent += self.indent
                lines = [self.current_indent * ' ' + self.encode(item) for item in obj]
                result = '[\n' + ',\n'.join(lines) + '\n'
                self.current_indent -= self.indent
                result += self.current_indent * ' ' + ']'
                return result
        return json.dumps(obj, ensure_ascii=False)
class TrackerSystem:
    def __init__(self, cfg,environment,
                current_timepoint,
                step_time):
        self.track_vehicle_dict={}
        self.solo_id=[]
        self.pooled_id=None
        self.cfg = cfg
        self.environment = environment
        self.current_timepoint = current_timepoint
        self.step_time = step_time
        self.stage_state_dict= {}
        self.fail_feasible=[]
        self.step_requests_id=[]
        self.req_id2state = {0: "waiting", 1: "assigned", 2: "picked up", 3: "dropped off"}
        self.req_state2id = {"waiting": 0, "assigned": 1, "picked up": 2, "dropped off": 3}
        self.V_pathed_after_assigned = defaultdict() # { vehicle_id: { req_id:[path position] } }
        self.U_state_tracker =  defaultdict() # { req_id: {state :[step] } }
        self.empty_decision = defaultdict() #

        self.step_states = defaultdict(defaultdict)
        self.step_u=defaultdict(defaultdict)
        self.step_v=defaultdict(defaultdict)
        folder_name_time = f"{datetime.now().strftime('%m-%d-%H-%M')}.log"

        dirname, filename = os.path.split(os.path.abspath(__file__))
        STEP_STATE_DIR = os.path.join(f'{dirname}/simulogs', folder_name_time)
        os.makedirs(STEP_STATE_DIR, exist_ok=True)
        self.STEP_STATE_JSON_FILE = os.path.join(STEP_STATE_DIR, "steps.json")
        self.STEP_U_JSON_FILE = os.path.join(STEP_STATE_DIR, "user.json")
        self.STEP_V_JSON_FILE = os.path.join(STEP_STATE_DIR, "vehicle.json")
    def save_cache(self, cache,type):
        if type=="u":
            self.write_log(self.STEP_U_JSON_FILE, cache, cache["id"])
        elif type=="v":
            self.write_log(self.STEP_V_JSON_FILE, cache, cache["id"])
        elif type=="step":
            self.write_log(self.STEP_STATE_JSON_FILE, cache, cache["step"])
    def write_log(self,file,new_cache,index):
        if os.path.exists(file):
            with open(file, 'r') as f:
                all_steps_cache = json.load(f)
        else:
            all_steps_cache = {}
        all_steps_cache[int(index)] = new_cache
        with open(file, 'w') as f:
            json.dump(all_steps_cache, f,ensure_ascii=False,cls=SingleLineKeyJSONEncoder)
    def load_cache(self):
        cache = {}
        if os.path.exists(self.STEP_STATE_JSON_FILE):
            with open(self.STEP_STATE_JSON_FILE, 'r') as f:
                cache = json.load(f)
        if not self.step_states:  # 检查是否为空
            for key, value in cache.items():
                self.step_states[int(key)] = value  # 将 cache 中的内容加载到 step_states 中
        return cache
    def get_state_text(self,u):
        id2state = {
            0: "searching for available vehicles",
            1: "assigned, waiting for pickup at origin",
            2: "picked up, waiting for arrival at destination",
            3: "dropped off and finished"
        }
        if u.finish_dropoff:
            return id2state[3]
        elif u.finish_pickup:
            return id2state[2]
        elif u.finish_assign:
            return id2state[1]
        else:
            return id2state[0]
    def get_state(self,u):
        if u.finish_dropoff:
            return self.req_id2state[3]
        elif u.finish_pickup:
            return self.req_id2state[2]
        elif u.finish_assign:
            return self.req_id2state[1]
        else:
            return self.req_id2state[0]
    def log_pathed(self,control_center,u_i,v): # if multi u assigned to same v, becuase of u key, it won't be overwritten
        state = self.get_state(u_i)
        if v.id not in self.V_pathed_after_assigned:
            self.V_pathed_after_assigned[v.id] = defaultdict(list)
            self.V_pathed_after_assigned[v.id][u_i.id] = [data_process.map_npTuple(v.current_position)]
        else:
            if state != "dropped off" and state != "waiting":
                self.V_pathed_after_assigned[v.id][u_i.id].append(data_process.map_npTuple(v.current_position))


    def log_init_scan(self,control_center): # expand detail with before decision
        pass
    def log_requests(self):
        pass
    def log_vehicles(self):
        pass
    def log_steps_state(self,step, Uinfo, Vinfo, U2MultiV, V2MultiU):
        self.step_states[step]["step"] = step
        self.step_states[step]["Uinfo"] = Uinfo
        self.step_states[step]["Vinfo"] = Vinfo
        self.step_states[step]["U2MultiV"] = U2MultiV
        self.step_states[step]["V2MultiU"] = V2MultiU
    def log_steps_decision(self,step, decision):
        self.step_states[step]["decision"] = decision
        self.save_cache(self.step_states[step],"step")

    def log_BeforeDemandNeedDecision(self,control_center,U2MultiV,V2MultiU):
        U2MultiV_to_decide = {}
        V2MultiU_to_decide = {}
        for u in U2MultiV.keys():
            if len(U2MultiV[u]) > 0:
                print("u: ",u, "is scanned by vehicles:",U2MultiV[u])
                U2MultiV_to_decide[u] = len(U2MultiV[u])
            else:
                print("u: ",u, "is NOT scanned by any vehicle")
        for v in V2MultiU.keys():
            if len(V2MultiU[v]) > 1:
                print("v: ",v, "has scanned requests:",V2MultiU[v])
                V2MultiU_to_decide[v] = len(V2MultiU[v])

        if len(U2MultiV_to_decide) < 1 :
            print(f"!!!NO TRIP FEASIBLE!!! CUR REQUESTS: {len(control_center.requests_step)}")
            self.empty_decision[control_center.step] = len(control_center.requests_step)

    def log_pooling(self,control_center, v, u_id):   # TODO POOLed log to generate complex decision situation
        assigned_req_num_by_car = len(v.current_requests) + len(v.next_requests)
        v_cur_reqs = []
        v_next_reqs = []
        u_id_in_v = False
        for req in v.current_requests:
            if int(req.id) != u_id:
                v_cur_reqs.append(int(req.id))
            else:
                u_id_in_v = True
        for req in v.next_requests:
            if int(req.id) != u_id:
                v_next_reqs.append(int(req.id))
            else:
                u_id_in_v = True
        excluded_req_num = len(v_cur_reqs) + len(v_next_reqs)

        count_num = assigned_req_num_by_car - excluded_req_num
        if  u_id_in_v and assigned_req_num_by_car==2:  # u_id assigened to v, and v has another request
            print("***ALREADY POOLed***")
            if len(v_cur_reqs) > 0:
                print(f"\tCurrent requests: {v_cur_reqs}")
            if len(v_next_reqs) > 0:
                print(f"\tNext requests: {v_next_reqs}")
            return True
        if assigned_req_num_by_car == 1 and u_id_in_v:  # u_id assigened to v, no other request
            print("***FINDING POOL***")
            if len(v_cur_reqs) > 0:
                print(f"\tCurrent requests: {v_cur_reqs}")
            if len(v_next_reqs) > 0:
                print(f"\tNext requests: {v_next_reqs}")
            return False
        if u_id_in_v == False:  # u_id not assigned to v
            print("***SOLO***")
            if len(v_cur_reqs) > 0:
                print(f"\tCurrent requests: {v_cur_reqs}")
            if len(v_next_reqs) > 0:
                print(f"\tNext requests: {v_next_reqs}")
            print(f"\tAssigned requests num: {assigned_req_num_by_car}")
            return False
    def log_multi_trips(self,control_center, uv_decision_pair, UV2trip_id,id_to_trip):
        print(f"??????\tChooseTripsbyPairs\tuv pair {uv_decision_pair} has more trips: ")
        v = control_center.vehicles_all[uv_decision_pair[1]]
        self.log_pooling(control_center, v, -1)
        for trip_id in UV2trip_id[uv_decision_pair]:
            tem_req_ids = [int(req.id) for req in id_to_trip[trip_id].requests]
            print(f"trip_id: {trip_id}, requests: {tem_req_ids}")
        print("??????")

    def flow_track(self,control_center):
        print("===============================================================")
        print(f"STEP {control_center.step}, num cumulated requests: {len(control_center.cur_step_states['requests_step_dict'])}")
        print("===============================================================")
        for u_id, u_i in control_center.cur_step_states["requests_step_dict"].items():
            state = self.get_state(u_i)
            print(f"_______________FOR U_ID {u_id} ____STATE : {state} ")
            self.step_u[u_id]["id"] = u_id
            if state == "waiting" :
                if "waiting_step" not in self.step_u[u_id]:
                    self.step_u[u_id]["waiting_step"] = control_center.step
            if state == "assigned":
                if "assigned_step" not in self.step_u[u_id]:
                    self.step_u[u_id]["assigned_step"] = control_center.step
            if state == "picked up":
                if "picked_step" not in self.step_u[u_id]:
                    self.step_u[u_id]["picked_step"] = control_center.step
            if state == "dropped off":
                if "dropped_step" not in self.step_u[u_id]:
                    self.step_u[u_id]["dropped_step"] = control_center.step
                    self.step_u[u_id] = data_process.merge_dicts( self.step_u[u_id],  self.u2dict(u_i))
                    self.save_cache(self.step_u[u_id],"u")

            if state != "waiting" and state != "dropped off":
                if u_i.vehicle_id is not None:
                    v = control_center.vehicles_all[u_i.vehicle_id] #
                    v.id = int(v.id)
                    self.log_pathed(control_center, u_i, v)
                    print(f"Assigned Vehicle {int(v.id)} gone {len(self.V_pathed_after_assigned[v.id][u_i.id])} step",)
                    self.log_pooling(control_center, v, u_id)
                else:
                    print("Not waiting but No vehicle assigned")

    def u2dict(self,u):

            return {
                'pickup_position': u.pickup_position,
                'dropoff_position': u.dropoff_position,
                'send_request_timepoint': u.send_request_timepoint,
                # 'assign_timepoint': u.assign_timepoint,
                # 'pickup_timepoint': u.pickup_timepoint,
                # 'dropoff_timepoint': u.dropoff_timepoint,
                'vehicle_id': int(u.vehicle_id),
                'pickup_grid_id': u.pickup_grid_id,
                'dropoff_grid_id': u.dropoff_grid_id,
            }
    def v2dict(self,v):
        return {
            "id":int(v.id)
        }

    def format_json(self,obj):
        json_str = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
        json_str = json_str[1:-1]
        pairs = json_str.split(',')
        formatted_pairs = [f"{pair}\n" for pair in pairs]
        return "{\n" + "".join(formatted_pairs) + "}"
    def track_assigned_request(self,requests_dict,vehicles):
        for request in requests_dict.values():
            if request.vehicle_id is not None:
                vehicle = vehicles[request.assigned_vehicle_id]
                self.set_track(vehicle)

    def set_track(self, vehicle):
        if not self.has_tracked(vehicle):
            self.track_vehicle_dict[vehicle.id] = vehicle
            if self.pooled_id is None:
                self.pooled_id = vehicle.id
    def delete_track(self, vehicle):
        if self.has_tracked(vehicle):
            del self.track_vehicle_dict[vehicle.id]
            if self.pooled_id == vehicle.id:
                self.pooled_id = None

    def remove_duplicated_reuqest(self,requests):
        req_id_set = set()
        for req in requests:
            if req.id in req_id_set:
                print(f'the request {req.id} is repeated in the requests')
            else:
                req_id_set.add(req.id)
    def fill_step_requests_id(self,requests_step,step=None):

        repeated_reqs = {}
        # repeated_req is all identical? Yes
        # for req in requests_step:
        #     if req.id in repeated_reqs:
        #         if req == repeated_reqs[req.id] or req.pickup_position == repeated_reqs[req.id].pickup_position:
        #             print(f'the request {req.id} is repeated in the step requests')
        #     else:
        #         repeated_reqs[req.id] = req
        # return
        self.step_requests_id = []
        for req in requests_step:
            self.step_requests_id.append(req.id)
        # check duplicated request id
        if step is  None:
            step=0
        if len(self.step_requests_id) != len(set(self.step_requests_id)):
            logging.info('%d request ids %s',step, self.step_requests_id)
            # duplicated_req_id = []
            # for req in self.step_requests_id:
            #     if self.step_requests_id.count(req) > 1:
            #         duplicated_req_id.append(req)


    def set_stage_state(self, vehicles, trips,stage,):
        pass

    # visual vehicle has scaned requests but failed to match feasible trips, providing the failure and success position map
    def compare_scan_feasible(self,requests_for_each_vehicle,vehicles_all,feasible_trips):
        if not TESTING:
            return
        failed_num = 0
        for scaned_reqs, trips,v in zip(requests_for_each_vehicle, feasible_trips,vehicles_all):
            if   len(scaned_reqs)  >= 1 and len(trips) <= 1:
                failed_num += 1
                self.fail_feasible.append((v,scaned_reqs))

                # print(f'the vehicle {v.id} has {len(scaned_reqs)} requests and has failed to match feasible trips')
            self.check_pooled_vehicle(v, trips)
        # print(f' the number of vehicles that failed to match feasible trips is {failed_num}')

    def check_repeated_req(self,final_trips, final_paths):
        req_id_set= set()
        for trip, path in zip(final_trips, final_paths):
            for req in trip.requests:
                if req.id in req_id_set:
                    print(f'the request {req.id} is repeated in the final trips')
                    #save the repeated request into a text file

                else:
                    req_id_set.add(req.id)
        # print(f' the number of STEP requests is {len(self.step_requests_id)}')
    # visual vehicle has feasible trips but failed to match final trips, providing the failure and success position map
    def compare_feasible_final(self,final_trips,vehicles_all,scored_feasible_trips):
        if not TESTING:
            return
        for trip, scored_trips, v in zip(final_trips, scored_feasible_trips,vehicles_all):
            reqs_assigned_vehicle = len(v.current_requests) + len(v.next_requests)
            if reqs_assigned_vehicle > 0 and len(scored_trips) < 1:
                print(f' the vehicle {v.id} has assigned {len(trip.requests)} requests but failed a scanned request')

            if len(scored_trips) > 1 and len(trip.requests) < 1:

                print(f' the vehicle {v.id} has {len(scored_trips)} requests but failed to match a final trip')

    # def check_stages_diff(self, vehicle):

    def has_tracked(self, vehicle):
        return vehicle.id in self.track_vehicle_dict
    def get_tracked(self):
        return self.track_vehicle_dict[self.pooled_id]
        # if len(self.solo_id) > 0:
        #     return self.track_vehicle_dict[self.solo_id[0]]
        # else:
        #     self.solo_id.append(list(self.track_vehicle_dict.keys())[0])
    def check_pooled_vehicle(self, chosen_v, trips):
        if (len(chosen_v.current_requests) + len(chosen_v.next_requests)) > 1 or len(trips) > 2:
            print(f'the vehicle {chosen_v.id} has {len(trips)} requests ')
            self.set_track(chosen_v)
        elif (len(chosen_v.current_requests) + len(chosen_v.next_requests)) == 0:
            self.delete_track(chosen_v)
    def check_init_match_process(self, trips, vehicles):
        pass
    def check_feasible_match_process(self, trips, vehicles):
        pass
    def get_v_of_multi_reqs(self, trips, vehicles):
        if not TESTING:
            return

        pooled_vehicles = []
        for index, chosen_v in enumerate(vehicles):
            if ( len(chosen_v.current_requests) + len(chosen_v.next_requests) ) > 1:

                pooled_trips=trips[index]

                print(f'the vehicle {chosen_v.id} has {len(pooled_trips)} requests ')
                self.track_vehicle_dict[chosen_v.id] = chosen_v
        return pooled_vehicles

    def draw_pooled_vehicle(self,control_center, img_path,step,img_cnt):
        if not TESTING:
            return
        if self.pooled_id is not None:
            print(f'{step} DRAWING the pooled vehicle {self.pooled_id}')
            fig_aspect_ratio = control_center.FigAspectRatio()
            fig = plt.figure(figsize=(15/fig_aspect_ratio*1.2,15), dpi=100)
            ax = fig.add_subplot(111)
            axis_lim = copy.deepcopy(control_center.environment.area_box)
            axis_lim[2] -= 0.01
            control_center.post_process_system.cmap = 'RdYlGn'
            control_center.post_process_system.legend_loc = (0.08, 1.01)

            ax = control_center.DrawPooledSnapshot(ax,self.track_vehicle_dict[self.pooled_id], v_size = 0.004, s = 100, draw_route = True, draw_road_network = True, speed_lim = [5,10], axis_lim = axis_lim)
            plt.subplots_adjust(left=0.15, right=0.95)
            plt.savefig(os.path.join(img_path, str(img_cnt).zfill(6) + '.png'))
            plt.close('all')
        return img_cnt+1