from flask import Flask, render_template, request, jsonify
from pydub.generators import Sine
from pydub import AudioSegment
from playsound import playsound
import threading

app = Flask(__name__)

# Define the frequency and decibel ranges
frequencies = list(range(30, 141, 10))  # Frequencies from 30Hz to 140Hz, step 10Hz
decibels = list(range(-50, -29, 5))     # Decibels from -50dB to -30dB, step 5dB

# To store user responses
user_responses = []

# Function to generate sound
def generate_sound(freq, db):
    sine_wave = Sine(freq).to_audio_segment(duration=2000)  # 2-second sound
    sine_wave = sine_wave - abs(db)  # Adjust volume (in dB)

    # Export the sound file and ensure it's saved correctly
    sine_wave.export("static/sound.wav", format="wav")

def play_sound():
    # Ensure the file exists and is accessible before playing
    import os
    if os.path.exists("static/sound.wav"):
        try:
            playsound("static/sound.wav")
        except Exception as e:
            print(f"Error playing sound: {e}")
    else:
        print("Sound file not found!")

# Serve the main page
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to start sound tests
@app.route('/start_sound_test', methods=['POST'])
def start_sound_test():
    global freq_idx, db_idx
    freq_idx = 0
    db_idx = 0
    user_responses.clear()  # Clear previous responses

    # Play the first sound
    return play_next_sound()

# Function to handle playing the next sound
def play_next_sound():
    global freq_idx, db_idx

    if freq_idx < len(frequencies):
        current_freq = frequencies[freq_idx]
        current_db = decibels[db_idx]

        # Generate sound and play it immediately
        generate_sound(current_freq, current_db)
        play_sound()

        return jsonify({
            "message": "Playing sound",
            "frequency": current_freq,
            "decibel": current_db
        }), 200
    else:
        # Test completed
        return jsonify({
            "message": "Test completed",
            "responses": user_responses
        }), 200

# Endpoint to record user response and move to the next sound
@app.route('/user_response', methods=['POST'])
def user_response():
    global freq_idx, db_idx

    # Record the user's response
    response = request.json.get('response')
    user_responses.append({
        "frequency": frequencies[freq_idx],
        "decibel": decibels[db_idx],
        "response": response
    })

    # Move to the next decibel value
    db_idx += 1
    if db_idx >= len(decibels):
        db_idx = 0
        freq_idx += 1

    # Play the next sound or complete the test
    return play_next_sound()

if __name__ == '__main__':
    app.run(debug=True)
