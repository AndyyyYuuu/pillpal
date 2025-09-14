#include <Servo.h>

/* ================= Pins ================= */
const int SERVO_PIN  = 9;    // servo signal
const int IR_PIN     = 2;    // break-beam receiver OUT (active-LOW with INPUT_PULLUP)
const int BUTTON_PIN = 12;   // button to GND (uses INPUT_PULLUP)
const int LED_PIN    = LED_BUILTIN; // status LED (onboard pin 13)

/* ============== Servo config ============== */
Servo myServo;
int angle = 0;                 // current target angle 0..180
const int OVERSHOOT = 3;       // degrees to overshoot to break friction
const int SETTLE_MS = 200;     // ms to wait at overshoot before target
const int POST_MOVE_MS = 60;   // small pause after final write

/* ============== IR filter ============== */
/* confirm a new IR state only after it remains stable long enough */
const unsigned long STABLE_LOW_MS  = 120; // confirm LOW (blocked/present) quickly
const unsigned long STABLE_HIGH_MS = 700; // confirm HIGH (clear/taken) slower

int stableIR;                  // last confirmed state (LOW/HIGH)
int candidateIR;               // candidate state we are timing
unsigned long candidateSince;  // when candidateIR started

/* ============== Button debounce (edge) ============== */
bool btnStable = HIGH;         // INPUT_PULLUP idle HIGH
bool btnLastReported = HIGH;
unsigned long btnChangedAt = 0;
const unsigned long BTN_DEBOUNCE_MS = 25;

/* ============== Serial helpers ============== */
String readLine() {
  static String buf;
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (buf.length()) { String out = buf; buf = ""; return out; }
    } else {
      buf += c;
    }
  }
  return "";
}

void sendIRPush(int v) {
  Serial.print("IR:");
  Serial.println(v == LOW ? "LOW" : "HIGH");
}

void sendIROneShot(int v) {
  Serial.print("IR=");
  Serial.println(v == LOW ? "LOW" : "HIGH");
}

/* ============== Motion ============== */
void moveTo(int target) {
  target = constrain(target, 0, 180);

  if (target > angle) {
    int over = min(target + OVERSHOOT, 180);
    myServo.write(over);
    delay(SETTLE_MS);
  } else if (target < angle) {
    int over = max(target - OVERSHOOT, 0);
    myServo.write(over);
    delay(SETTLE_MS);
  }

  angle = target;
  myServo.write(angle);
  delay(POST_MOVE_MS);

  Serial.print("OK angle=");
  Serial.println(angle);
}

/* ============== IR filtering ============== */
void updateIR() {
  int raw = digitalRead(IR_PIN);
  unsigned long now = millis();

  if (raw != candidateIR) {
    candidateIR = raw;
    candidateSince = now;
  }

  unsigned long need = (candidateIR == HIGH) ? STABLE_HIGH_MS : STABLE_LOW_MS;
  if (candidateIR != stableIR && (now - candidateSince) >= need) {
    stableIR = candidateIR;
    sendIRPush(stableIR);                             // push event to Pi
    digitalWrite(LED_PIN, (stableIR == LOW) ? HIGH : LOW); // LED on when blocked
  }
}

/* ============== Button edge detector ============== */
bool buttonPressedEdge() {
  bool raw = digitalRead(BUTTON_PIN);
  unsigned long now = millis();

  if (raw != btnStable) {
    btnStable = raw;
    btnChangedAt = now;
  }

  if ((now - btnChangedAt) >= BTN_DEBOUNCE_MS) {
    if (btnStable != btnLastReported) {
      bool was = btnLastReported;
      btnLastReported = btnStable;
      if (was == HIGH && btnStable == LOW) {
        // falling edge = press
        return true;
      }
    }
  }
  return false;
}

/* ============== Setup ============== */
void setup() {
  pinMode(LED_PIN, OUTPUT);

  // IR input (active-LOW). If your module is active-HIGH, change to INPUT and invert prints.
  pinMode(IR_PIN, INPUT_PULLUP);
  stableIR = digitalRead(IR_PIN);
  candidateIR = stableIR;
  candidateSince = millis();
  digitalWrite(LED_PIN, (stableIR == LOW) ? HIGH : LOW);

  pinMode(BUTTON_PIN, INPUT_PULLUP);

  myServo.attach(SERVO_PIN);
  myServo.write(angle);

  Serial.begin(9600);
  delay(20);
  Serial.println("READY");
  sendIRPush(stableIR);  // announce initial IR state
}

/* ============== Loop ============== */
void loop() {
  /* 1) Always keep IR filter alive + LED reflecting IR */
  updateIR();

  /* 2) Button: on debounced press, notify the Pi (or your main script) */
  if (buttonPressedEdge()) {
    Serial.println("BTN:PRESS");
  }

  /* 3) Handle serial commands from Raspberry Pi */
  String cmd = readLine();
  if (cmd.length()) {
    if (cmd == "TURN") {
      int next = angle + 45;
      if (next > 180) next = 0;  // wrap
      moveTo(next);

    } else if (cmd.startsWith("SET ")) {
      int req = cmd.substring(4).toInt();
      moveTo(req);

    } else if (cmd == "IR?") {
      sendIROneShot(stableIR);

    } else if (cmd == "PING") {
      Serial.println("PONG");

    } else {
      Serial.print("ERR unknown: ");
      Serial.println(cmd);
    }
  }

  // small idle delay to avoid busy-looping
  delay(5);
}
