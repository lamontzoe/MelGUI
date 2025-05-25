# Melanoma Detection & Observation Tool

This application allows users to leverage a machine learning model to analyze skin lesions for potential melanoma. Users can manage profiles, scan new lesions, track their history, and monitor changes over time through an intuitive graphical user interface.

## Dependencies

This project relies on the following Python libraries:

- **PyQt5:** For the graphical user interface.
- **ultralytics:** For the YOLOv8 machine learning model used for lesion analysis.
- **OpenCV-Python (cv2):** For image processing tasks.

You can install these dependencies using pip:

```bash
pip install PyQt5 ultralytics opencv-python
```

## Model Setup

The application requires a pre-trained YOLO model file named `best.pt` located in the `models/` directory. This file is included in the repository and is necessary for the lesion analysis functionality.

Ensure the `models/best.pt` file is present before running the application.

## How to Run

Once the dependencies are installed and the model file is in place, you can run the application directly from the source code.

Navigate to the root directory of the project in your terminal and execute the following command:

```bash
python src/main.py
```

## GUI Usage

The application features a tab-based interface for easy navigation:

- **Profiles Tab:**
  - Manage user profiles for different individuals.
  - Create new profiles, select existing ones, or delete profiles.
  - Profile data is stored in `profiles.json` in the `src/` directory and scan data within `profile_scans/`.

- **Scan Tab:**
  - Once a profile is selected, you can start a new scan.
  - Click on the body map to indicate the location of the lesion.
  - Upload a clear photo of the lesion.
  - The application will then analyze the image using the ML model and display the risk assessment results. Analyzed images are saved in the respective profile's folder within `profile_scans/`.

- **Monitor Tab:**
  - View the history of scans for the currently selected profile.
  - Track changes and observations over time.

- **About Tab:**
  - Provides general information about the application.

- **Settings Tab:**
  - Allows for adjustment of application preferences (if any are implemented).

## Project Structure

Key directories in the project include:

- `src/`: Contains the main Python source code for the application, including GUI components, inference logic, and profile management.
- `models/`: Stores the pre-trained machine learning model (`best.pt`) used for lesion analysis.
- `profile_scans/`: This directory is created automatically and stores user-specific data, including uploaded scan images and their analysis results, organized by profile ID.
- `Resources/`: Contains icon files and other static resources used by the GUI.

## Building the Executable (Optional)

This project is configured to be bundled into a standalone executable using PyInstaller. This allows you to run the application without needing a Python interpreter or installing dependencies manually on the target machine.

**Prerequisites for Building:**

1.  **Python Environment:** You'll need a Python environment (preferably the same version used for development, e.g., Python 3.9+) on the machine where you intend to build the executable.
2.  **PyInstaller:** Install PyInstaller in your Python environment:
    ```bash
    pip install pyinstaller
    ```
3.  **Python Shared Library:** PyInstaller requires your Python installation to have been compiled with shared library support (e.g., `libpythonX.Y.so` on Linux, or the equivalent on other OSes). If you encounter `PythonLibraryNotFoundError`, you might need to reinstall/reconfigure Python with the `--enable-shared` flag or install a development version of Python (e.g., `sudo apt-get install python3-dev` on Debian/Ubuntu, though this was not sufficient in some limited environments).

**Building with `MelanomaApp.spec`:**

The repository includes a `MelanomaApp.spec` file which contains all the necessary configurations for PyInstaller.

1.  Navigate to the root directory of this project in your terminal.
2.  Run the following command:
    ```bash
    pyinstaller MelanomaApp.spec
    ```
3.  If the build is successful, you will find the bundled application in a directory named `dist/MelanomaApp` (or `dist/MelanomaApp.exe` on Windows, `dist/MelanomaApp.app` on macOS within a folder).

**Running the Executable:**

Once built, you can run the application by executing the main file within the `dist/MelanomaApp` directory.

---
**Debugging Resource Issues:**

If you build the executable and find that resources like icons or models are not loading correctly, run the executable from a command terminal. The application now includes debugging print statements that will output information to the console regarding how it's trying to locate these resource files. This can help diagnose whether the files are not being included in the bundle correctly or if the paths are being resolved unexpectedly. Look for lines starting with "resource_path called with:", "Bundle Mode:", or "Dev Mode:".
---
