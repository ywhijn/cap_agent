"""
select pooled vehicle to track
each trip and path at least has an empty
"""
TESTING = False
import logging
import matplotlib.pyplot as plt
import os
import copy
logging.basicConfig(filename='duplicated_req_pos.log',
                    filemode='a',
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
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