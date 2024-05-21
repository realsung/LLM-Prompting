import os
import time
import json
import glob
import difflib
import re
from env import settings
from openai import OpenAI
import tempfile
import instructions
import csv

'''
Todo
# - .js filename list & path to .jsonl file
# - Upload the codebase
- Few-shot prompting with example codes
- query the model for the output
    - match code style
    - profiling the code style (e.g. tabWidth, semi, etc.)
- save the output to a file (e.g. security patch comments, etc.)
- refactoring the code
- testing the code (diffing, performance, etc.)
- translate english to korean or extract comment to korean
- 클래스화
'''

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

def diff_code(code1, code2):
    code1 = code1.splitlines()
    code2 = code2.splitlines()
    diff = difflib.unified_diff(code1, code2, lineterm='')
    return '\n'.join(diff)

def check_status(run_id,thread_id):
    run = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id,
    )
    return run.status

def upload_file(uploaded_file):
    global client
    with open(uploaded_file, "rb") as f:
        file = client.files.create(
            file=f,
            purpose = 'assistants'
        )
        print(file)
    return file

# def preprocess_code(file_path):
#     with open(file_path, 'r') as file:
#         lines = file.readlines()
    
#     if lines and lines[0].startswith('#!'):
#         lines = lines[1:]
    
#     temp_dir = tempfile.mkdtemp()

#     temp_file_path = os.path.join(temp_dir, os.path.basename(file_path))
#     with open(temp_file_path, 'w') as temp_file:
#         temp_file.writelines(lines)

#     # temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
#     # temp_file.writelines(lines)
#     # temp_file.close()
    
#     return temp_file_path

def preprocess_code(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    if lines and lines[0].startswith('#!'):
        lines = lines[1:]

    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
    temp_file.writelines(lines)
    temp_file.close()
    
    return temp_file.name



# create assistant
# assistant = client.beta.assistants.create(
#     name="Code Refactorer",
#     instructions=instructions.instruction_assistance,
#     tools=[{"type": "code_interpreter"}, {"type": "file_search"}],
#     model="gpt-4o",
# )
# id : asst_V3qdl7fwrsz1CI6iC3a1ZCuZ

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
    temp_file_path = preprocess_code(file['path'])
    print(f'[*] {temp_file_path}')
    assistant_file_id = upload_file(temp_file_path)
    file_id_list.append(assistant_file_id)
    os.remove(temp_file_path)

thread  = client.beta.threads.create()

attachments_list = []
for file in file_id_list:
    attachments_list.append({"file_id": file.id, "tools": [{"type": "code_interpreter"}]})



message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=instructions.instruction_learning_code,
    attachments=attachments_list,
)


my_run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=settings.LLM_API_KEY['assistant'],
)

start_time = time.time()
status = check_status(my_run.id,thread.id)

while status != 'completed':
    time.sleep(1)
    status = check_status(my_run.id,thread.id)

print("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60), int((time.time() - start_time) % 60)))
print(f'Status: {status}')

messages = client.beta.threads.messages.list(
    thread_id=thread.id
)

print(messages)



script_directory = os.path.dirname(os.path.realpath(__file__)) #파이썬 스크립트가 존재하는 디렉터리

csv_file_path = input("input csv file path: ")
csv_name = os.path.basename(csv_file_path)

f = open(csv_file_path, 'r', encoding='utf-8')
rdr = csv.reader(f)

vulnerabilities_list = list()
for line in rdr:
    vulnerabilities_list.append(line)
f.close()

vulnerabilities_dict_list = list()
for vulnerability_list in vulnerabilities_list:
    vulnerability_dict = dict()
    vulnerability_dict['name'] = vulnerability_list[0]
    vulnerability_dict['description'] = vulnerability_list[1]
    vulnerability_dict['severity'] = vulnerability_list[2]
    vulnerability_dict['message'] = vulnerability_list[3]
    vulnerability_dict['path'] = vulnerability_list[4]
    vulnerability_dict['start_line'] = int(vulnerability_list[5])
    vulnerability_dict['start_column'] = int(vulnerability_list[6])
    vulnerability_dict['end_line'] = int(vulnerability_list[7])
    vulnerability_dict['end_column'] = int(vulnerability_list[8])

print(vulnerability_dict)
vulnerabilities_dict_list.append(vulnerability_dict)



response = client.beta.threads.delete(thread.id)
# response = client.beta.assistants.delete(assistant.id)
for my_file in file_id_list:
    response = client.files.delete(my_file.id)