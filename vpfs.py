# 3 API Calls
# The Match API is used to communicate match state to vehicles, 
# and provide a check that all vehicles are connected to the server.

# The Fare API is used to see the currently available fares, select one to deliver, 
# and check the current fare's status.

# The GPS API is used to identify where a vehicle is on the map. Note that the GPS is updated 
# periodically (expected to be 0.25-5Hz, depending on the optimization that can be achieved), so some 
# consideration should be given to the age of the data.

import json
from urllib import request

# Server details will change between lab, home, and competition, so saving them somewhere easy to edit
server_ip = "localhost"
server = f"http://{server_ip}:5000"
authKey = "10"
team = 10

# Match API
res = request.urlopen(server + "/match" + "?auth=" + authKey)
if res == 200:
    match_data = json.loads(res.read())
else:
     print("Got status", str(res.status), "requesting match")

# Fare API
res = request.urlopen(server + "/fares")
# Verify that we got HTTP OK
if res.status == 200:
    # Decode JSON data
    fares = json.loads(res.read())
    # Loop over the available fares
    for fare in fares:
        # If the fare is claimed, skip it
        if not fare['claimed']:
            # Get the ID of the fare
            toClaim = fare['id']
            
            # Make request to claim endpoint
            res = request.urlopen(server + "/fares/claim/" + str(toClaim) + "?auth=" + authKey)
            # Verify that we got HTTP OK
            if res.status == 200:
                # Decode JSON data
                data = json.loads(res.read())
                if data['success']:
                    # If we have a fare, exit the loop
                    print("Claimed fare id", toClaim)
                    break
                else:
                    # If the claim failed, report it and let the loop continue to the next
                    print("Failed to claim fare", toClaim, "reason:", data['message'])
            else:
                # Report HTTP request error
                print("Got status", str(res.status), "claiming fare")

else:
    # Report HTTP request error
    print("Got status", str(res.status), "requesting fares")

# Check the status of our fare
res = request.urlopen(server + "/fares/current/" + str(team))
# Verify that we got HTTP OK
if res.status == 200:
    # Decode JSON data
    data = json.loads(res.read())
    # Report fare status
    if data['fare'] is not None:
        print("Have fare", data['fare'])
    else:
        print("No fare claimed", data['message'])
else:
    # Report HTTP request error
    print("Got status", str(res.status), "checking fare")

# GPS API
# res = request.urlopen(server + "/WhereAmI/" + str(team))
# if res == 200:
#     GPS_data = json.loads(res.read())
# else:
#      print("Got status", str(res.status), "requesting location of vehicle")