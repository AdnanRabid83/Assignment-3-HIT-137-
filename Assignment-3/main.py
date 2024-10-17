import tkinter as tk
from tkinter import filedialog, Label, Button, Frame
from PIL import Image, ImageTk
import tensorflow as tf
import numpy as np

# AI Model Loading (mockup using MobileNetV2)
def load_model():
    model = tf.keras.applications.MobileNetV2(weights='imagenet')
    return model

# Class for managing file input/output
class FileManager:
    def __init__(self):
        self.filepath = None

    def open_file(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png")])
        return self.filepath

    def get_filepath(self):
        return self.filepath

# Main YouTube-like Tkinter App
class YouTubeLikeApp(tk.Tk, FileManager):  # Multiple Inheritance
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.title("YouTube-Like Image Classifier")
        self.geometry("800x600")
        self.configure(bg="#f9f9f9")  # Light YouTube-like background color

        # Creating a Frame to hold the "video"
        self.video_frame = Frame(self, width=480, height=270, bg="black")  # Mimics YouTube video frame
        self.video_frame.pack(pady=20)
        self.video_frame.pack_propagate(0)  # Prevents the frame from resizing

        # Label to display the image/video in the "video frame"
        self.image_label = Label(self.video_frame, bg="black")
        self.image_label.pack(expand=True)

        # Frame for buttons (like YouTube buttons below the video)
        self.button_frame = Frame(self, bg="#f9f9f9")
        self.button_frame.pack(pady=10)

        # Upload Button (acts as the "upload/play" button)
        self.button_upload = Button(self.button_frame, text="Upload Image", command=self.upload_image, font=("Arial", 12), bg="#ff0000", fg="white")
        self.button_upload.grid(row=0, column=0, padx=10)

        # Classify Button (acts as the "play" button)
        self.button_classify = Button(self.button_frame, text="Classify Image", command=self.classify_image, font=("Arial", 12), bg="#00ff00", fg="white")
        self.button_classify.grid(row=0, column=1, padx=10)

        # Frame for results (similar to YouTube's description/comments section)
        self.results_frame = Frame(self, bg="#f9f9f9")
        self.results_frame.pack(pady=10)

        # Label to display classification result
        self.result_label = Label(self.results_frame, text="Classification result will appear here...", font=("Arial", 12), bg="#f9f9f9")
        self.result_label.pack()

        # Image to store the uploaded image
        self.image = None

    def upload_image(self):
        self.filepath = self.open_file()  # Inherited from FileManager
        if self.filepath:
            img = Image.open(self.filepath)
            img = img.resize((480, 270))  # Resize to fit in the "video frame"
            self.image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.image)

    def classify_image(self):
        if self.filepath:
            img = Image.open(self.filepath)
            img = img.resize((224, 224))  # Resize for model input
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            predictions = self.model.predict(img_array)
            decoded_preds = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=1)[0]
            result = f"Prediction: {decoded_preds[0][1]}, Confidence: {decoded_preds[0][2]*100:.2f}%"
            self.result_label.config(text=result)
        else:
            self.result_label.config(text="Please upload an image first.")

# Regular function to run the app
def run_image_classifier_app():
    model = load_model()  # Loading AI model
    app = YouTubeLikeApp(model)  # Creating an instance of the class
    app.mainloop()  # Start the Tkinter GUI loop

# Running the application
if __name__ == "__main__":
    run_image_classifier_app()
