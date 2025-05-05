import cv2
import csv
import os
from tkinter import Tk, Button, Label, filedialog, Canvas, ttk
from PIL import Image, ImageTk
from ultralytics import YOLO
from threading import Thread

OCEAN_BLUE = "#5900be"
TEXT_COLOR = "#ffffff"

# Config
OBB_MODEL_PATH = "runs/obb/road_condition_obb_model2/weights/best.pt"  # Added missing variable
OUTPUT_VIDEO_PATH = os.path.join(os.getcwd(), "output", "output_annotated_video.mp4")
CSV_LOG_PATH = os.path.join(os.getcwd(), "output", "detections_log.csv")
FRAMES_DIR = os.path.join(os.getcwd(), "output", "extracted_frames")
LOGO_PATH = "C:\\Users\\Supratim\\Downloads\\Logo-removebg-preview.png"  # Update as needed

class RoadDefectApp:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg=OCEAN_BLUE)
        self.root.title("Road Defect Detection")
        self.root.geometry("800x800")
        self.video_path = ""
        self.output_dir = os.path.join(os.getcwd(), "output")  # Default output directory
        self.is_processing = False
        self.thread = None

        # Initialize UI elements first to avoid attribute errors
        self.canvas = Canvas(root, width=700, height=400, bg=OCEAN_BLUE, highlightthickness=0)
        self.canvas.pack(pady=10)
        self.progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(pady=10)
        self.status_label = Label(root, text="Select a video to start. Output will be saved to a user-selected directory.", font=("Arial", 12), bg=OCEAN_BLUE, fg=TEXT_COLOR)
        self.status_label.pack(pady=5)
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)
        Button(button_frame, text="🎞️ Select Video", command=self.select_video, bg="#005f99", fg=TEXT_COLOR).pack(side="left", padx=5)
        Button(button_frame, text="🔍 Start Detection", command=self.start_detection, bg="#005f99", fg=TEXT_COLOR).pack(side="left", padx=5)
        Button(button_frame, text="⏹️ Terminate Processing", command=self.terminate_processing, bg="#005f99", fg=TEXT_COLOR, state="disabled").pack(side="left", padx=5)
        self.terminate_button = button_frame.winfo_children()[-1]

        # Logo (after UI elements to ensure status_label is available)
        try:
            logo_image = Image.open(LOGO_PATH)
            logo_image.thumbnail((180, 180), Image.Resampling.LANCZOS)
            self.logo_tk = ImageTk.PhotoImage(logo_image)
            self.logo_label = Label(root, image=self.logo_tk, bg=OCEAN_BLUE)
            self.logo_label.pack(side="bottom", pady=10)
        except Exception as e:
            self.show_status(f"⚠️ Failed to load logo: {e}")
            self.logo_label = Label(root, text="Logo not found", bg=OCEAN_BLUE, fg=TEXT_COLOR)
            self.logo_label.pack(side="bottom", pady=10)

        # Model loading (after UI elements to ensure status_label is available)
        try:
            self.model = YOLO(OBB_MODEL_PATH)
        except Exception as e:
            self.show_status(f"⚠️ Failed to load model: {e}")
            return

    def show_status(self, message):
        self.status_label.config(text=message)

    def select_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        if self.video_path:
            self.show_status(f"Selected: {os.path.basename(self.video_path)}. Output will be saved to a user-selected directory.")
        else:
            self.show_status("⚠️ No video selected! Output will be saved to a user-selected directory.")

    def start_detection(self):
        if not self.video_path:
            self.show_status("⚠️ No video selected! Output will be saved to a user-selected directory.")
            return
        if self.is_processing:
            self.show_status("⚠️ Processing already in progress! Output will be saved to a user-selected directory.")
            return

        # Prompt user to select output directory
        self.output_dir = filedialog.askdirectory(title="Select Output Directory", initialdir=os.getcwd())
        if not self.output_dir:
            self.show_status(f"⚠️ No output directory selected! Output will be saved to default: {self.output_dir}")
            # self.output_dir remains the default

        # Update output paths with selected directory
        global OUTPUT_VIDEO_PATH, CSV_LOG_PATH, FRAMES_DIR
        OUTPUT_VIDEO_PATH = os.path.join(self.output_dir, "output_annotated_video.mp4")
        CSV_LOG_PATH = os.path.join(self.output_dir, "detections_log.csv")
        FRAMES_DIR = os.path.join(self.output_dir, "extracted_frames")
        os.makedirs(FRAMES_DIR, exist_ok=True)

        self.is_processing = True
        self.terminate_button.config(state="normal")
        self.thread = Thread(target=self.process_video)
        self.thread.start()

    def terminate_processing(self):
        if self.is_processing and self.thread:
            self.show_status(f"⏹️ Terminating processing... Output may be incomplete in: {self.output_dir}")
            self.thread.join(timeout=2)
            if self.thread.is_alive():
                import ctypes
                ctypes.windll.kernel32.TerminateThread(int(self.thread.ident), 0)
            self.is_processing = False
            self.terminate_button.config(state="disabled")
            self.show_status(f"✅ Processing terminated. Output saved to: {self.output_dir} (if any)")

    def process_video(self):
        self.show_status(f"🚀 Processing started... Output will be saved to: {self.output_dir}")
        os.makedirs(FRAMES_DIR, exist_ok=True)

        try:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                self.show_status(f"⚠️ Failed to open video! Output will be saved to: {self.output_dir}")
                self.is_processing = False
                self.terminate_button.config(state="disabled")
                return

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.progress["maximum"] = total_frames

            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(OUTPUT_VIDEO_PATH, fourcc, fps, (width, height))

            with open(CSV_LOG_PATH, mode='w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(["Frame", "Class", "Confidence", "X", "Y", "Width", "Height", "Rotation"])

                frame_num = 0
                while cap.isOpened() and self.is_processing:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    results = self.model.predict(frame, conf=0.5)[0]
                    save_frame = False

                    if hasattr(results, 'obb') and results.obb is not None and len(results.obb) > 0:
                        rboxes = results.obb.xywhr.cpu().numpy()
                        classes = results.obb.cls.cpu().numpy().astype(int)
                        confs = results.obb.conf.cpu().numpy()

                        for i, (xywhr, cls, conf) in enumerate(zip(rboxes, classes, confs)):
                            x, y, w, h, angle = xywhr
                            label = results.names[cls]
                            csv_writer.writerow([frame_num, label, round(conf, 2), x, y, w, h, angle])

                            rect = ((x, y), (w, h), angle * 180 / 3.14159)
                            box = cv2.boxPoints(rect)
                            box = box.astype(int)
                            cv2.polylines(frame, [box], True, (0, 255, 0), 2)
                            cv2.putText(frame, f"{label} {conf:.2f}", (int(x), int(y)-10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            save_frame = True

                        if save_frame:
                            frame_filename = os.path.join(FRAMES_DIR, f"frame_{frame_num}.jpg")
                            cv2.imwrite(frame_filename, frame)

                    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(img_rgb)
                    img_resized = img_pil.resize((700, 400))
                    img_tk = ImageTk.PhotoImage(img_resized)
                    self.canvas.create_image(0, 0, anchor="nw", image=img_tk)
                    self.canvas.image = img_tk

                    out.write(frame)
                    frame_num += 1
                    self.progress["value"] = frame_num
                    self.root.update_idletasks()

            cap.release()
            out.release()
            self.show_status(f"✅ Done! Output saved to: {self.output_dir}")
        except Exception as e:
            self.show_status(f"⚠️ Error during processing: {e}. Output saved to: {self.output_dir} (if any)")
        finally:
            self.is_processing = False
            self.terminate_button.config(state="disabled")

if __name__ == "__main__":
    app = Tk()
    RoadDefectApp(app)
    app.mainloop()
