import json

with open("data/subscribers.json", "r") as file_handler:
    subs = [sub["relative_url"] for sub in json.load(file_handler)]
    
with open("data/all_time_subscribers.json", "r") as file_handler:
    pros = json.load(file_handler)

for pro in pros:
    pro["subscribed"] = False
    if pro["relative_url"] in subs:
        pro["subscribed"] = True

with open("data/professionals.json", "w") as file_handler:
    json.dump(pros, file_handler, indent=4, ensure_ascii=False)
