# main.py
from arduino import Dispenser
from datetime import datetime
import time
from vision import vision  # <- add this

from pill_reminder_simple import remind_patient  # expects remind_patient(time_str, med_name)

MED_NAME = "Scheduled medication"
DROP_DELAY = 1.0
FIRST_WINDOW = 30
POST_REMINDER_WINDOW = 60
HAND_GESTURE_TIMEOUT = 60  # 1 minute max to see "eaten"

IR_POLL_INTERVAL = 0.25
IR_HIGH_CONFIRMED_READS = 3

def read_ir(d: Dispenser) -> str:
    try:
        return d.get_ir()  # 'LOW' or 'HIGH'
    except Exception as e:
        print(f"[IR] read error: {e}")
        return "LOW"

def wait_for_ir_high_stable(d: Dispenser, timeout_s: int) -> bool:
    deadline = time.time() + timeout_s
    consecutive = 0
    while time.time() < deadline:
        state = read_ir(d)
        print("IR state:", state)
        if state == "HIGH":
            consecutive += 1
            if consecutive >= IR_HIGH_CONFIRMED_READS:
                print("✅ IR HIGH confirmed (pill removed).")
                return True
        else:
            consecutive = 0
        time.sleep(IR_POLL_INTERVAL)
    return False

def main():
    d = Dispenser()
    try:
        print("Dispensing pill...")
        d.turn_45()
        time.sleep(DROP_DELAY)

        print(f"Waiting up to {FIRST_WINDOW}s for pickup (IR HIGH)...")
        if not wait_for_ir_high_stable(d, FIRST_WINDOW):
            # Not picked up → remind, then keep watching
            now = datetime.now().strftime("%H:%M")
            print("⏰ Not picked up — sending reminder...")
            remind_patient(now, MED_NAME)

            print(f"Watching another {POST_REMINDER_WINDOW}s for pickup...")
            if not wait_for_ir_high_stable(d, POST_REMINDER_WINDOW):
                print("⚠️ Still not picked up after reminder window.")
                return  # or escalate if you have that hook

        # Picked up → verify hand-to-mouth with vision
        print("🎥 Starting vision check for hand-to-mouth...")
        vision.start_camera()  # safe to call even if already started

        eaten = False
        try:
            eaten = vision.wait_for_hand_to_mouth(timeout_s=HAND_GESTURE_TIMEOUT)
        finally:
            vision.stop_camera()

        if eaten:
            print("🎉 Vision: eaten confirmed. Cycle complete.")
            return

        # No gesture within 1 minute → remind via VAPI
        now = datetime.now().strftime("%H:%M")
        print("📞 No hand-to-mouth detected within 1 min — reminding patient via VAPI.")
        remind_patient(now, MED_NAME)

        # Optional: watch a bit more in case of late gesture
        print(f"Watching another {POST_REMINDER_WINDOW}s for late gesture...")
        vision.start_camera()
        try:
            if vision.wait_for_hand_to_mouth(timeout_s=POST_REMINDER_WINDOW):
                print("✅ Late eaten gesture detected — done.")
                return
        finally:
            vision.stop_camera()

        print("⚠️ No eaten gesture detected after reminder window.")
        # (Optional) escalate here

    except KeyboardInterrupt:
        print("\nShutting down. Bye.")
    finally:
        d.close()

if __name__ == "__main__":
    main()
