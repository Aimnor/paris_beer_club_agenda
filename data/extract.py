import json
with open("data/subscribers.json", "r") as file_handler:
    data = json.load(file_handler)
    
with open("data/subscribers.txt", "w") as file_handler:
    file_handler.writelines([subscriber["relative_url"]+"\n" for subscriber in data])