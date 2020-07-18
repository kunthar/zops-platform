#!/usr/bin/env python3
import yaml
import sys
import tempfile
import subprocess
import os

args = sys.argv[1:]
yaml_file = None
new_file = None
start_arg = None

# Find yaml file and change its name to tmpfile in args
for i, arg in enumerate(args):
    if ('.yml' or '.yaml') in arg:
        yaml_file = arg
        full_path = os.path.abspath(yaml_file)
        dir_path, file_name = os.path.split(full_path)
        new_file = '{}/apw-{}'.format(dir_path, file_name)
        args[i] = new_file
    if '--start-at-task' in arg:
        start_arg = (i, arg.split('=')[1])

# read content of file
with open(yaml_file, 'r') as f:
    content = f.read()

# convert it to python object
playbook = yaml.load(content)

# add task numbers
for play_no, play in enumerate(playbook):
    for task_no, task in enumerate(play['tasks']):
        task.update({'name': '{},{}] [{}'.format(play_no, task_no, task['name'])})
        try:
            if '{},{}'.format(play_no, task_no) == start_arg[1]:
                args[start_arg[0]] = '{}={}'.format('--start-at-task', task['name'])
        except TypeError:
            pass


# write new content to tempfile
with open(new_file, 'w') as file:
 file.write(yaml.dump(playbook, default_flow_style=False))

# run playbook with args
ansible_playbook = ['ansible-playbook']
print('{} is created. Check for the new version of playbook.\n'.format(new_file))
subprocess.call(ansible_playbook + args)

