import json

prompts = []

with open("prompt.txt", "r") as file:
    for line in file:
        prompts.append(line)

with open("prompts.json", "w") as json_file:
    json.dump(prompts, json_file, indent=4)
