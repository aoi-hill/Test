import requests, json

# url = "http://localhost:8000/oldRun"
# headers = {"Content-Type": "application/json"}
# data = {"flow_run_name": "xyz", "retries": 1, 
#         "jati": json.load(open("D:/Mahesh_Sir/sensothon-sep2024/sensothon-sep2024-noorjahabhanu.m-main-patch-81334/job_execution/orchestratorV1/Job/jati.json")),
#         "deploymentName":"test31",
#         "poolName":"processPool1"
# }

# url = "http://localhost:8000/newRun"
# headers = {"Content-Type": "application/json"}
# data = {"flow_run_name": "xyz1", "retries": 1, 
#         "jati": json.load(open("D:/Mahesh_Sir/sensothon-sep2024/sensothon-sep2024-noorjahabhanu.m-main-patch-81334/job_execution/orchestratorV1/Job/jati.json")),
#         "deploymentName":"test1"
# }

# url = "http://localhost:8000/deleteDeployment"
# headers = {"Content-Type": "application/json"}
# data = {"DeploymentID": "576746a0-53ce-4f90-8e91-dce3c5028f2e"}

# url = "http://localhost:8000/viewDeploymentJson"
# response = requests.get(url)
# print(response.json())

# url = "http://localhost:8000/apiListJson"
# response = requests.get(url)
# print(response.json().values())

# url = "http://localhost:8000/deploy"
# headers = {"Content-Type": "application/json"}
# data = {"deploymentName": "test77", "poolName": "processPool1"}

# response = requests.post(url, json=data, headers=headers)
# print(response.json())
