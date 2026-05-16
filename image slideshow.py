from itertools import cycle
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, Scale

# =========================================
# MAIN WINDOW
# =========================================

root = tk.Tk()
root.title("✨ Modern Image Slideshow Viewer")
root.geometry("1300x950")
root.configure(bg="#0f172a")

# =========================================
# VARIABLES
# =========================================

image_size = (900, 650)

image_paths = [
    r'/Users/pranshnayyar/Desktop/ganeshji2.jpeg',
    r'/Users/pranshnayyar/Desktop/gggg.jpeg'
]

images = []
current_index = 0
running = False
speed = 3000

# =========================================
# LOAD IMAGES
# =========================================

def load_images():

    global images, slideshow

    images.clear()

    for path in image_paths:

        try:
            img = Image.open(path)

            img.thumbnail(image_size)

            photo = ImageTk.PhotoImage(img)

            images.append(photo)

        except Exception as e:
            print(f"Error loading {path}: {e}")

    slideshow = cycle(images)

# Load images initially
load_images()

# =========================================
# HEADER
# =========================================

title = tk.Label(
    root,
    text="📸 Interactive Slideshow Viewer",
    font=("Helvetica", 30, "bold"),
    bg="#0f172a",
    fg="white"
)

title.pack(pady=15)

# =========================================
# IMAGE FRAME
# =========================================

frame = tk.Frame(
    root,
    bg="#1e293b",
    bd=0
)

frame.pack(pady=20)

# =========================================
# IMAGE LABEL
# =========================================

label = tk.Label(
    frame,
    bg="#1e293b"
)

label.pack(padx=25, pady=25)

# =========================================
# IMAGE NAME LABEL
# =========================================

image_name_label = tk.Label(
    root,
    text="",
    font=("Helvetica", 14, "bold"),
    bg="#0f172a",
    fg="#38bdf8"
)

image_name_label.pack()

# =========================================
# SHOW IMAGE FUNCTION
# =========================================

def show_image(index):

    global current_index

    if not images:
        return

    current_index = index % len(images)

    img = images[current_index]

    label.config(image=img)
    label.image = img

    image_counter.config(
        text=f"Image {current_index + 1} / {len(images)}"
    )

    image_name = image_paths[current_index].split("/")[-1]

    image_name_label.config(
        text=f"🖼 {image_name}"
    )

# =========================================
# AUTO SLIDESHOW
# =========================================

def auto_slide():

    global running

    if running:

        next_image()

        root.after(speed, auto_slide)

# =========================================
# BUTTON FUNCTIONS
# =========================================

def start_slideshow():

    global running

    if not running:

        running = True

        auto_slide()

        status_label.config(
            text="▶ Slideshow Running",
            fg="#22c55e"
        )

def stop_slideshow():

    global running

    running = False

    status_label.config(
        text="⏸ Slideshow Paused",
        fg="#facc15"
    )

def next_image():

    global current_index

    current_index += 1

    show_image(current_index)

def previous_image():

    global current_index

    current_index -= 1

    show_image(current_index)

# =========================================
# KEYBOARD CONTROLS
# =========================================

def key_controls(event):

    if event.keysym == "Right":
        next_image()

    elif event.keysym == "Left":
        previous_image()

    elif event.keysym == "space":

        if running:
            stop_slideshow()
        else:
            start_slideshow()

root.bind("<Right>", key_controls)
root.bind("<Left>", key_controls)
root.bind("<space>", key_controls)

# =========================================
# ADD IMAGES
# =========================================

def add_image():

    files = filedialog.askopenfilenames(
        title="Select Images",
        filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg *.gif")
        ]
    )

    if files:

        for file in files:
            image_paths.append(file)

        load_images()

        show_image(current_index)

        status_label.config(
            text="✅ New Images Added",
            fg="#38bdf8"
        )

# =========================================
# REMOVE CURRENT IMAGE
# =========================================

def remove_current_image():

    global current_index

    if len(image_paths) <= 1:

        status_label.config(
            text="❌ Cannot remove last image",
            fg="red"
        )

        return

    image_paths.pop(current_index)

    load_images()

    current_index = 0

    show_image(current_index)

    status_label.config(
        text="🗑 Image Removed",
        fg="#f87171"
    )

# =========================================
# SPEED CONTROL
# =========================================

def change_speed(val):

    global speed

    speed = int(val)

speed_label = tk.Label(
    root,
    text="⏱ Slideshow Speed",
    font=("Helvetica", 13),
    bg="#0f172a",
    fg="white"
)

speed_label.pack(pady=(10, 0))

speed_slider = Scale(
    root,
    from_=1000,
    to=10000,
    orient="horizontal",
    length=350,
    bg="#0f172a",
    fg="white",
    troughcolor="#334155",
    highlightthickness=0,
    command=change_speed
)

speed_slider.set(speed)

speed_slider.pack()

# =========================================
# CONTROLS FRAME
# =========================================

controls = tk.Frame(
    root,
    bg="#0f172a"
)

controls.pack(pady=20)

# =========================================
# BUTTON STYLE
# =========================================

button_style = {
    "font": ("Helvetica", 14, "bold"),
    "padx": 20,
    "pady": 12,
    "bd": 0,
    "cursor": "hand2"
}

# =========================================
# BUTTONS
# =========================================

prev_btn = tk.Button(
    controls,
    text="⏮ Previous",
    bg="#334155",
    fg="white",
    command=previous_image,
    **button_style
)

prev_btn.grid(row=0, column=0, padx=10)

play_btn = tk.Button(
    controls,
    text="▶ Play",
    bg="#22c55e",
    fg="white",
    command=start_slideshow,
    **button_style
)

play_btn.grid(row=0, column=1, padx=10)

pause_btn = tk.Button(
    controls,
    text="⏸ Pause",
    bg="#eab308",
    fg="black",
    command=stop_slideshow,
    **button_style
)

pause_btn.grid(row=0, column=2, padx=10)

next_btn = tk.Button(
    controls,
    text="⏭ Next",
    bg="#334155",
    fg="white",
    command=next_image,
    **button_style
)

next_btn.grid(row=0, column=3, padx=10)

add_btn = tk.Button(
    controls,
    text="➕ Add Images",
    bg="#3b82f6",
    fg="white",
    command=add_image,
    **button_style
)

add_btn.grid(row=0, column=4, padx=10)

remove_btn = tk.Button(
    controls,
    text="🗑 Remove",
    bg="#ef4444",
    fg="white",
    command=remove_current_image,
    **button_style
)

remove_btn.grid(row=0, column=5, padx=10)

# =========================================
# IMAGE COUNTER
# =========================================

image_counter = tk.Label(
    root,
    text="",
    font=("Helvetica", 15),
    bg="#0f172a",
    fg="#cbd5e1"
)

image_counter.pack(pady=5)

# =========================================
# STATUS LABEL
# =========================================

status_label = tk.Label(
    root,
    text="✨ Ready",
    font=("Helvetica", 13),
    bg="#0f172a",
    fg="#38bdf8"
)

status_label.pack(pady=10)

# =========================================
# FOOTER
# =========================================

footer = tk.Label(
    root,
    text="Built with Python + Tkinter + Pillow 💙",
    font=("Helvetica", 11),
    bg="#0f172a",
    fg="#64748b"
)

footer.pack(side="bottom", pady=15)

# =========================================
# SHOW FIRST IMAGE
# =========================================

show_image(0)

# =========================================
# RUN APP
# =========================================

root.mainloop()
<!DOCTYPE html>
<html>
<head>
    <title>Image Slideshow</title>
    <style>
        body { background: #0f172a; text-align: center; }
        img { max-width: 900px; margin: 20px auto; }
    </style>
</head>
<body>
    <h1>📸 Image Slideshow</h1>
    <img id="slideshow" src="images/image1.jpg" />
    <script>
        // Your slideshow logic here
    </script>
</body>
</html>
