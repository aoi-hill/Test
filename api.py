    def config(self, **kwargs):
        f = open(runConfig["inputFlowConfig"])
        inputFlowConfig = json.load(f)
            
        for key,val in kwargs.items():
            if val!=None:
                inputFlowConfig[key]=val
                
        write_dict_to_file(inputFlowConfig, runConfig["finalFlowConfig"])
        return 

=========================================================================================================================================================

import asyncio
import uuid
import logging
from typing import List, Dict, Any
import fastapi
# from fastapi import FastAPI, BackgroundTasks, Request
from flask import Flask, request, jsonify
import uvicorn
import aiohttp
import json
import functools
import time
from prefect import flow, task
import requests
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process, Queue
from abc import ABC, abstractmethod
import logging
from prefect import task, flow
import yaml 
import functools, time
import httpx
import subprocess
import re

import os, sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))

# Add project_root to sys.path
if project_root not in sys.path:
    sys.path.append(project_root)

print(sys.path)

from orchestrator.factory.orchestratorFactory import *
        
@app.route('/data/<name>', methods=["POST"]) # ? change this in JATI
def executeJob(name):
        prefectLogger.info("Inside ",name," Function")
        input = request.get_json()
        ret = "Job "+name+" executed successfully"
        return {"message": ret}

#=========================================================================================================================
from flask import Flask, render_template, request, jsonify
import json

currentOrchestrator = None

readRunConfigFile = json.load(open(runConfigFilePath))

@app.route('/runConfig', methods=['GET', 'POST'])
def runConfigForm():
    data = readRunConfigFile
    
    if request.method == 'POST':
        updatedData = {}
        for key in data.keys():
            value = request.form.get(key)
            updatedData[key] = value if value else data[key]
        
        return jsonify(updatedData)

    # Generate HTML dynamically
    form_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Run Configuration</title>
        <style>
            input[type="text"] {
                width: 900px; /* Increase the width */
                padding: 5px;
                margin: 5px 0;
            }
            button {
                padding: 10px 15px;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <h2>Edit Run Configuration</h2>
        <form method="post">
    """

    for key, value in data.items():
        value_str = "" if value is None else str(value)
        form_html += f"""
            <label>{key}:</label>
            <input type="text" name="{key}" value="{value_str}" style="width: 1050px;"><br>
        """

    form_html += """
            <button type="submit">Update</button>
        </form>
    </body>
    </html>
    """

    return form_html 

@app.route('/flowConfig', methods=['GET', 'POST'])
def flowConfigForm():
    
    data = json.load(open(readRunConfigFile["inputFlowConfig"]))
    if request.method == 'POST':
        updatedData = {}
        for key in data.keys():
            value = request.form.get(key)
            updatedData[key] = value if value else data[key]
            
        currentOrchestrator.config(**updatedData) 
        return jsonify(updatedData)
   
    # Generate HTML dynamically
    form_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Run Configuration</title>
        <style>
            input[type="text"] {
                width: 600px; /* Increase the width */
                padding: 5px;
                margin: 5px 0;
            }
            button {
                padding: 10px 15px;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <h2>Edit Run Configuration</h2>
        <form method="post">
    """

    for key, value in data.items():
        value_str = "" if value is None else str(value)
        form_html += f"""
            <label>{key}:</label>
            <input type="text" name="{key}" value="{value_str}" style="width: 1050px;"><br>
        """

    form_html += """
            <button type="submit">Update</button>
        </form>
    </body>
    </html>
    """

    return form_html 

@app.route('/deploy', methods=['GET'])
def deployAPI():
    prefectLogger.info("Starting Only Deploy mode")
    currentOrchestrator.deploy()
    return style_response("DEPLOYMENT DONE")

@app.route('/oldRun', methods=['GET'])
def oldRunAPI():
    prefectLogger.info("Starting Run Pre-deployed flow mode")    
    currentOrchestrator.run()
    return style_response("PREVIOUSLY DEPLOYED FLOW HAS RAN")

@app.route('/newRun', methods=['GET'])
def newRunAPI():
    prefectLogger.info("Starting New Run mode")
    currentOrchestrator.deploy()
    currentOrchestrator.run()
    return style_response("NEWLY DEPLOYED FLOW HAS RAN")

def style_response(message, error=False):
    color = "red" if error else "green"
    styled_html = f"""
    <html>
        <head>
            <title>Flow Status</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    background-color: #f4f4f4;
                }}
                .message {{
                    font-size: 24px;
                    color: {color};
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="message">{message}</div>
        </body>
    </html>
    """
    return render_template_string(styled_html)

# Write specific post-check functions which can be directly called

# Hook Block in JATI will contain list of hooks which are dictionary with keys same as in payload along with the status decorator string

from prefect import task, flow, get_run_logger
from prefect.client import get_client
from prefect.runtime import task_run as task_run_context
from prefect.cache_policies import DEFAULT
from prefect.context import TaskRunContext

'''
careful on hitl, runs when retry = max_retry+1, so if not fail it will not run or will run if max_retires = 0
'''

'''
2 types of parameters, one from JATI and one from flow
Currently assuming the flow runtime parameters (results) will be passed as dictionary, do with that what you will
I need to combine parameters from the JATI and the flow, do this in task 
Only deal with kwargs no args, for simplicity
Hence, keep all calls/structure as payloads, this generalises the function call
make a decisinon on how to pass the flow results between tasks ?

Logger

Seperate Deployment and Run, Order of execution will be config -> deploy -> run (deployment_ID)

Instead of Returning Status (custom), how about keeping the status in the return dictionary along with result
Possible Status: failure, success, failureButContinue ....

Prefect Resolves tasks futures automatically when passed into another task 
'''
# Only below parameters are configuable for flow

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Job Orchestration System")
    parser.add_argument("--mode", choices=["server","newRun","oldRun","onlyDeploy"], required=True, help="Run in appropriate mode")
    parser.add_argument("--orchestrator", choices=["prefect","airflow","dagster"], required=True, help="Run chosen orchestrator")
    args = parser.parse_args()
    
    currentOrchestrator = orchestratorFactory().getInstance(args.orchestrator)
    
    if args.mode == "server":
        prefectLogger.info("Starting Server")
        app.run(debug=True, host="localhost", port=8000)
        
    #     app1.run(debug=True)
    # elif args.mode == "newRun":
    #     prefectLogger.info("Starting New Run mode")
    #     myOrchestrator.deploy()
    #     myOrchestrator.config(flowConfig)
    #     myOrchestrator.run()
        
    # elif args.mode == "oldRun":
    #     prefectLogger.info("Starting Run Pre-deployed flow mode")
    #     myOrchestrator.config(flowConfig)
    #     myOrchestrator.run()
    
    # elif args.mode == "onlyDeploy":
    #     prefectLogger.info("Starting Only Deploy mode")
    #     myOrchestrator.deploy()
        

'''
make modular
Change json, continue, failure, failureButContinue - Done
no hardcoding - Done
Remove prefectLogger.info, use logs  - Done
Make Factory - Done

Can preBlock add values to pass to algo or just checker, no change to core logic (payload)???
file output log path for handler i cannot put in config, as i need to set up the logger before reading config ????? - changed ot but is it correct
'''    
 
================================================================================================================

import asyncio
import uuid
import logging
from typing import List, Dict, Any
import fastapi
# from fastapi import FastAPI, BackgroundTasks, Request
from flask import Flask, request, jsonify
import uvicorn
import aiohttp
import json
import functools
import time
from prefect import flow, task
import requests
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process, Queue
from abc import ABC, abstractmethod
import logging
from prefect import task, flow
import yaml 
import functools, time
import httpx
import subprocess
import re
from fastapi import FastAPI, Form, Request, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os, sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))

# Add project_root to sys.path
if project_root not in sys.path:
    sys.path.append(project_root)

print(sys.path)

from orchestrator.factory.orchestratorFactory import *

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class JobInput(BaseModel):
    data: Dict[str, Any] = {}

@app.post("/data/{name}")
async def execute_job(name: str, input_data: JobInput = Body(...)):
    prefectLogger.info(f"Inside {name} Function")
    input_json = input_data.data
    ret = f"Job {name} executed successfully"
    return {"message": ret}
#=========================================================================================================================
currentOrchestrator = None
readRunConfigFile = json.load(open(runConfigFilePath))
updatedRunConfig = None

# Create a class for the form data
class flowConfigData:
    def __init__(self, data: Dict):
        self.data = data

    async def update_config(self, form_data: Dict):
        updated_data = {}
        for key in self.data.keys():
            value = form_data.get(key)
            updated_data[key] = value if value else self.data[key]
        
        # Assuming currentOrchestrator is a global object in your original code
        currentOrchestrator.config(**updated_data)
        return updated_data

# Create a class for the form data
class runConfigData:
    def __init__(self, data: Dict):
        self.data = data

    async def update_config(self, form_data: Dict):
        updated_data = {}
        for key in self.data.keys():
            value = form_data.get(key)
            updated_data[key] = value if value else self.data[key]
        
        return updated_data
    
@app.get("/runConfig", response_class=HTMLResponse)
async def runConfigFormGet():
    # Load the configuration data
    data = readRunConfigFile
    
    # Generate HTML dynamically
    form_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Run Configuration</title>
        <style>
            input[type="text"] {
                width: 600px;
                padding: 5px;
                margin: 5px 0;
            }
            button {
                padding: 10px 15px;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <h2>Edit Run Configuration</h2>
        <form method="post">
    """

    for key, value in data.items():
        value_str = "" if value is None else str(value)
        form_html += f"""
            <label>{key}:</label>
            <input type="text" name="{key}" value="{value_str}" style="width: 1050px;"><br>
        """

    form_html += """
            <button type="submit">Update</button>
        </form>
    </body>
    </html>
    """

    return form_html

@app.post("/runConfig", response_class=JSONResponse)
async def runConfigFormPost(request: Request):
    # Load the configuration data
    data = readRunConfigFile
    
    # Create a config handler
    config_handler = runConfigData(data)
    
    # Get form data
    form_data = await request.form()
    form_dict = dict(form_data)
    
    # Update configuration
    updated_data = await config_handler.update_config(form_dict)
    global updatedRunConfig
    updatedRunConfig = updated_data
    return JSONResponse(content=updated_data)

@app.get("/flowConfig", response_class=HTMLResponse)
async def flowConfigFormGet():
    # Load the configuration data
    data = json.load(open(readRunConfigFile["inputFlowConfig"]))
    
    # Generate HTML dynamically
    form_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Run Configuration</title>
        <style>
            input[type="text"] {
                width: 600px;
                padding: 5px;
                margin: 5px 0;
            }
            button {
                padding: 10px 15px;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <h2>Edit Run Configuration</h2>
        <form method="post">
    """

    for key, value in data.items():
        value_str = "" if value is None else str(value)
        form_html += f"""
            <label>{key}:</label>
            <input type="text" name="{key}" value="{value_str}" style="width: 1050px;"><br>
        """

    form_html += """
            <button type="submit">Update</button>
        </form>
    </body>
    </html>
    """

    return form_html

@app.post("/flowConfig", response_class=JSONResponse)
async def flowConfigFormPost(request: Request):
    # Load the configuration data
    data = json.load(open(readRunConfigFile["inputFlowConfig"]))
    
    # Create a config handler
    config_handler = flowConfigData(data)
    
    # Get form data
    form_data = await request.form()
    form_dict = dict(form_data)
    
    # Update configuration
    updated_data = await config_handler.update_config(form_dict)
    
    return JSONResponse(content=updated_data)

def styleResponse(message, error=False):
    """Helper function to create styled HTML responses"""
    color = "red" if error else "green"
    styled_html = f"""
    <html>
        <head>
            <title>Flow Status</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    background-color: #f4f4f4;
                }}
                .message {{
                    font-size: 24px;
                    color: {color};
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="message">{message}</div>
        </body>
    </html>
    """
    return HTMLResponse(content=styled_html)

@app.get("/deploy", response_class=HTMLResponse)
async def deployApi():
    """Endpoint to deploy the flow"""
    prefectLogger.info("Starting Only Deploy mode")
    await asyncio.to_thread(currentOrchestrator.deploy, name = updatedRunConfig["deploymentName"], workPoolName = updatedRunConfig["poolName"])
    return styleResponse("DEPLOYMENT DONE")

@app.get("/oldRun", response_class=HTMLResponse)
async def oldRunApi():
    """Endpoint to run a pre-deployed flow"""
    prefectLogger.info("Starting Run Pre-deployed flow mode")    
    await asyncio.to_thread(currentOrchestrator.run, deploymentName=updatedRunConfig["deploymentName"])
    return styleResponse("PREVIOUSLY DEPLOYED FLOW HAS RAN")

@app.get("/newRun", response_class=HTMLResponse)
async def newRunApi():
    """Endpoint to deploy and then run a flow"""
    prefectLogger.info("Starting New Run mode")
    await asyncio.to_thread(currentOrchestrator.deploy, name = updatedRunConfig["deploymentName"], workPoolName = updatedRunConfig["poolName"])
    await asyncio.to_thread(currentOrchestrator.run, deploymentName=updatedRunConfig["deploymentName"])
    return styleResponse("NEWLY DEPLOYED FLOW HAS RAN")

@app.get("/", response_class=HTMLResponse)
async def getApiLst():        
    api_list = {
        "See and Modify Run Configuration": "/runConfig",
        "See and Modify Flow Configuration": "/flowConfig",
        "Deploy a Flow": "/deploy",
        "Run an Existing Flow Deployment": "/oldRun",
        "Deploy and Run a Flow": "/newRun",
    }

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API List</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                text-align: center;
                padding: 20px;
            }
            .container {
                max-width: 600px;
                margin: auto;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #333;
            }
            ul {
                list-style: none;
                padding: 0;
            }
            li {
                background: #007bff;
                color: white;
                margin: 10px 0;
                padding: 10px;
                border-radius: 5px;
                font-size: 18px;
            }
            a {
                color: white;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Available API Endpoints</h1>
            <ul>
    """

    # Dynamically generate the API list in HTML format
    for desc, url in api_list.items():
        html_content += f'<li><a href="{url}">{desc}</a></li>'

    html_content += """
            </ul>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)
# Write specific post-check functions which can be directly called

# Hook Block in JATI will contain list of hooks which are dictionary with keys same as in payload along with the status decorator string

from prefect import task, flow, get_run_logger
from prefect.client import get_client
from prefect.runtime import task_run as task_run_context
from prefect.cache_policies import DEFAULT
from prefect.context import TaskRunContext

'''
careful on hitl, runs when retry = max_retry+1, so if not fail it will not run or will run if max_retires = 0
'''

'''
2 types of parameters, one from JATI and one from flow
Currently assuming the flow runtime parameters (results) will be passed as dictionary, do with that what you will
I need to combine parameters from the JATI and the flow, do this in task 
Only deal with kwargs no args, for simplicity
Hence, keep all calls/structure as payloads, this generalises the function call
make a decisinon on how to pass the flow results between tasks ?

Logger

Seperate Deployment and Run, Order of execution will be config -> deploy -> run (deployment_ID)

Instead of Returning Status (custom), how about keeping the status in the return dictionary along with result
Possible Status: failure, success, failureButContinue ....

Prefect Resolves tasks futures automatically when passed into another task 
'''
# Only below parameters are configuable for flow

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Job Orchestration System")
    # parser.add_argument("--mode", choices=["server","newRun","oldRun","onlyDeploy"], required=True, help="Run in appropriate mode")
    parser.add_argument("--mode", choices=["fastApi","flask"], required=True, help="Run in appropriate mode")
    parser.add_argument("--orchestrator", choices=["prefect","airflow","dagster"], required=True, help="Run chosen orchestrator")
    args = parser.parse_args()
    
    currentOrchestrator = orchestratorFactory().getInstance(args.orchestrator)
    
    if args.mode == "fastApi":
        prefectLogger.info("Starting Fast Api Server")
        uvicorn.run(app, host="localhost", port=8000, log_level="info")
    elif args.mode == "flask":
        app1.run(debug=True, host="localhost", port=8001)
        
    #     app1.run(debug=True)
    # elif args.mode == "newRun":
    #     prefectLogger.info("Starting New Run mode")
    #     myOrchestrator.deploy()
    #     myOrchestrator.config(flowConfig)
    #     myOrchestrator.run()
        
    # elif args.mode == "oldRun":
    #     prefectLogger.info("Starting Run Pre-deployed flow mode")
    #     myOrchestrator.config(flowConfig)
    #     myOrchestrator.run()
    
    # elif args.mode == "onlyDeploy":
    #     prefectLogger.info("Starting Only Deploy mode")
    #     myOrchestrator.deploy()
        

'''
make modular
Change json, continue, failure, failureButContinue - Done
no hardcoding - Done
Remove prefectLogger.info, use logs  - Done
Make Factory - Done

Can preBlock add values to pass to algo or just checker, no change to core logic (payload)???
file output log path for handler i cannot put in config, as i need to set up the logger before reading config ????? - changed ot but is it correct
'''    
 
=============================================================
from prefect import flow, task
import sys
import os
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



def getConfig(key):
    fileConfigDict = read_dict_from_file(runConfig["finalFlowConfig"])
    return fileConfigDict[key]

class prefectOrchestrator(Orchestrator, AutoDecorate):
    
    def __init__(self):
        self._processGraph = {}
        self.flowName="callFlow"
        # Only below parameters are configuable for flow
        self.flowConfig = {
            "flow_run_name":"XYZ",
            "retries":PREFECT_FLOW_DEFAULT_RETRIES.value(),
            "retry_delay_seconds":PREFECT_FLOW_DEFAULT_RETRY_DELAY_SECONDS.value(),
            "validate_parameters":True,
            "timeout_seconds":3700
        }
    
    def _postOrder(self, curNodeGID:int, graphWeight:int):
        curNode = self._processGraph[curNodeGID]
        
        dependencyNodes = []
        ind=0
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
        
        curJob = parseJob(job)
        
        self._processGraph[curJob.gid] = prefectNode(curJob)
        for activity in curJob.activities:
            self._processGraph[activity.gid] = prefectNode(activity)
            for task in activity.tasks:
                self._processGraph[task.gid] = prefectNode(task)
                for instruction in task.instructions:
                    self._processGraph[instruction.gid] = prefectNode(instruction)
        
        #Post order traversal of graph, loop over paths
        graphWeight = 1
        while(True and graphWeight<=curJob.maxGraphWeight):
            try:
                self._postOrder(curNodeGID=1,graphWeight=graphWeight).result() #Returns task future of the Job Node, Edge weight (which subgraph) is manually passed for now
                break
            except Exception as e:
                prefectLogger.info("Graph Failed using Path No. %s",graphWeight)
                prefectLogger.info(e)
                graphWeight+=1
                
        if(graphWeight>curJob.maxGraphWeight):
            raise Exception("All Paths Failed")
        
        dummyTask.submit()
        return
    
    def config(self, **kwargs):
        f = open(runConfig["inputFlowConfig"])
        inputFlowConfig = json.load(f)
            
        for key,val in kwargs.items():
            if val!=None:
                inputFlowConfig[key]=val
        self.flowConfig = inputFlowConfig
        write_dict_to_file(inputFlowConfig, runConfig["finalFlowConfig"])
        return 
    
    #Seperate Graph creation and run
    def deploy(self, name = runConfig["deploymentName"], workPoolName = runConfig["poolName"]):
        
        print(runConfig,"################")
        
        callFlow.from_source(
                source=str(Path(__file__).parent),  # code stored in local directory
                entrypoint="prefectOrchestrator.py:callFlow",
            ).deploy(
                name = name,
                work_pool_name = workPoolName
            )
        return

    def run(self, filename=runConfig["jatiPath"], deploymentName = runConfig["deploymentName"]):
        f = open(filename)
        sample_job = json.load(f)
        
        params = {}
        params["job"] = sample_job
        callName = self.flowName+"/"+deploymentName
        print(callName, "====================================================================================================================== 1111")
        run_deployment(
            name=callName,
            parameters=params
        )
        return

def write_dict_to_file(dictionary, filename):
    f = open(filename,'w')
    json.dump(dictionary, f, indent=4,default=custom_serializer)
    return

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

@flow(flow_run_name=getConfig("flow_run_name"), retries=getConfig("retries"), retry_delay_seconds=getConfig("retry_delay_seconds"), validate_parameters=getConfig("validate_parameters"), timeout_seconds=getConfig("timeout_seconds"))
@Observability.log
def callFlow(job):
    myFlow = prefectOrchestrator()
    result = myFlow.process(job)
    return result
