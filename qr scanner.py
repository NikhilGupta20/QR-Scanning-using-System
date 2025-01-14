import cv2
import webbrowser
import numpy as np
import datetime
import sys
import ctypes
import threading

# Function to get screen dimensions
def get_screen_resolution():
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    return screen_width, screen_height

# Function to calculate window position
def calculate_window_position(window_width, window_height):
    screen_width, screen_height = get_screen_resolution()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    return x, y

def scan_qr_and_open_link():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        sys.exit(1)

    detector = cv2.QRCodeDetector()
    zoom_level = 1.0
    log_file = open("scanned_qr_log.txt", "a")

    qr_code_data = None
    try:
        start_time = datetime.datetime.now()
        while (datetime.datetime.now() - start_time).seconds < 30:  # Scan for up to 30 seconds
            ret, img = cap.read()
            if not ret:
                print("Failed to capture image")
                break

            data, bbox, _ = detector.detectAndDecode(img)
            if data:
                qr_code_data = data
                if bbox is not None and len(bbox) > 0:
                    qr_size = np.amax(bbox[0, 2:])
                    zoom_level = max(1.0, 100.0 / qr_size)
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_file.write(f"Scanned QR Code: {qr_code_data}, Date/Time: {current_time}\n")
                    log_file.flush()
                break

            resized_img = cv2.resize(img, None, fx=zoom_level, fy=zoom_level)
            window_name = "QR Code Scanner"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.moveWindow(window_name, *calculate_window_position(resized_img.shape[1], resized_img.shape[0]))

            # Display instructions to close the window
            instructions = "Scan QR Code..."
            cv2.putText(resized_img, instructions, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow(window_name, resized_img)
            cv2.waitKey(1)  # Needed for imshow to process events

    finally:
        log_file.close()
        cap.release()
        cv2.destroyAllWindows()

    if qr_code_data:
        webbrowser.open(str(qr_code_data))
    else:
        print("No QR code detected.")

def main():
    # Start the QR code scanning in a separate thread
    qr_thread = threading.Thread(target=scan_qr_and_open_link)
    qr_thread.start()

if __name__ == "__main__":
    main()