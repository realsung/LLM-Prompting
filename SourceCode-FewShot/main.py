import os
from openai import OpenAI
import time
import json
import glob
import difflib
import re
from env import settings

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

# Setting the API key
OpenAI.api_key = settings.LLM_API_KEY['openai']

try:
    client = OpenAI()
except:
    print("OpenAI() failed")
    
try:
    os.system("rm mydata.jsonl")
except:
    pass

# .js filename list & write to .jsonl file
# get ./example dir .js list glob
for path in glob.iglob('example/**/*.js', recursive=True):
    with open("mydata.jsonl", "a+") as f:
        f.write(json.dumps({"filename": os.path.basename(path), "path":path}) + "\n")

with open("mydata.jsonl", "r") as f:
    print(f.read())

# Upload the codebase
file_list = []
with open("mydata.jsonl", "r") as f:
    for line in f:
        file_list.append(json.loads(line))

for file in file_list:
    with open(file['path'], 'rb') as f:
        uploaded_file = client.files.create(
            file=f,
            purpose='assistants'
        )
    # client.beta.assistants.files.create(assistant_id=assistant_id, file_id=uploaded_file.id)

print(client.files.list())


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