# arduino.py — minimal API to control servo & read IR via an Arduino over USB serial.
# Usage:
#   from arduino import Dispenser
#   d = Dispenser()            # auto-detects port
#   d.turn_45()                # move servo +45° (wraps at 180->0)
#   print(d.get_ir())          # 'LOW' or 'HIGH'
#   d.on_ir_change(lambda s: print("IR changed:", s))  # async callbacks
#   ... later ...
#   d.close()

import glob, os, serial, threading, time

def _find_port():
    # Prefer descriptive symlinks
    by_id = sorted(glob.glob('/dev/serial/by-id/*'))
    if by_id:
        return os.path.realpath(by_id[0])
    # Fallback to common names
    ports = sorted(glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*'))
    if not ports:
        raise RuntimeError("No serial ports found (plug in the Arduino).")
    return ports[0]

class Dispenser:
    def __init__(self, port: str | None = None, baud: int = 9600):
        self.port = port or _find_port()
        self.ser = serial.Serial(self.port, baud, timeout=0.3)
        time.sleep(2.0)  # let Uno reset
        self._ir_state = None
        self._callbacks = []
        self._stop = False
        self._rx_thread = threading.Thread(target=self._reader, daemon=True)
        self._rx_thread.start()
        # Drain boot lines and remember last IR state if sent
        t0 = time.time()
        while time.time() - t0 < 2.0:
            line = self._readline_nowait()
            if not line:
                break
            self._handle_line(line)

    # -------- public API --------
    def turn_45(self):
        self._send("TURN\n")
        # optional: wait for OK
        self._wait_for_prefix("OK angle=", timeout=1.0)

    def set_angle(self, angle: int):
        self._send(f"SET {int(angle)}\n")
        self._wait_for_prefix("OK angle=", timeout=1.0)

    def get_ir(self) -> str:
        """Returns 'LOW' (beam blocked/pill present) or 'HIGH' (clear)."""
        self._send("IR?\n")
        line = self._wait_for_prefix("IR=", timeout=1.0)
        if not line:
            # fall back to last seen push message
            return self._ir_state or "UNKNOWN"
        state = line.split("=", 1)[1].strip()
        self._ir_state = state
        return state

    def on_ir_change(self, callback):
        """Register a callback: callback(state_str) where state_str is 'LOW'/'HIGH'."""
        self._callbacks.append(callback)

    def close(self):
        self._stop = True
        try:
            self._rx_thread.join(timeout=0.5)
        except Exception:
            pass
        try:
            self.ser.close()
        except Exception:
            pass

    # -------- internals --------
    def _send(self, data: str):
        self.ser.write(data.encode())

    def _readline_nowait(self) -> str | None:
        try:
            line = self.ser.readline().decode(errors='ignore').strip()
            return line if line else None
        except Exception:
            return None

    def _wait_for_prefix(self, prefix: str, timeout: float = 1.0) -> str | None:
        t0 = time.time()
        while time.time() - t0 < timeout:
            line = self._readline_nowait()
            if not line:
                continue
            if line.startswith(prefix):
                return line
            # still process other useful lines (like IR pushes)
            self._handle_line(line)
        return None

    def _handle_line(self, line: str):
        # Examples: "READY", "OK angle=45", "IR=LOW", "IR:HIGH"
        if line.startswith("IR="):
            self._ir_state = line.split("=",1)[1].strip()
        elif line.startswith("IR:"):
            state = line.split(":",1)[1].strip()
            self._ir_state = state
            for cb in self._callbacks:
                try:
                    cb(state)
                except Exception:
                    pass
        # You could log/print other lines if desired.

    def _reader(self):
        while not self._stop:
            line = self._readline_nowait()
            if line:
                self._handle_line(line)
            else:
                time.sleep(0.01)
