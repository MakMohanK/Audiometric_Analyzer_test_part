from flask import Flask, render_template, request, jsonify
from pydub.generators import Sine
from pydub import AudioSegment
import pygame
import os
import time

app = Flask(__name__)

# Initialize pygame for sound playback
pygame.mixer.init()

# Define the frequency and decibel ranges
frequencies = list(range(30, 141, 10))  # Frequencies from 30Hz to 140Hz, step 10Hz
decibels = list(range(-50, -29, 5))     # Decibels from -50dB to -30dB, step 5dB

# To store user responses
user_responses = []


def is_file_in_use():
    file_path = "static/sound.wav"
    """Check if the file is currently in use by another process."""
    try:
        # Try opening the file in exclusive mode
        with open(file_path, 'a') as file:
            file.close()
            # If the file opens successfully, it is not being used by another process
            return False
    except IOError:
        # If an IOError occurs, it means the file is in use
        return True


# Function to generate sound
def generate_sound(freq, db):
    sine_wave = Sine(freq).to_audio_segment(duration=2000)  # 2-second sound
    sine_wave = sine_wave - abs(db)  # Adjust volume (in dB)

    # Ensure the directory exists
    if not os.path.exists("static"):
        os.makedirs("static")

    while True: # wait untill the resource is being free.
        if (is_file_in_use() == False):
            print("Continue with further exicution")
            break
        else:
            print(" Resource is utilised wait to get it free")

    # If the file already exists, remove it before creating a new one
    sound_file = "static/sound.wav"
    if os.path.exists(sound_file):
        try:
            os.remove(sound_file)
        except Exception as e:
            print(f"Error removing file: {e}")
            return

    # Export the sound to a file
    sine_wave.export(sound_file, format="wav")

# Function to play sound using pygame
def play_sound():
    # Initialize pygame for sound playback
    # time.sleep(0.15)
    pygame.mixer.init()
    while True: # wait untill the resource is being free.
        if (is_file_in_use() == False):
            print("Continue with further exicution")
            break
        else:
            print(" Resource is utilised wait to get it free")

    if os.path.exists("static/sound.wav"):
        try:
            pygame.mixer.music.load("static/sound.wav")
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)  # Wait until the sound is done playing
            
            # Stop the mixer after playing the sound to free the file
            pygame.mixer.music.stop()
            pygame.mixer.quit()  # Quits pygame and frees resources

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
        # Get current frequency and decibel value
        current_freq = frequencies[freq_idx]
        current_db = decibels[db_idx]

        # Generate and play sound
        generate_sound(current_freq, current_db)
        play_sound()

        return jsonify({
            "message": "Playing sound",
            "frequency": current_freq,
            "decibel": current_db
        }), 200
    else:
        # Test completed
        print("Test Completed\n",user_responses)
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
