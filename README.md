# Epic Photo Editor

A desktop photo editing application built with **Python and Tkinter** that provides drawing tools, image adjustments, cropping, shape insertion, and undo/redo functionality.

The editor allows users to open images, edit them directly on a canvas, and export the final result.

---

## Features

### Image Management
- Open image files (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.gif`)
- Save edited images
- Save selected portions of the canvas
- Clear the canvas

### Drawing Tools
- Freehand paint tool
- Adjustable brush thickness
- Color picker
- Eraser tool

### Shape Tools
- Draw rectangles
- Draw ovals
- Draw lines
- Optional shape fill color
- Adjustable outline thickness

### Image Editing
- Brightness adjustment
- Saturation adjustment
- Sharpness adjustment

### Canvas Tools
- Crop selected areas
- Fill canvas with color

### Editing Utilities
- Undo
- Redo

---

## Tech Stack

- **Python**
- **Tkinter** (GUI)
- **Pillow (PIL)** for image processing
- **ImageGrab** for capturing canvas content


---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/epic-photo-editor.git
cd epic-photo-editor
```

### 2. Install dependencies

```bash
pip install pillow
```

Tkinter is included with most Python installations.

---

## Running the Application

```bash
python main.py
```

The editor will open in a fullscreen window.

---

## How to Use

### Opening an Image
1. Go to **File → Open**
2. Select an image file

### Drawing
1. Select the **Paint Tool**
2. Choose a color and thickness
3. Drag the mouse on the canvas

### Erasing
1. Select the **Erase Tool**
2. Drag across the canvas to remove drawings

### Shapes
1. Select the **Shape Tool**
2. Choose rectangle, oval, or line
3. Drag on the canvas to draw

### Cropping
1. Select the **Crop Tool**
2. Drag to select the area
3. Confirm crop in the popup window

### Image Adjustments
Use the **Image Settings** tool to adjust:
- Brightness
- Saturation
- Sharpness

### Saving
- **File → Save** to export the full canvas
- **File → Partial Save** to save a selected area

---

## Requirements

- Python 3.8+
- Pillow

---

## License

MIT License
