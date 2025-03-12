import asyncio
import uuid
import logging
from typing import List, Dict, Any
import fastapi
# from fastapi import FastAPI, BackgroundTasks, Request
from flask import Flask, request, jsonify
import uvicorn
import aiohttp
from jinja2 import Template
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

f = open(readRunConfigFile["inputFlowConfig"])
inputFlowConfig = json.load(f)
    
# Create a class for the both form and run data
class configData:
    def __init__(self, data: Dict):
        self.data = data

    async def update_config(self, form_data: Dict):
        updated_data = {}
        for key in self.data.keys():
            value = form_data.get(key) if key in form_data.keys() else None
            updated_data[key] = value if value else self.data[key]
        
        return updated_data
    
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

#IMPORTANT : MAKE SURE THE TWO CONFIG FILES DON"T HAVE ANY COMMON KEY
@app.get("/deploy", response_class=HTMLResponse)
async def deployApi():
    
    global readRunConfigFile
    dataRun = readRunConfigFile

    # Generate HTML dynamically
    form_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Deploy Configuration</title>
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
        <h2>Edit Deploy Configuration</h2>
        <form method="post">
    """
    for key, value in dataRun.items():
        if key!="deploymentName" and key!="poolName":
            continue
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

@app.post("/deploy", response_class=JSONResponse)
async def deployApi(request: Request):
    """Endpoint to deploy the flow"""
    global readRunConfigFile
    dataRun = readRunConfigFile
    
    #IMPORTANT : MAKE SURE THE TWO CONFIG FILES DON"T HAVE ANY COMMON KEY
    # Create a config handler
    config_handler_run = configData(dataRun)
    
    try:
        data = await request.json()
    except Exception:
        # If JSON parsing fails, try getting form data
        form_data = await request.form()
        data = dict(form_data)
    
    # Update configuration
    updatedRunConfig = await config_handler_run.update_config(data)
    
    prefectLogger.info("Starting Only Deploy mode")
    # prefectLogger.info(updatedFlowConfig)
    # prefectLogger.info('************************************')
    
    await currentOrchestrator.deploy(name = updatedRunConfig["deploymentName"], workPoolName = updatedRunConfig["poolName"])
    
    return JSONResponse(content=data)
    # return styleResponse("DEPLOYMENT DONE")

@app.get("/oldRun", response_class=HTMLResponse)
async def oldRunApi():
    
    global inputFlowConfig, readRunConfigFile
    dataFlow = inputFlowConfig
    dataRun = readRunConfigFile
    

    form_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Run Configuration</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                padding: 20px;
                background-color: #f4f4f4;
            }
            h2 {
                text-align: center;
            }
            form {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                max-width: 900px;
                margin: auto;
            }
            label {
                font-weight: bold;
                display: block;
                margin-top: 15px;
            }
            textarea {
                width: 100%;
                height: 30px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
                resize: vertical;
            }
            button {
                display: block;
                width: 100%;
                padding: 10px;
                background: #007BFF;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 5px;
                margin-top: 20px;
                cursor: pointer;
            }
            button:hover {
                background: #0056b3;
            }
        </style>
    </head>
    <body>
        <h2>Edit Run Configuration</h2>
        <form method="post">
    """

    # Generate input fields dynamically
    for key, value in {**dataFlow}.items():
        value_str = "" if value is None else json.dumps(value) if type(value)==dict else str(value)
        form_html += f"""
            <label for="{key}">{key}:</label>
            <textarea id="{key}" name="{key}">{value_str}</textarea>
        """
    
    for key, value in {**dataRun}.items():
        if key not in ["deploymentName","poolName","jati"]: continue
        value_str = "" if value is None else json.dumps(value) if type(value)==dict else str(value)
        form_html += f"""
            <label for="{key}">{key}:</label>
            <textarea id="{key}" name="{key}">{value_str}</textarea>
        """

    # Submit button
    form_html += """
            <button type="submit">Update</button>
        </form>
    </body>
    </html>
    """
    return form_html

@app.post("/oldRun", response_class=JSONResponse)
async def oldRunApi(request: Request):
    """Endpoint to deploy the flow"""
    global inputFlowConfig, readRunConfigFile
    dataFlow = inputFlowConfig
    dataRun = readRunConfigFile
    
    #IMPORTANT : MAKE SURE THE TWO CONFIG FILES DON"T HAVE ANY COMMON KEY
    # Create a config handler
    config_handler_flow = configData(dataFlow)
    config_handler_run = configData(dataRun)
    
    try:
        data = await request.json()
    except Exception:
        # If JSON parsing fails, try getting form data
        form_data = await request.form()
        data = dict(form_data)
    
    # Update configuration
    updatedFlowConfig = await config_handler_flow.update_config(data)
    updatedRunConfig = await config_handler_run.update_config(data)
    # index = append_dict_to_json_file(updatedFlowConfig, readRunConfigFile["finalFlowConfig"])
    
    """Endpoint to run a pre-deployed flow"""
    prefectLogger.info("Starting Run Pre-deployed flow mode")    
    await currentOrchestrator.run(jati=updatedRunConfig["jati"], deploymentName=updatedRunConfig["deploymentName"], inputFlowConfig = updatedFlowConfig)
    # return styleResponse("PREVIOUSLY DEPLOYED FLOW HAS RAN")
    return JSONResponse(data)

@app.get("/newRun", response_class=HTMLResponse)
async def newRunApi():
    
    global inputFlowConfig, readRunConfigFile
    dataFlow = inputFlowConfig
    dataRun = readRunConfigFile
    

    form_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Run Configuration</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                padding: 20px;
                background-color: #f4f4f4;
            }
            h2 {
                text-align: center;
            }
            form {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                max-width: 900px;
                margin: auto;
            }
            label {
                font-weight: bold;
                display: block;
                margin-top: 15px;
            }
            textarea {
                width: 100%;
                height: 30px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
                resize: vertical;
            }
            button {
                display: block;
                width: 100%;
                padding: 10px;
                background: #007BFF;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 5px;
                margin-top: 20px;
                cursor: pointer;
            }
            button:hover {
                background: #0056b3;
            }
        </style>
    </head>
    <body>
        <h2>Edit Run Configuration</h2>
        <form method="post">
    """

    # Generate input fields dynamically
    for key, value in {**dataFlow}.items():
        value_str = "" if value is None else json.dumps(value) if type(value)==dict else str(value)
        form_html += f"""
            <label for="{key}">{key}:</label>
            <textarea id="{key}" name="{key}">{value_str}</textarea>
        """
    
    for key, value in {**dataRun}.items():
        if key not in ["deploymentName","poolName","jati"]: continue
        value_str = "" if value is None else json.dumps(value) if type(value)==dict else str(value)
        form_html += f"""
            <label for="{key}">{key}:</label>
            <textarea id="{key}" name="{key}">{value_str}</textarea>
        """

    # Submit button
    form_html += """
            <button type="submit">Update</button>
        </form>
    </body>
    </html>
    """


    return form_html

@app.post("/newRun", response_class=JSONResponse)
async def newRunApi(request: Request):
    """Endpoint to deploy the flow"""
    
    global inputFlowConfig, readRunConfigFile
    dataFlow = inputFlowConfig
    dataRun = readRunConfigFile
    
    #IMPORTANT : MAKE SURE THE TWO CONFIG FILES DON"T HAVE ANY COMMON KEY
    # Create a config handler
    config_handler_flow = configData(dataFlow)
    config_handler_run = configData(dataRun)
    
    try:
        data = await request.json()
    except Exception:
        # If JSON parsing fails, try getting form data
        form_data = await request.form()
        data = dict(form_data)
    
    # Update configuration
    updatedFlowConfig = await config_handler_flow.update_config(data)
    updatedRunConfig = await config_handler_run.update_config(data)

    # index = append_dict_to_json_file(updatedFlowConfig, readRunConfigFile["finalFlowConfig"])
    
    """Endpoint to deploy and then run a flow"""
    prefectLogger.info("Starting New Run mode")
    await currentOrchestrator.deploy(name = updatedRunConfig["deploymentName"], workPoolName = updatedRunConfig["poolName"])
    await currentOrchestrator.run(jati=updatedRunConfig["jati"], deploymentName=updatedRunConfig["deploymentName"], inputFlowConfig = updatedFlowConfig)
    # return styleResponse("NEWLY DEPLOYED FLOW HAS RAN")
    return JSONResponse(data)

@app.get("/deleteDeployment", response_class=HTMLResponse)
async def deleteDeployment():
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
        <label>Deployent ID</label>
        <input type="text" name="DeploymentID" value="" style="width: 1050px;"><br>
    """

    form_html += """
            <button type="submit">Delete</button>
        </form>
    </body>
    </html>
    """

    return form_html

@app.post("/deleteDeployment", response_class=JSONResponse)
async def deleteDeployment(request: Request):
    """Endpoint to delete Deployment"""
    
    try:
        data = await request.json()
    except Exception:
        # If JSON parsing fails, try getting form data
        form_data = await request.form()
        data = dict(form_data)

    prefectLogger.info("Starting Only Delete deployment")
    prefectLogger.info(data["DeploymentID"])
    
    await currentOrchestrator.deleteDeployment(data["DeploymentID"]) #change to ID
    
    return JSONResponse(data)
    # return styleResponse("DEPLOYMENT DELETED")

@app.get("/viewDeployments", response_class=HTMLResponse)
async def viewDeployment():
    data = json.load(open("D:/Mahesh_Sir/sensothon-sep2024/sensothon-sep2024-noorjahabhanu.m-main-patch-81334/job_execution/OrchestratorV1/orchestrator/factory/prefectCore/deployments.json"))

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dictionary Table</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 10px;
                background-color: #f4f4f4;
            }}
            h2 {{
                text-align: center;
            }}
            table {{
                width: 60%;
                margin: 20px auto;
                border-collapse: collapse;
                background: white;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }}
            th, td {{
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #007BFF;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
            form {{
                margin: 0;
                display: inline;
            }}
            button {{
                padding: 5px 10px;
                border: none;
                background-color: red;
                color: white;
                cursor: pointer;
                border-radius: 5px;
            }}
            button:hover {{
                background-color: darkred;
            }}
        </style>
    </head>
    <body>

        <h2>Dictionary Data</h2>
        <table>
            <tr>
                <th>Key</th>
                <th>Value</th>
                <th>Action</th>
            </tr>
            {''.join(f"""
                <tr>
                    <td>{key}</td>
                    <td>{value}</td>
                    <td>
                        <form action="/deleteDeployment" method="post">
                            <input type="hidden" name="DeploymentID" value="{key}">
                            <button type="submit">Delete</button>
                        </form>
                    </td>
                </tr>
            """ for key, value in data.items())}
        </table>

    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/viewDeploymentJson", response_class=JSONResponse)
async def viewDeploymentJson():
    with open("D:/Mahesh_Sir/sensothon-sep2024/sensothon-sep2024-noorjahabhanu.m-main-patch-81334/job_execution/OrchestratorV1/orchestrator/factory/prefectCore/deployments.json") as f:
        data = json.load(f)
    return JSONResponse(content=data)

@app.get("/apiList", response_class=HTMLResponse)
async def getApiLst():        
    api_list = {
        "Deploy a Flow": "/deploy",
        "Run an Existing Flow Deployment": "/oldRun",
        "Deploy and Run a Flow": "/newRun",
        "Delete a Deployment":"/deleteDeployment",
        "View Deployments":"/viewDeployments"
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

@app.get("/apiListJson", response_class=JSONResponse)
async def getApiLst():        
    api_list = {
        "Deploy a Flow": "http://localhost:8000/deploy",
        "Run an Existing Flow Deployment": "http://localhost:8000/oldRun",
        "Deploy and Run a Flow": "http://localhost:8000/newRun",
        "Delete a Deployment":"http://localhost:8000/deleteDeployment",
        "View Deployments":"http://localhost:8000/viewDeployments"
    }
    return JSONResponse(content=api_list)

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
 
