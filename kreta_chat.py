

import os
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv
import json
import requests
import datetime
from rich.console import Console

from utils.kreta import KretaUtils
from utils.date_utils import KretaDateUtils

TRACE_TOOL_CALLS = True

load_dotenv()
console = Console()

kreta_user_id = os.getenv("KRETA_USER_ID")
kreta_password = os.getenv("KRETA_USER_PASSWORD")
kreta_klik_id = os.getenv("KRETA_KLIK_ID")

kreta_utils = KretaUtils(kreta_user_id, kreta_password, kreta_klik_id)
date_utils = KretaDateUtils()

if os.getenv("SERVICE_TYPE") == "azure":
    client = AzureOpenAI(
        api_key=os.environ.get('AZURE_OPENAI_API_KEY'),  
        api_version=os.environ.get('AZURE_OPENAI_API_VERSION'), 
        azure_endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT') )
    deployment_name=os.environ.get('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME')
elif os.getenv("SERVICE_TYPE") == "openai":
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    deployment_name=os.environ.get('OPENAI_CHAT_MODEL_ID')

messages = [
    {"role": "system", 
        "content": f"""You are a helpful assistant that can helf with answering questions about the students timetable, lessons, homework, etc. The date today is {datetime.date.today()}. 
                    If the information from a function call is already available in the context, use that info instead of doing the same call again.
                    If you need to call a function, provide the correct arguments, don't make up the parameters.
                    Respond as you would in a verbal conversation. So reply with sentences as in a conversation, no formatting or markdown is needed.
                    Respond in a funny way, but always provide the correct information."""},
]

tools = [
        {
            "type": "function",
            "function": {
                "name": "get_school_year_dates",
                "description": "Get important dates of the school year",
                "parameters": { },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_grades",
                "description": "Get the grades of the student for the given week",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "The date in the week in YYYY-MM-DD format",
                        },
                    },
                    "required": ["date"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_lessons_for_week",
                "description": "Get the lessons for a week, which contains the given date",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "The date in the week in YYYY-MM-DD format",
                        },
                    },
                    "required": ["date"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_homework",
                "description": "Get the homework for a given period",
                "parameters": {
                    "type": "object",
                    "properties": {
                      "date": {
                            "type": "string",
                            "description": "The date for which to check the homework in YYYY-MM-DD format",
                        },
                    },
                    "required": ["date"],
                },
            },
    }
    ]

def trace_tool_call(tool_call, arguments, function_call_response):
    if TRACE_TOOL_CALLS:
        console.print(f"[bold blue]TOOL_CALL[/]: ", end="")
        # First 100 characters of the response with ellipsis
        response_short = str(function_call_response)[:100] + "..." if len(str(function_call_response)) > 100 else str(function_call_response)
        console.print(f"{tool_call.function.name}, arguments: {arguments}, response: {response_short}")   

while True:
    user_input = console.input("[bold green]Student:[/] ")
    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        tools=tools,
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    messages.append(response_message)

    if tool_calls:
        for tool_call in tool_calls:
            function_args = json.loads(tool_call.function.arguments) 

            if tool_call.function.name == "get_lessons_for_week":
                func_arg_date=function_args.get("date")
                start_date, end_date = date_utils.get_week_start_enddates(datetime.datetime.strptime(func_arg_date, "%Y-%m-%d").date())
                function_call_response = kreta_utils.get_lessons(start_date, end_date)    
                if (function_call_response == []):
                    function_call_response = "No lessons for this week."
                func_arguments = f"start_date: {start_date}, end_date: {end_date}"
                trace_tool_call(tool_call, func_arguments, function_call_response)

            elif tool_call.function.name == "get_homework":
                func_arg_date=function_args.get("date")
                start_date, end_date = date_utils.get_week_start_enddates(datetime.datetime.strptime(func_arg_date, "%Y-%m-%d").date())
                function_call_response = kreta_utils.get_homework(start_date, end_date)    
                if (function_call_response == []):
                    function_call_response = "No homework for this week."
                func_arguments = f"start_date: {start_date}, end_date: {end_date}"
                trace_tool_call(tool_call, func_arguments, function_call_response)
            
            elif tool_call.function.name == "get_school_year_dates":
                function_call_response = kreta_utils.get_school_year_dates()    
                if (function_call_response == []):
                    function_call_response = "No school year dates available."
                trace_tool_call(tool_call, '', function_call_response)

            elif tool_call.function.name == "get_grades":
                func_arg_date=function_args.get("date")
                start_date, end_date = date_utils.get_week_start_enddates(datetime.datetime.strptime(func_arg_date, "%Y-%m-%d").date())
                function_call_response = kreta_utils.get_grades(start_date, end_date)    
                if (function_call_response == []):
                    function_call_response = "No grades for this week."
                func_arguments = f"date: {func_arg_date}"
                trace_tool_call(tool_call, func_arguments, function_call_response)

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_call.function.name,
                    "content": str(function_call_response),
                }
            ) 
        function_response = client.chat.completions.create(
            model=deployment_name,
            messages=messages,
        )   

        response_function = function_response.choices[0].message

        console.print(f"[bold blue]Kréta Bot:[/] ", end="")
        console.print(response_function.content)
    else:      
        console.print(f"[bold blue]Kréta Bot:[/] ", end="")
        console.print(response_message.content)        