import requests
import json
import pprint as pp
import matplotlib.pyplot as plt
import numpy as np
import ast
import string
import math as m
import time
import datetime
import os

def distance_on_unit_sphere(lat1, long1, lat2, long2):
 
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = m.pi/180.0
         
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
         
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
         
    # Compute spherical distance from spherical coordinates.
         
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta', phi')
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length 
    cos = (m.sin(phi1)*m.sin(phi2)*m.cos(theta1 - theta2) + m.cos(phi1)*m.cos(phi2))
 
    # some VooDoo    
    cleanCos = min(1,max(cos,-1)) 
    
    arc = m.acos(cleanCos)

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc*6373000 #3960 for miles



def listenFromServer():
    # get from the NameServer
    # Set url address.
    while True:
        base = 'http://127.0.0.1:5000/'
        endpoint1 = 'network/eBikeDemo/object/DataVisual/stream/inputCoordinates'
        
        address1 = base + endpoint1
        
        
        # Set query (i.e. http://url.com/?key=value).
        query = {}
        # Set header.
        header = {'Content-Type':'application/json'}
    
        # Set body (also referred to as data or payload). Body is a JSON string.
        at = int((datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(0)).total_seconds())
    
       
        
        # Form and send request. Set timeout to 2 minutes. Receive response.
        response1 = requests.request('get', address1, data=None, params=query)
        
        payload1 = json.loads( response1.text )
        #payload1_data = payload1['objects']['Lab5']['streams']['processedData']['points']
        
        #data_origin = payload1_data[0]['value']
        #data_destination = payload_data[0]['value']
    
        #print data_value1
    
        #return [str(data_origin), str(data_destination)]
        if 'message' in payload1 and payload1['message'] == 'Stream not found':
            import time
            time.sleep(2)
            print payload1
            continue
        else:
            print(payload1)
            payload1_data = payload1['objects']['DataVisual']['streams']['inputCoordinates']['points']
            for point in payload1_data:
                if point['at'] == 2:
                    destination = point['value']
                elif point['at'] == 1:
                    origin = point['value']
                else:
                    print("need destination as 2 and origin as 1")
            return [origin, destination]

resultsFromServer = listenFromServer()

api_key = "AIzaSyB9YRKeHx1Y-g2VAdB5SX1rtlBkp1nrn-A"
    
# Define Input Parameters
imHere = resultsFromServer[0] #Origin
#imHere = '1823 Highland Place, Berkeley CA 94203'
#imHere = input("Where are you?: ")
goHere = resultsFromServer[1] #Destination
#goHere = 'Clark Kerr Campus, Berkeley California 94720'
#goHere = input("Where do you want to go?: ")
plotType = 'Simple'
title = "Elevation"

# header just to make stuff look pretty
print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
print "Runtime: " + time.strftime("%H,%M")
print "Trip: " + imHere + " to " + goHere
print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

# format directions request URL
baseDirect = 'https://maps.googleapis.com/maps/api/directions/json?' 
origin = "origin=" + imHere
destination = "destination=" + goHere

# make request, turn request to json dictionary
directions = requests.request("get",baseDirect + origin + '&' + destination + '&' + api_key)
direct_json = directions.json()

# this is a branch of the json file received from api request
stepWise = direct_json['routes'][0]['legs'][0]['steps']

# counts up to move through dictionary
stepIndex = 0
polyLines = []
legLength = []

# make polyLines and legLength by indexing into different parts of the dictionary
for i in stepWise:
    polyLines.append((stepIndex, direct_json['routes'][0]['legs'][0]['steps'][stepIndex]['polyline']['points']))
    legLength.append(i['distance']['value'])
    stepIndex += 1

# format elevation request URL
locationElevation = []
y = []
sampleCount = 0
urlLen = []
baseElevation = "https://maps.googleapis.com/maps/api/elevation/json?"

# a request is made for each polyline 
for i in range(0,len(polyLines)):
    
    # a request has to have samples, path, api key 
    samples = 'samples=' + str(legLength[i]/50) + '&'
    path = 'path=enc:' + polyLines[i][1] + '&'
    url = baseElevation + samples + path + api_key
    urlLen.append(len(url))
    
    # make the request
    elevate = requests.request('get',url)
    
    # some weird voodoo shit, I was getting HTML at the end of the text
    # caused an error so i cut it off
    elev8 = elevate.text
    if string.find(elev8, "<!") == 0:
        break
    
    # change back to dictionary
    elevationDict = ast.literal_eval(elev8)
    # add a sample every 50m
    sampleCount += legLength[i]/50
    
    # create y - elevation data
    # create locationElevation - 
    for i in elevationDict['results']:
        locationElevation.append((round(i['elevation'],2),i['location']))
        y.append(i['elevation'])

# get distance between consecutive points to make accurate x values
print "LocEle: ", len(locationElevation)

# make array
xTest = [0]
sumTillNow = 0
counter = 0


for i in range(0,len(locationElevation)-1):
    
    # pick 2 lat long pairs from locationElevation
    lat1 = locationElevation[i][1]['lat']
    long1 = locationElevation[i][1]['lng']
    lat2 = locationElevation[i+1][1]['lat']
    long2 = locationElevation[i+1][1]['lng']
    
    # call arc length function to get distance, scaling to meters done
    dx = distance_on_unit_sphere(lat1, long1, lat2, long2)
    
    # get sum to write to each x value
    sumTillNow += dx
    counter += 1
    
    # annoyingly precise numbers here, leaving for now
    xTest.append(sumTillNow)
    
print "Max URL Len: ", max(urlLen)
print xTest
    
x = xTest
#TODO Get more accurate x
xTrim = x[:len(y)]

gradient = np.gradient(y)    
plt.plot(xTrim, gradient)
plt.title("Slope v. Distance")
plt.xlabel("Distance [m]")
plt.ylabel("Slope")
plt.show()

x_fewer, y_fewer = [], []
# CHOOSE NUMBER OF SAMPLES HERE len(y) <-----------------
spaced = np.linspace(0,len(y)-1, 20)
for i in spaced:
    x_fewer.append(x[int(i)])
    y_fewer.append(y[int(i)])
plt.plot(x_fewer, y_fewer)
plt.title("Trimmed Elevation")
plt.ylabel("Elevation [m]")
plt.xlabel("Distance [m]")
plt.show()

# Physics now
# constants
weight = 100
C_roll = .015
rho = 1.2041
C_d = 1.1
A = .5
DT_Loss = 7.
eff = .9

# iniaialize things
# slopes = list of slope value between i, i+1
slopes = []
# eneOut = list of (Force x Distance x Drive Train Loss)
eneOut = []
# cumulativeEnergy = sum of eneOut including step i
cumulativeEnergy = []
for i in range(0, len(x_fewer)-1):
    slopeSubI = (y_fewer[i+1]-y_fewer[i])/(x_fewer[i+1]-y_fewer[i])
    slopes.append(slopeSubI)
    
idx = 0 
for s in slopes:
    # Choose v based on slope (could be finer)
    if s > 0.0015:
        v = 3
    elif s < -0.0015:
        v = 7
    else:
        v = 5
    # Forces
    F_grav = 9.807 * m.sin(m.atan(s)) * weight
    F_roll = 9.807 * m.cos(m.atan(s)) * weight * C_roll
    F_drag = 0.5 * C_d * A * rho * v**2
    print "F_grav", F_grav
    print "F_roll", F_roll
    print "F_drag", F_drag
    print ""
    
    W_Legs = (1-(DT_Loss/100))**-1 * (F_grav + F_roll + F_drag) * (x_fewer[int(idx+1)]-x_fewer[int(idx)])
    
    # too many sig figs
    deltaE = round(W_Legs * 1/eff, 0)/1000 # kJ
    
    eneOut.append(deltaE)
    cumulativeEnergy.append(sum(eneOut))
    
# plot thing
plt.plot(range(0,len(eneOut)),cumulativeEnergy)
plt.title("Energy Use")
plt.xlabel("Distance [m]")
plt.ylabel("Energy Use [kJ]")
plt.axis([0, len(eneOut), 0, sum(eneOut)])
plt.show()

print cumulativeEnergy
    
def main():
    distance=x_fewer #elevation
    elevation=y_fewer #distance
    #energy = cumulativeEnergy[0:len(cumulativeEnergy)-1]
    energy = cumulativeEnergy
    print len(cumulativeEnergy)
    print len(x_fewer)
    distance2 = x_fewer[0:len(cumulativeEnergy)]
    
    dataFromGMapsAPI(distance,elevation,'elevation')
    dataFromGMapsAPI(distance2,energy,'energy')
    
    writePlanDotText()
# Send an HTTP request to store
# gMapsAPI data to Server
def dataFromGMapsAPI(x,y,stream_location):
    #stream_location must be a string
    # Send (POST) a name to the NameServer
    # Set url address.
    base = 'http://127.0.0.1:5000/'
    endpoint1 = 'network/eBikeDemo/object/DataVisual/stream/' + stream_location
    #endpoint2 = 'network/eBikeDemo/object/DataVisual/stream/EnergyUse'
    address1 = base + endpoint1
    #address2 = base + endpoint2
    
    
    for i in range(len(x)):
        # Set query (i.e. http://url.com/?key=value).
        query = {}
        # Set header.
        header = {'Content-Type':'application/json'}
    
        # Set body (also referred to as data or payload). Body is a JSON string.
        at = int((datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(0)).total_seconds())
        payload1 = [ {'value':str(x[i])+','+ str(y[i]),'at':at } ]
        print(payload1)
        #payload2 = [ {'value':float(y),'at':at } ]
        body1 = json.dumps(payload1)
        #body2 = json.dumps(payload2)
       
    
        # Form and send request. Set timeout to 2 minutes. Receive response.
        response1 = requests.request('post', address1, data=body1, params=query, headers=header, timeout=120 )
        #response2 = requests.request('post', address2, data=body2, params=query, headers=header, timeout=120 )

def writePlanDotText():
    planStr = ''
    for i in range(len(cumulativeEnergy)):
        planStr += str(round(x_fewer[i],1))
        planStr += ','
        planStr += str(round(cumulativeEnergy[i],1))
        planStr += ':'
    fileName = os.path.join(os.path.expanduser('~'), "Desktop/plan.txt")
    plan = open(fileName, 'w')
    plan.write(planStr)
    plan.close()
# Run the program
main()




# pp.pprint(thingthing)
# ^^^ Makes json things readable