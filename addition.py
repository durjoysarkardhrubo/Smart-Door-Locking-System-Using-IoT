import RPi.GPIO as GPIO
import time
from flask import Flask, render_template, request, redirect, url_for

# GPIO setup
SERVO_PIN = 17  # GPIO pin connected to the servo motor
BUTTON_LOCK_PIN = 27  # GPIO pin for lock button
BUTTON_UNLOCK_PIN = 22  # GPIO pin for unlock button

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(BUTTON_LOCK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_UNLOCK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize servo
servo = GPIO.PWM(SERVO_PIN, 50)  # 50Hz PWM frequency
servo.start(0)

app = Flask(__name__)

# Lock and Unlock positions (modify these angles based on your servo)
LOCK_ANGLE = 0
UNLOCK_ANGLE = 90

def set_servo_angle(angle):
    duty = angle / 18 + 2
    GPIO.output(SERVO_PIN, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(SERVO_PIN, False)
    servo.ChangeDutyCycle(0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lock', methods=['POST'])
def lock():
    set_servo_angle(LOCK_ANGLE)
    return redirect(url_for('index'))

@app.route('/unlock', methods=['POST'])
def unlock():
    set_servo_angle(UNLOCK_ANGLE)
    return redirect(url_for('index'))

def button_callback(channel):
    if channel == BUTTON_LOCK_PIN:
        print("Lock button pressed")
        set_servo_angle(LOCK_ANGLE)
    elif channel == BUTTON_UNLOCK_PIN:
        print("Unlock button pressed")
        set_servo_angle(UNLOCK_ANGLE)

# Add event detection for buttons
GPIO.add_event_detect(BUTTON_LOCK_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)
GPIO.add_event_detect(BUTTON_UNLOCK_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)

# HTML template for the web interface
html_content = """
<!doctype html>
<html lang="en">
  <head>
    <title>Smart Door Lock</title>
  </head>
  <body>
    <h1>Smart Door Lock Control</h1>
    <form action="/lock" method="post">
      <button type="submit">Lock</button>
    </form>
    <form action="/unlock" method="post">
      <button type="submit">Unlock</button>
    </form>
  </body>
</html>
"""

# Write the HTML template to the templates folder
import os
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
if not os.path.exists(template_dir):
    os.makedirs(template_dir)
with open(os.path.join(template_dir, 'index.html'), 'w') as f:
    f.write(html_content)

if __name__ == '__main__':
    try:
        # Start Flask app
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        pass
    finally:
        servo.stop()
        GPIO.cleanup()
