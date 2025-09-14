# main.py
from arduino import Dispenser
from datetime import datetime
import time
from pill_reminder_simple import remind_patient  # expects remind_patient(time_str, med_name)
# If you have escalate_to_caregiver / call_patient, you can import & use them similarly.

MED_NAME = "Scheduled medication"
DROP_DELAY = 1.0        # seconds for pill to fall after turning servo
FIRST_WINDOW = 30       # seconds to wait before reminding
POST_REMINDER_WINDOW = 60  # keep watching after reminder

def wait_until_taken(d: Dispenser, timeout_s: int) -> bool:
    """Return True if IR becomes HIGH within timeout; False otherwise."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        state = d.get_ir()  # 'LOW' (present) / 'HIGH' (taken)
        print("IR state:", state)
        if state == "HIGH":
            print("✅ Pill taken!")
            return True
        time.sleep(1)
    return False

def main():
    d = Dispenser()
    try:
        print("Dispensing pill...")
        d.turn_45()
        time.sleep(DROP_DELAY)  # let pill drop into detection position

        print(f"Waiting up to {FIRST_WINDOW}s for patient to take the pill...")
        if wait_until_taken(d, FIRST_WINDOW):
            return  # done

        # Not taken → send reminder and KEEP RUNNING to monitor
        now = datetime.now().strftime("%H:%M")
        print("⏰ Pill NOT taken within first window — sending reminder...")
        remind_patient(now, MED_NAME)

        print(f"Watching another {POST_REMINDER_WINDOW}s after reminder...")
        if wait_until_taken(d, POST_REMINDER_WINDOW):
            return

        # Optional: escalate here if you have that function
        # escalate_to_caregiver(now, MED_NAME)
        print("⚠️ Pill still not taken after reminder window. (Escalate here if desired.)")

        # Keep the program alive until user stops it, so you can continue monitoring or handle events.
        print("Press Ctrl+C to exit; continuing to idle-watch every 5s...")
        while True:
            # Light idle-watch; break if taken
            if d.get_ir() == "HIGH":
                print("✅ Pill taken (late)!")
                break
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nShutting down. Bye.")
    finally:
        d.close()

if __name__ == "__main__":
    main()
