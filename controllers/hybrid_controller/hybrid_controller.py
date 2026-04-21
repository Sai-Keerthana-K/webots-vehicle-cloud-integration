from vehicle import Driver
from controller import Keyboard

driver = Driver()
timestep = int(driver.getBasicTimeStep())

keyboard = Keyboard()
keyboard.enable(timestep)

# -------------------------
# PARAMETERS
# -------------------------
AUTO_SPEED = 12.0
MAX_SPEED = 25.0

STEER_STEP = 0.05
MAX_STEER = 0.5

manual_speed = AUTO_SPEED
manual_steer = 0.0

print("Hybrid auto + manual controller started")
print("Arrow keys = manual override")
print("Release keys = automatic resumes")

# -------------------------
# MAIN LOOP
# -------------------------
while driver.step() != -1:
    key = keyboard.getKey()

    manual_override = False

    # ---------- MANUAL OVERRIDE ----------
    if key != -1:
        manual_override = True

        if key == Keyboard.UP:
            manual_speed += 0.5

        elif key == Keyboard.DOWN:
            manual_speed -= 0.5

        elif key == Keyboard.LEFT:
            manual_steer += STEER_STEP

        elif key == Keyboard.RIGHT:
            manual_steer -= STEER_STEP

        # Clamp values
        manual_speed = max(0.0, min(manual_speed, MAX_SPEED))
        manual_steer = max(-MAX_STEER, min(manual_steer, MAX_STEER))

        driver.setCruisingSpeed(manual_speed)
        driver.setSteeringAngle(manual_steer)

    # ---------- AUTOMATIC MODE ----------
    else:
        driver.setCruisingSpeed(AUTO_SPEED)
        driver.setSteeringAngle(0.0)

        # Smoothly reset manual state
        manual_speed = AUTO_SPEED
        manual_steer *= 0.9
