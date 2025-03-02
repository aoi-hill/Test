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
 
