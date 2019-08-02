import math
import random
import time

# Create a list of strings that can be selected from randomly. This allows for greater variety in the strings created.
class rstring():
    def __init__(self, items):
        if items:
            self.items = items
        else:
            self.items = []
        
    def append(self, str):
            self.items.append(str)
    
    def __repr__(self):
        if len(self.items) == 0:
            return ""
        else:
            return self.items[random.randint(0, len(self.items) - 1)]

def clamp(_max,_min,value):
    if value > _max:
        return _max
    if value < _min:
        return _min
    return value

def sign(x):
    if x <= 0:
        return -1
    else:
        return 1

class Vector:
    def __init__(self, content): #accepts list of float/int values
        self.data = content

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        return self.data[item]

    def vec3Convert(self):
        return vec3(self.data[0],self.data[1].self.data[2])

    def raiseLengthError(self,other, operation):
        raise ValueError(f"Tried to perform {operation} on 2 vectors of differing lengths")

    def raiseCrossError(self):
        raise ValueError("Both vectors need 3 terms for cross product")

    def __mul__(self, other):
        if len(self.data) == len(other.data):
            return Vector([self.data[i] * other[i] for i in range(len(other))])
        else:
            self.raiseLengthError(other,"multiplication")

    def __add__(self, other):
        if len(self.data) == len(other.data):
            return Vector([self.data[i] + other[i] for i in range(len(other))])
        else:
            self.raiseLengthError(other, "addition")

    def __sub__(self, other):
        if len(self.data) == len(other.data):
            return Vector([self.data[i] - other[i] for i in range(len(other))])
        else:
            self.raiseLengthError(other, "subtraction")

    def alignTo(self, rot):
        v = Vector([self.data[0], self.data[1], self.data[2]])
        v = Vector([v[0],math.cos(rot[0]) * v[1] + math.sin(rot[0]) * v[2],math.cos(rot[0]) * v[2] - math.sin(rot[0]) * v[1]])
        v = Vector([math.cos(-rot[1]) * v[0] + math.sin(-rot[1]) * v[2], v[1], math.cos(-rot[1]) * v[2] - math.sin(-rot[1]) * v[0]])
        v = Vector([math.cos(-rot[2]) * v[0] + math.sin(-rot[2]) * v[1], math.cos(-rot[2]) * v[1] - math.sin(-rot[2]) * v[0], v[2]])

        return v

    def crossProduct(self,other):
        if len(self.data) == 3 and len(other.data) == 3:
            newVec = [0,0,0]
            newVec[0] = self[1]*other[2] - self[2]*other[1]
            newVec[1] = self[2]*other[0] - self[0]*other[2]
            newVec[2] = self[0] * other[1] - self[1] * other[0]

            return Vector(newVec)


        else:
            self.raiseCrossError()


    def magnitude(self):
        return math.sqrt(sum([x*x for x in self]))

    def normalize(self):
        mag = self.magnitude()
        if mag != 0:
            return Vector([x/mag for x in self])
        else:
            return Vector([0 for _ in range(len(self.data))])

    def dotProduct(self,other):
        product = 0
        for i,j in zip(self,other):
            product += i*j
        return product

    def scale(self,scalar):
        return Vector([x*scalar for x in self.data])


    def correction_to(self, ideal):
        current_in_radians = math.atan2(self[1], -self[0])
        ideal_in_radians = math.atan2(ideal[1], -ideal[0])

        correction = ideal_in_radians - current_in_radians
        if abs(correction) > math.pi:
            if correction < 0:
                correction += 2 * math.pi
            else:
                correction -= 2 * math.pi

        return correction


    def toList(self):
        return self.data

    def lerp(self,otherVector,percent): #percentage indicated 0 - 1
        percent = clamp(1,0,percent)
        originPercent = 1-percent

        scaledOriginal = self.scale(originPercent)
        other = otherVector.scale(percent)
        return scaledOriginal+other

def convertStructLocationToVector(struct):
    return Vector([struct.physics.location.x,struct.physics.location.y,struct.physics.location.z])

def convertStructVelocityToVector(struct):
    return Vector([struct.physics.velocity.x,struct.physics.velocity.y,struct.physics.velocity.z])


def findDistance(origin,destination):
    difference = origin - destination
    return abs(math.sqrt(sum([x * x for x in difference])))

def distance2D(origin_vector,destination_vector):
    _origin = Vector([origin_vector[0],origin_vector[1]])
    _destination = Vector([destination_vector[0],destination_vector[1]])
    difference = _origin - _destination
    return abs(math.sqrt(sum([x * x for x in difference])))

def cornerDetection(_vec):
    #a simple function for determining if a vector is located within the corner of the field
    #if the vector is, will return the corner number, otherwise will return -1
    # 0 = blue right, 1 = blue left, 2 = orange left, 3 = orange right  #perspective from blue goal
    y_value = 3840
    x_value = 2500

    if abs(_vec.data[0]) > x_value and abs(_vec.data[1]) > y_value:
        x = _vec.data[0]
        y = _vec.data[1]

        if x > 0:
            if y > 0:
                return 2
            else:
                return 1
        else:
            if y > 0:
                return 3
            else:
                return 0
    else:
        return -1

def boxDetection(_vec):
    if abs(_vec[0]) <= 1000:
        if 5120 - abs(_vec[1]) <= 1000:
            if _vec[1] > 0:
                #in orange box
                return 4
            else:
                return 5
    return -1

def get_team_color_by_zone(num):
    blues = [0,1,5,7]
    oranges = [2,3,4,6]

    if num in blues:
        return "blue"
    elif num in oranges:
        return "orange"
    else:
        raise ValueError(f"arg num must be a number 0-7, value recieved: {num}.")

def find_current_zone(ball_object):
    #0:blue right, 1:blue left, 2:orange left, 3:orange right, 4:orange box, 5:blue box, 6:orange half, 7:blue half,
    zone = cornerDetection(ball_object.location)
    if zone != -1:
        return zone

    zone = boxDetection(ball_object.location)
    if zone != -1:
        return zone

    else:
        if ball_object.location[1] > 0:
            return 6
        else:
            return 7


def isBallNearWall(ball_vector):
    if ball_vector[0] > 4096 - 150:
        return True
    if ball_vector[0] < -4096 + 150:
        return True

    if ball_vector[1] < -5120 + 150:
        return True

    if ball_vector[1] > 5120 - 150:
        return True



def speedConversion(speed_in_UU):
    # Goosefairy - "1uu == 1cm iirc". BLame Goose if this information is incorrect
    if speed_in_UU != 0:
        return int(round((speed_in_UU/100000)*60*60))
    return 0

class Car():
    def __init__(self, name, team, index): #could probably just start updating this class with boost, location and velocity
        self.name = name
        self.team = team
        self.index = index


class ballObject():
    def __init__(self, packetBall):
        self.location = convertStructLocationToVector(packetBall)
        self.velocity = convertStructVelocityToVector(packetBall)

    def getRealSpeed(self):
        return speedConversion(self.velocity.magnitude())



class Team():
    def __init__(self, teamNumber, members):
        self.team = teamNumber
        self.members = members
        self.lastTouch = None
        self.score = 0

    def update(self, ballTouch):
        if ballTouch.team == self.team:
            self.lastTouch = ballTouch


class ballTouch():
    def __init__(self, touchInfo):
        self.player_name = touchInfo.player_name
        self.hit_location = touchInfo.hit_location
        self.team = touchInfo.team
        self.player_index = touchInfo.player_index
        self.time_seconds = touchInfo.time_seconds

    def __eq__(self,other):
        if type(other) != ballTouch:
            raise ValueError(f"Can not do comparisan operations of balltouch and {type(other)} objects.")

        if self.player_name != other.player_name:
            return False

        if self.hit_location != other.hit_location:
            return False

        if self.team != other.team:
            return False

        if self.player_index != other.player_index:
            return False

        if self.time_seconds != other.time_seconds:
            return False

        return True

class Comment():
    def __init__(self, _comment, voiceID,priority,decayRate):
        self.comment = _comment
        self.voiceID = voiceID
        self.priority = priority # 1-10 (except in rare cases)
        self.decayRate = decayRate # 1-10 (except in rare cases) lower = faster decay rate
        self.time_generated = time.time()
        self.valid = True

    def update(self):
        if self.priority <10:
            if time.time() - self.time_generated > self.decayRate:
                self.valid = False




def shotDetection(ballPredictions,timeLimit,gameTime):
    y_threshold = 5200

    for i in range(ballPredictions.num_slices):
        if ballPredictions.slices[i].game_seconds - gameTime < timeLimit:
            y_val = ballPredictions.slices[i].physics.location.y
            if abs(y_val) >= y_threshold:
                if y_val > 0:
                    return True,1
                else:
                    return True,0
        else:
            return False,0

    return False,0






def ballHeading(ballObj,ballPredictionStruct): #0 heading towards blue, 1 heading towards orange, 2 nuetral hit
    blueGoal = Vector([0,-5200,0])
    orangeGoal = Vector([0, 5200, 0])

    futureLocation = convertStructLocationToVector(ballPredictionStruct)

    blueDistance = distance2D(ballObj.location,blueGoal)
    orangeDistance = distance2D(ballObj.location,orangeGoal)

    futureBlueDistance = distance2D(futureLocation,blueGoal)
    futureOrangeDistance = distance2D(futureLocation, orangeGoal)

    if futureBlueDistance < blueDistance and futureOrangeDistance > orangeDistance:
        return 0

    if futureOrangeDistance < orangeDistance and futureBlueDistance > blueDistance:
        return 1

    return 2



