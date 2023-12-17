from flask import Flask, render_template, Response
import cv2
from pyzbar.pyzbar import decode
import webbrowser
import threading
import tkinter as tk

app = Flask(__name__)
camera = cv2.VideoCapture(0)
qr_thread = None  # Placeholder for QR scanning thread

def generate_frames():
    global camera
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def get_qr_data():
    global camera
    global qr_thread
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            decoded_objs = decode(frame)
            if decoded_objs:
                for obj in decoded_objs:
                    qr_data = obj.data.decode('utf-8')
                    print('QR Data:', qr_data)
                    if qr_data.startswith('http'):
                        webbrowser.open(qr_data)  # Open the URL from the QR code

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_flask():
    global qr_thread
    qr_thread = threading.Thread(target=get_qr_data)
    qr_thread.daemon = True
    qr_thread.start()
    app.run(debug=False)

def open_browser():
    webbrowser.open('http://127.0.0.1:5000')

def stop_qr_scanner():
    global qr_thread
    if qr_thread and qr_thread.is_alive():
        qr_thread.join()  # Wait for QR thread to complete before stopping Flask
    camera.release()  # Release the camera
    cv2.destroyAllWindows()  # Close any OpenCV windows

def start_flask():
    threading.Thread(target=run_flask).start()

def start_gui():
    root = tk.Tk()
    root.title("QR Code Scanner")
    root.iconbitmap('C:\\Users\\LENOVO\\Downloads\\favicon (3).ico')  # Set the icon for the window

    label = tk.Label(root, text="Click below to start the QR Code Scanner:")
    label.pack()

    button = tk.Button(root, text="START QR SCANNER", command=start_flask)
    button.pack()

    stop_button = tk.Button(root, text="STOP QR SCANNER", command=stop_qr_scanner)
    stop_button.pack()

    open_button = tk.Button(root, text="OPEN QR SCANNER", command=open_browser)
    open_button.pack()

    root.mainloop()

threading.Thread(target=start_gui).start()
