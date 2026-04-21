from vehicle import Driver
from controller import Keyboard

driver = Driver()
timestep = int(driver.getBasicTimeStep())

keyboard = Keyboard()
keyboard.enable(timestep)

# Sensors
front = driver.getDevice("front_ds")
left  = driver.getDevice("left_ds")
right = driver.getDevice("right_ds")

front.enable(timestep)
left.enable(timestep)
right.enable(timestep)

# Parameters
AUTO_SPEED = 10.0
TURN_SPEED = 6.0
OBSTACLE_TH = 0.8

STEER_STEP = 0.05
MAX_STEER = 0.5

manual_speed = AUTO_SPEED
manual_steer = 0.0

# Headlight state (future-proof)
headlights_on = False

print("SAFE autonomous + manual controller started")
print("Arrow keys = manual override")
print("L = lights ON, O = lights OFF")

while driver.step() != -1:
    key = keyboard.getKey()
    manual = False

    # -------- MANUAL OVERRIDE --------
    if key != -1:
        manual = True

        if key == Keyboard.UP:
            manual_speed += 0.5
        elif key == Keyboard.DOWN:
            manual_speed -= 0.5
        elif key == Keyboard.LEFT:
            manual_steer += STEER_STEP
        elif key == Keyboard.RIGHT:
            manual_steer -= STEER_STEP

        # Lights (logic only for now)
        elif key == ord('L'):
            headlights_on = True
            print("Headlights ON")
        elif key == ord('O'):
            headlights_on = False
            print("Headlights OFF")

        manual_speed = max(0, min(manual_speed, 25))
        manual_steer = max(-MAX_STEER, min(manual_steer, MAX_STEER))

        driver.setCruisingSpeed(manual_speed)
        driver.setSteeringAngle(manual_steer)

    # -------- AUTOMATIC MODE --------
    if not manual:
        f = front.getValue()
        l = left.getValue()
        r = right.getValue()

        speed = AUTO_SPEED
        steer = 0.0

        # Obstacle logic
        if f > OBSTACLE_TH:
            speed = TURN_SPEED
            steer = 0.3 if l < r else -0.3
        elif l > OBSTACLE_TH:
            steer = -0.3
        elif r > OBSTACLE_TH:
            steer = 0.3

        driver.setCruisingSpeed(speed)
        driver.setSteeringAngle(steer)

        manual_speed = speed
        manual_steer *= 0.9
