🚗 Vehicle Detection and Tracking GUI using YOLOv8 and SORT
This is a Python GUI application built with Tkinter, which allows users to:

Load a video file.

Run object detection using a trained YOLOv8 model.

Track vehicles (car, bus, truck) using the SORT tracking algorithm.

Display real-time detection and tracking results.

Save detection/tracking logs to a CSV file.

✅ Features
👁️ Real-time object detection using your custom .pt YOLOv8 model.

🧠 Vehicle tracking using the SORT algorithm.

📺 Full video frame rendering in the GUI.

💾 Export detected vehicle info (frame time, bounding boxes, IDs) to CSV.

📤 Clean and minimal Tkinter-based user interface.

🛠️ Requirements
Install dependencies using:

bash
Copy
Edit
pip install ultralytics opencv-python pillow numpy filterpy
Ensure the following files are in your working directory:

your_model.pt – Trained YOLOv8 model.

sort.py – SORT tracker implementation.

▶️ How to Use
Run the script:

bash
Copy
Edit
python Image_Processing_test_5.py
Load a video by clicking the Load Video button.

Start detection by clicking Start Detection.

Watch vehicle detection and tracking in real time.

Click Save CSV to export results:

Format: Time(ms), TrackID, x1, y1, x2, y2

📁 Output
A .csv file with tracking logs.

Video display in GUI with real-time bounding boxes and Track IDs.

🧠 Internals
Detection: Powered by Ultralytics YOLOv8.

Tracking: SORT tracker (Simple Online Realtime Tracking).

Interface: Tkinter for simple GUI, OpenCV for video handling, and PIL for rendering.

🧩 Customization
To detect other classes, modify the line:

python
Copy
Edit
if int(cls) == 2 or int(cls) == 5:  # Car or Bus
using YOLO class indices.

Change video resize resolution:

python
Copy
Edit
resized_frame = cv2.resize(frame, (640, 384))
Replace "your_model.pt" with your actual YOLO model filename.

⚠️ Troubleshooting
ModuleNotFoundError: No module named 'sort'
→ Make sure sort.py is in the same directory.

Bounding box issues
→ Ensure YOLO model returns expected [x1, y1, x2, y2, score, class] format.

📦 Packaging
To build a standalone executable:

bash
Copy
Edit
pip install pyinstaller
pyinstaller --onefile --noconsole Image_Processing_test_5.py
📧 Author
Developed by: Supratim Mondal  
Contact: subhasupratim.mondal@gmail.com
