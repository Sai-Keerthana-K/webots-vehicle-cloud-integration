from controller import Supervisor, Keyboard

# Create supervisor
robot = Supervisor()
timestep = int(robot.getBasicTimeStep())

# Enable keyboard
keyboard = Keyboard()
keyboard.enable(timestep)

# Get headlight PointLights by DEF name
left_headlight = robot.getFromDef("LEFT_HEADLIGHT")
right_headlight = robot.getFromDef("RIGHT_HEADLIGHT")

if left_headlight is None or right_headlight is None:
    print("Headlight nodes NOT found")
else:
    print("Headlights found")
    left_intensity = left_headlight.getField("intensity")
    right_intensity = right_headlight.getField("intensity")

print("Press L = Headlights ON")
print("Press O = Headlights OFF")

while robot.step(timestep) != -1:
    key = keyboard.getKey()

    # Turn headlights ON
    if key == ord('L') and left_headlight is not None:
        left_intensity.setSFFloat(5.0)
        right_intensity.setSFFloat(5.0)
        print("Headlights ON")

    # Turn headlights OFF
    elif key == ord('O') and left_headlight is not None:
        left_intensity.setSFFloat(0.0)
        right_intensity.setSFFloat(0.0)
        print("Headlights OFF")
