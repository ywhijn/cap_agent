# u3621353
#Ywh=12171119

step=6
step_requests_id = [1,2,3,4,5,6,6,3,12,13,14,15,16]
duplicated_req_id = []
for req in step_requests_id:
    if step_requests_id.count(req) > 1:
        duplicated_req_id.append(req)

print(f'the duplicated request ids are {duplicated_req_id}')
#
