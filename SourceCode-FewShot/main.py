import os
import time
import json
import glob
import difflib
import re
from env import settings
from openai import OpenAI

'''
Todo
# - .js filename list & path to .jsonl file
# - Upload the codebase
- Few-shot prompting with .jsonl lists
- query the model for the output
    - match code style with few-shot prompt
    - profiling the code style (e.g. tabWidth, semi, etc.)
- save the output to a file (e.g. security patch comments, etc.)
- refactoring the code
- testing the code (diffing, performance, etc.)
- translate english to korean or extract comment to korean
- 클래스화
'''

def extract_code(text):
    try:
        if '```' in text:
            matches = re.findall(r'`{3}(.*?)`{3}', text, re.DOTALL)
            return matches

        else:
            return [text,]
        
    except Exception as exception:
        return [text,]
    
    '''
    function = None
    match = re.search('```(.*?)```', code, re.DOTALL)
    if match:
        function = match.group(1)
        function = function.replace("python","")

    if function != None:
        if len(Check_Syntax(function)) != 0:
            return None
        
    return function
    '''

def diff_code(code1, code2):
    code1 = code1.splitlines()
    code2 = code2.splitlines()
    diff = difflib.unified_diff(code1, code2, lineterm='')
    return '\n'.join(diff)

try:
    client = OpenAI(
        api_key=settings.LLM_API_KEY['openai'],
    )
except:
    print("OpenAI() failed")
    
try:
    os.system("rm filelist.jsonl")
except:
    pass

instruction = '''
You are a highly skilled security analyst tasked with fixing a vulnerability in the following source code:

Your task is to carefully review the code, identify the root cause of the vulnerability, and provide a detailed explanation of how to fix it. Please provide your analysis and proposed solution in the following format:

1. Vulnerability Summary:
   - Briefly describe the type of vulnerability and its potential impact.

2. Root Cause Analysis:
   - Explain the specific code patterns, design flaws, or coding practices that led to this vulnerability.
   - Provide line numbers or code snippets to illustrate the problematic areas.

3. Proposed Solution:
   - Outline the steps or code changes required to remediate the vulnerability.
   - If applicable, provide sample code snippets or pseudocode to demonstrate the secure implementation.

4. Additional Considerations:
   - Mention any potential side effects, trade-offs, or best practices to consider when implementing the proposed solution.
   - Suggest any additional security measures or coding practices that could further strengthen the codebase.

Please provide a thorough and actionable response, ensuring that your proposed solution effectively mitigates the identified vulnerability while adhering to secure coding principles and best practices.'''
'''
I'm working on a project to fix a vulnerability by entering the source code into LLM.
The source code is annotated with information about the vulnerability.
Please create a prompt for me to enter the LLM.
'''

# create assistant
# assistant = client.beta.assistants.create(
#     name="Code Refactorer",
#     instructions=instruction,
#     tools=[{"type": "code_interpreter"}],
#     model="gpt-4o",
# )

# .js filename list & write to .jsonl file
# get ./example dir .js list glob
for path in glob.iglob('example/**/*.js', recursive=True):
    with open("filelist.jsonl", "a+") as f:
        f.write(json.dumps({"filename": os.path.basename(path), "path":path}) + "\n")

with open("filelist.jsonl", "r") as f:
    print(f.read())

# Upload the codebase
file_list = []
file_id_list = []

with open("filelist.jsonl", "r") as f:
    for line in f:
        file_list.append(json.loads(line))

for file in file_list:
    file_id = client.files.create(
        file=open(file['path'], "rb"),
        purpose="user_data",
    )
    file_id_list.append(file_id.id)

    # client.beta.assistants.files.create(assistant_id=assistant_id, file_id=uploaded_file.id)

print(file_id_list)
# thread = client.beta.threads.create(
    
# )


# assistant = client.beta.assistants.create(
#     name="Data visualizer",
#     description="You are great at creating beautiful data visualizations. You analyze data present in .csv files, understand trends, and come up with data visualizations relevant to those trends. You also share a brief text summary of the trends observed.",
#     model="gpt-4o",
#     tools=[{"type": "code_interpreter"}],
#     tool_resources={
#         "code_interpreter": {
#             "file_ids": [file.id]
#         }
#     }
# )