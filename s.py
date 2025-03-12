from prefect import flow, task
import sys
import os
from prefect import get_client
# Get the absolute path of project_root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))

# Add project_root to sys.path
if project_root not in sys.path:
    sys.path.append(project_root)
    
from orchestrator.factory.prefectCore.prefectNode import *

from pathlib import Path
from prefect.deployments import run_deployment
from prefect.settings import (
    PREFECT_FLOW_DEFAULT_RETRIES,
    PREFECT_FLOW_DEFAULT_RETRY_DELAY_SECONDS
)

'''
Main code which orchestrates the tasks/nodes to run with config, run, deploy exposed to user
'''

# flowConfig = {
#             "flow_run_name":"XYZ",
#             "retries":PREFECT_FLOW_DEFAULT_RETRIES.value(),
#             "retry_delay_seconds":PREFECT_FLOW_DEFAULT_RETRY_DELAY_SECONDS.value(),
#             "validate_parameters":True,
#             "timeout_seconds":3600
#         }

# f = open(json.load(open(runConfigFilePath))["inputFlowConfig"])
# flowConfig = json.load(f)
# flowConfig = {}
from prefect.runtime import flow_run

# def getConfig(key):
#     fileConfigDict = read_dict_from_file(runConfig["finalFlowConfig"])
#     ind = flow_run.get_parameters()["index"]
#     return fileConfigDict[ind][key]
    # global flowConfig
    # prefectLogger.info(flowConfig)
    # prefectLogger.info('#############################################2')
    # return flowConfig[key]

class prefectOrchestrator(Orchestrator, AutoDecorate):
    
    def __init__(self):
        self._processGraph = {}
        self.flowName="callFlow"
        # Only below parameters are configuable for flow
    
    def _postOrder(self, curNodeGID:int, graphWeight:int):
        curNode = self._processGraph[curNodeGID]
        
        dependencyNodes = []
        ind = 0
        if curNode._node.edges!=None:
            for i in curNode._node.edges:
                if graphWeight in curNode._node.edgeWeights[ind]:
                    dependencyNodes.append(self._postOrder(curNodeGID=i,graphWeight=graphWeight)) # TaskFuture
                ind += 1
                
        if len(dependencyNodes):
            scheduledNode = curNode._nodeBlock([node.wait() for node in dependencyNodes], wait_for=dependencyNodes, upstreamOutput=dependencyNodes)#, taskRunName=taskRunName)
        else:
            scheduledNode = curNode._nodeBlock(upstreamOutput=dependencyNodes)#, taskRunName=taskRunName)
            
        return scheduledNode
    
    
    def process(self, job):
        # Dict holding the graph
        
        flowParams = flow_run.get_parameters() # retries, retry_delay_seconds
        
        curJob = parseJob(job)
        
        self._processGraph[curJob.gid] = prefectNode(curJob)
        for activity in curJob.activities:
            self._processGraph[activity.gid] = prefectNode(activity)
            for task in activity.tasks:
                self._processGraph[task.gid] = prefectNode(task)
                for instruction in task.instructions:
                    self._processGraph[instruction.gid] = prefectNode(instruction)
        
        retryCount = int(flowParams["retries"])
        retryDelaySeconds = float(flowParams["retry_delay_seconds"])
        #Post order traversal of graph, loop over paths, retry once all paths exhausted
        graphWeight = 1
        while(retryCount>=0):
            
            exit = False
            graphWeight = 1
            while(True and graphWeight<=curJob.maxGraphWeight):
                try:
                    self._postOrder(curNodeGID=1,graphWeight=graphWeight).result() #Returns task future of the Job Node, Edge weight (which subgraph) is manually passed for now
                    exit = True
                    break
                except Exception as e:
                    prefectLogger.info("Graph Failed using Path No. %s",graphWeight)
                    prefectLogger.info(e)
                    graphWeight+=1
                    
            if(exit): break
            retryCount-=1
            if(retryCount>=0): time.sleep(retryDelaySeconds)
            
                
        if(graphWeight>curJob.maxGraphWeight and retryCount<0):
            raise Exception("All Paths Failed")
        
        dummyTask.submit()
        return
    
    # def config(self, **kwargs):
    #     f = open(runConfig["inputFlowConfig"])
    #     inputFlowConfig = json.load(f)
            
    #     for key,val in kwargs.items():
    #         if val!=None:
    #             inputFlowConfig[key]=val
    #     self.flowConfig = inputFlowConfig
    #     write_dict_to_file(inputFlowConfig, runConfig["finalFlowConfig"])
    #     return 
    
    #Seperate Graph creation and run
    async def deploy(self, name = runConfig["deploymentName"], workPoolName = runConfig["poolName"]):
        x = await callFlow.from_source(
                source=str(Path(__file__).parent),  # code stored in local directory
                entrypoint="prefectOrchestrator.py:callFlow",
            )
        
        id = await x.deploy(
                name = name,
                work_pool_name = workPoolName
            )
        
        id = str(id)
        name_ = workPoolName+"/"+name
        append_to_json_file("D:/Mahesh_Sir/sensothon-sep2024/sensothon-sep2024-noorjahabhanu.m-main-patch-81334/job_execution/OrchestratorV1/orchestrator/factory/prefectCore/deployments.json",id ,name_)
        
        return

    async def run(self, jati=runConfig["jati"], deploymentName = runConfig["deploymentName"], inputFlowConfig = None):
        
        # f = open(filename)
        # sample_job = json.load(f)
               
        params = inputFlowConfig
        params["job"] = json.loads(jati) if type(jati)!=dict else jati
        
        callName = self.flowName+"/"+deploymentName
        
        await run_deployment(
            name=callName,
            parameters=params
        )
        return

    async def deleteDeployment(self, deployment_id: str):
        await get_client().delete_deployment(deployment_id)
        delete_key_from_json("D:/Mahesh_Sir/sensothon-sep2024/sensothon-sep2024-noorjahabhanu.m-main-patch-81334/job_execution/OrchestratorV1/orchestrator/factory/prefectCore/deployments.json", deployment_id)
        
def write_dict_to_file(dictionary, filename):
    f = open(filename,'w')
    json.dump(dictionary, f, indent=4,default=custom_serializer)
    return

# def append_dict_to_json_file(dictionary, filename):
#     # Check if file exists and has valid JSON
#     sz = 0
#     if os.path.exists(filename) and os.path.getsize(filename) > 0:
#         try:
#             with open(filename, 'r+') as f:
#                 data = json.load(f)  # Load existing JSON data
#                 if not isinstance(data, list):  # Ensure it's a list
#                     raise ValueError("JSON file does not contain a list!")
#                 data.append(dictionary)  # Append new dictionary
#                 sz = len(data)
#                 f.seek(0)  # Move cursor to the start of the file
#                 json.dump(data, f, indent=4)  # Write back updated JSON
#                 f.truncate()  # Remove any remaining old data
#         except json.JSONDecodeError:
#             print(f"Error: {filename} contains invalid JSON.")
#     else:
#         # Create a new file with a JSON list
#         with open(filename, 'w') as f:
#             json.dump([dictionary], f, indent=4)

#     return sz-1  # Optional success flag


def append_to_json_file(filename, key, value):
    try:
        # Load existing data from the file
        with open(filename, 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is empty, initialize as an empty dict
        data = {}

    # Append the new key-value pair
    data[key] = value

    # Save the updated data back to the file
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def delete_key_from_json(filename, key):
    if not os.path.exists(filename):  # Check if file exists
        print("File not found!")
        return
    
    with open(filename, "r+") as file:
        try:
            data = json.load(file)  # Load JSON data
        except json.JSONDecodeError:
            print("Invalid JSON format!")
            return
        
        if key in data:
            del data[key]  # Delete the key-value pair
        else:
            print(f"Key '{key}' not found!")
            return

        file.seek(0)  # Move to the start of the file
        json.dump(data, file, indent=4)
        file.truncate()  # Remove any leftover content
        
def read_dict_from_file(filename):
    f = open(filename)
    x = json.load(f)
    return x

@task
def dummyTask():
    return


# This is a indirect caller of flow as class flow function path cannot be given as entrypoint in deployment
# Similarly many flow methods cannot be string, so a function call done to get the right value at runtime
# these functions get called whenever you first run code, even in server mode

## decorator is ran when called
# this is only called on run deployment not on deployment
# All flow decorator parameters are resolved 
# @flow(flow_run_name=lambda: getConfig("flow_run_name"))

#flow_run_name: Optional[Union[Callable[[], str], str]] = None , others don't take callable so will give pydantic error
@flow(flow_run_name="{flow_run_name}", timeout_seconds=10000)#lambda:getConfig("flow_run_name"))#, persist_result=lambda:getConfig("validate_parameters"))#, retry_delay_seconds=lambda:getConfig("retry_delay_seconds"))#, retries=lambda:getConfig("retries"),, timeout_seconds=lambda:getConfig("timeout_seconds"))
@Observability.log
def callFlow(job, flow_run_name, retries, retry_delay_seconds):
    myFlow = prefectOrchestrator()
    result = myFlow.process(job)
    return result

===============================================================================================================================================================

        taskMetaData = "WorkPool=>{}___DeploymentName=>{}___DeploymentID=>{}___FlowRunName=>{}___FlowName=>{}___flowRunID=>{}".format(
            EngineContext.get().flow_run.work_pool_name,
            deployment.get_name(),
            deployment.get_id(),
            EngineContext.get().flow.flow_run_name,
            flow_run_context.get_flow_name(),
            flow_run_context.get_id(),
            # EngineContext.get().flow.timeout_seconds,
            )

            thread = threading.Thread(target=thread_task, args=(hitlId, self._node.hitl, hitlInput, taskMetaData,), daemon=True)
