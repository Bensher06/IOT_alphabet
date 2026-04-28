import eventlet
import socketio
import serial
import speech_recognition as sr
import threading
import time
import sys
import os
from pathlib import Path

# --- 1. HARDWARE CONFIGURATION ---
ARDUINO_PORT = 'COM3' 
BAUD_RATE = 115200

# --- 2. THE ULTIMATE PHONETIC TRAINING MAP ---
training_map = {
    # Numbers 1-10
    "one": "1", "won": "1", "on": "1", "want": "1", "un": "1", "wan": "1", 
    "two": "2", "too": "2", "to": "2", "do": "2", "tu": "2",
    "three": "3", "tree": "3", "free": "3", "the": "3",
    "four": "4", "for": "4", "fore": "4", "pour": "4",
    "five": "5", "fine": "5", "hive": "5", "fire": "5",
    "six": "6", "sex": "6", "sick": "6", "sics": "6",
    "seven": "7", "sever": "7", "heaven": "7",
    "eight": "8", "ate": "8", "ait": "8", "eat": "8",
    "nine": "9", "line": "9", "mine": "9", "night": "9",
    "ten": "10", "tin": "10", "then": "10",

    # Alphabet A-Z (Start-words)
    "ape": "A", "axe": "A", "air": "A", "art": "A", "apple": "A",
    "boy": "B", "ball": "B", "bat": "B", "bee": "B",
    "sea": "C", "city": "C", "see": "C",
    "dog": "D", "dad": "D", "dot": "D", "door": "D",
    "egg": "E", "eat": "E", "ear": "E", "eye": "E",
    "fan": "F", "fox": "F", "fish": "F",
    "giraffe": "G", "giant": "G", "goat": "G",
    "each": "H", "eight": "H", "hat": "H",
    "ice": "I", "ink": "I", "iron": "I",
    "jar": "J", "jet": "J", "job": "J",
    "key": "K", "king": "K", "kite": "K",
    "log": "L", "leg": "L", "lion": "L",
    "man": "M", "map": "M", "milk": "M",
    "nut": "N", "net": "N", "now": "N",
    "owl": "O", "oil": "O", "old": "O",
    "pen": "P", "pig": "P", "pin": "P",
    "queen": "Q", "quit": "Q", "quiz": "Q",
    "rat": "R", "run": "R", "register": "R", "reason": "R", "rabbit": "R", "river": "R", "ride": "R", "ride": "R",
    "sun": "S", "sit": "S", "star": "S",
    "top": "T", "ten": "T", "toy": "T",
    "up": "U", "us": "U", "unit": "U", "you": "U",
    "van": "V", "vet": "V", "view": "V",
    "wet": "W", "win": "W", "web": "W",
    "x-ray": "X", "box": "X",
    "yes": "Y", "why": "Y",
    "zoo": "Z", "zip": "Z", "zero": "Z"
}

whitelists = {
    "alphabet": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    "number": [str(i) for i in range(1, 11)],
    "shape": ["circle", "square", "triangle", "rectangle", "oblong", "diamond"],
    "color": ["red", "blue", "green", "yellow", "orange", "purple"]
}

# --- 3. SYSTEM STATE ---
BASE_DIR = Path(__file__).resolve().parent
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(
    sio,
    static_files={
        "/": str(BASE_DIR / "index.html"),
    },
)
current_mode = "alphabet"
arduino = None

def connect_arduino():
    global arduino
    try:
        if arduino: arduino.close()
        arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=0.1)
        time.sleep(2)
        print(f"✅ Hardware Linked: {ARDUINO_PORT}")
    except:
        print("⚠️ Hardware Not Found. Retrying...")
        arduino = None

@sio.on('change_category')
def change_category(sid, data):
    global current_mode
    current_mode = data
    print(f"🔄 MODE SWITCHED: {current_mode.upper()}")

def voice_thread():
    global arduino
    rec = sr.Recognizer()
    rec.dynamic_energy_threshold = True 
    
    with sr.Microphone() as source:
        print("🎙️ Calibrating... Speak clearly.")
        rec.adjust_for_ambient_noise(source, duration=2)
        print("✅ READY.")
        
        while True:
            try:
                audio = rec.listen(source, phrase_time_limit=2)
                raw_input = rec.recognize_google(audio).lower().strip()
                
                # --- ENHANCED PHRASE & REPETITION HANDLING ---
                words = raw_input.split()
                match_found = False

                # 1. First, check if the ENTIRE phrase is a multi-word color (like "red red")
                # We normalize the input by removing the repetition for the whitelist check
                unique_words = sorted(list(set(words)), key=words.index)
                collapsed_input = " ".join(unique_words)

                for word in words:
                    # Apply phonetic mapping
                    processed = training_map.get(word, word)
                    
                    # Alphabet logic: First letter fallback
                    if current_mode == "alphabet" and len(processed) > 1:
                        processed = processed[0].upper()
                    
                    # Normalize
                    final_val = processed.upper() if current_mode == "alphabet" else processed.lower()
                    
                    # Validation
                    if final_val in whitelists[current_mode]:
                        print(f"🎯 VALID MATCH: {final_val} (From: {raw_input})")
                        sio.emit('voice_match', {'word': final_val, 'mode': current_mode})
                        
                        if arduino:
                            try:
                                arduino.write(f"{final_val}\n".encode())
                                match_found = True
                                break 
                            except serial.SerialException:
                                connect_arduino()
                        else:
                            connect_arduino()
                
                if not match_found:
                    print(f"☁️ IGNORED: {raw_input}")

            except sr.UnknownValueError:
                pass 
            except Exception as e:
                print(f"⚠️ Voice Error: {e}")

if __name__ == '__main__':
    connect_arduino()
    threading.Thread(target=voice_thread, daemon=True).start()
    print(f"🌐 Web + API live at http://{HOST}:{PORT}")
    eventlet.wsgi.server(eventlet.listen((HOST, PORT)), app)