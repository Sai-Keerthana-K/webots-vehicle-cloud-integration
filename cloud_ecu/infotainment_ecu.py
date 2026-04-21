from gateway_ecu import send_to_vehicle

last_speed = 0

def infotainment_menu():
    print("\n=== INFOTAINMENT SYSTEM ===")
    print("1. Set Speed")
    print("2. Stop Vehicle")
    print("3. Headlights ON")
    print("4. Headlights OFF")
    print("5. Hazard Lights ON")
    print("6. Hazard Lights OFF")
    print("7. Vehicle Status")
    print("8. Exit")

while True:
    infotainment_menu()
    choice = input("Select option: ")

    if choice == "1":
        try:
            speed = float(input("Enter speed: "))

            # 🔒 INPUT VALIDATION (ADDED)
            if speed < 0 or speed > 30:
                print("❌ Invalid speed! Allowed range: 0 to 30")
                continue

            last_speed = speed
            cmd = {"cmd": "SET_SPEED", "value": speed}

        except ValueError:
            print("❌ Invalid input! Please enter a numeric value.")
            continue

    elif choice == "2":
        cmd = {"cmd": "SET_SPEED", "value": 0}

    elif choice == "3":
        cmd = {"cmd": "HEADLIGHT_ON"}

    elif choice == "4":
        cmd = {"cmd": "HEADLIGHT_OFF"}

    elif choice == "5":
        cmd = {"cmd": "HAZARD_ON"}

    elif choice == "6":
        cmd = {"cmd": "HAZARD_OFF"}

    elif choice == "7":
        cmd = {"cmd": "STATUS"}

    elif choice == "8":
        print("Infotainment ECU shutting down.")
        break

    else:
        print("Invalid option")
        continue

    ack = send_to_vehicle(cmd)
    print("Vehicle ACK:", ack)
