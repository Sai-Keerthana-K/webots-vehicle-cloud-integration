from vehicle import Driver
import math

driver = Driver()
timestep = int(driver.getBasicTimeStep())

# -------- GPS --------
gps = driver.getDevice("gps")
gps.enable(timestep)

# -------- COMPASS --------
compass = driver.getDevice("compass")
compass.enable(timestep)

# -------- LIDAR --------
lidar = driver.getDevice("lidar")
lidar.enable(timestep)

# -------- PARAMETERS --------
CRUISE_SPEED = 40.0
SLOW_SPEED = 10.0

STEER_GAIN = 1.2
MAX_STEER = 0.25

SAFE_DISTANCE = 6.0
WAYPOINT_TOL = 2.0   # meters

# -------- WAYPOINTS (x, z) --------
waypoints = [
    (-5, 50),
    (0, 30),
    (10, 10),
    (15, -10),
    (10, -30),
]

current_wp = 0

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# -------- MAIN LOOP --------
while driver.step() != -1:

    # --- Position ---
    pos = gps.getValues()
    x = pos[0]
    z = pos[2]

    # --- Heading from compass ---
    north = compass.getValues()
    heading = math.atan2(north[0], north[2])  # yaw

    # --- Target waypoint ---
    tx, tz = waypoints[current_wp]

    dx = tx - x
    dz = tz - z
    distance = math.sqrt(dx*dx + dz*dz)

    if distance < WAYPOINT_TOL:
        current_wp = (current_wp + 1) % len(waypoints)
        continue

    target_angle = math.atan2(dx, dz)
    angle_error = target_angle - heading

    # normalize angle
    while angle_error > math.pi:
        angle_error -= 2 * math.pi
    while angle_error < -math.pi:
        angle_error += 2 * math.pi

    steer = clamp(STEER_GAIN * angle_error, -MAX_STEER, MAX_STEER)

    # --- Obstacle avoidance ---
    ranges = lidar.getRangeImage()
    front = min(ranges[len(ranges)//3 : 2*len(ranges)//3])

    if front < SAFE_DISTANCE:
        driver.setCruisingSpeed(SLOW_SPEED)
        steer += 0.2
    else:
        driver.setCruisingSpeed(CRUISE_SPEED)

    driver.setSteeringAngle(clamp(steer, -MAX_STEER, MAX_STEER))
