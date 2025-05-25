import sys
import os

def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    print(f"resource_path called with: {relative_path}") # General debug
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        resolved_path = os.path.join(base_path, relative_path)
        print(f"Bundle Mode: Trying path: {resolved_path}")

        # Specific check for 'Resources' directory content
        # Check if relative_path contains a path separator (e.g. "Resources/icon.png")
        if os.path.sep in relative_path:
            resource_dir_in_bundle_name = os.path.dirname(relative_path) # Should be "Resources"
            if resource_dir_in_bundle_name: # Ensure it's not empty if relative_path is just "file.png"
                resource_dir_in_bundle_abs = os.path.join(base_path, resource_dir_in_bundle_name)

                print(f"Bundle Mode: Checking existence of directory: {resource_dir_in_bundle_abs}")
                if os.path.exists(resource_dir_in_bundle_abs) and os.path.isdir(resource_dir_in_bundle_abs):
                    print(f"Bundle Mode: Contents of '{resource_dir_in_bundle_abs}': {os.listdir(resource_dir_in_bundle_abs)}")
                else:
                    print(f"Bundle Mode: Directory '{resource_dir_in_bundle_abs}' NOT found or not a directory.")
            else:
                # This case implies relative_path is just a filename, so resources are expected at bundle root.
                # We can list base_path contents if needed for debugging.
                print(f"Bundle Mode: No directory in relative_path. Listing contents of bundle root '{base_path}': {os.listdir(base_path)}")


        print(f"Bundle Mode: Full path exists: {os.path.exists(resolved_path)}")
    else:
        # Development mode
        try:
            # Assumes utils.py is in src/, and main script (sys.argv[0]) is in src/
            # and resources (models/, Resources/) are at the project root.
            current_script_dir = os.path.dirname(os.path.abspath(__file__)) # Directory of utils.py (src/)
            base_path = os.path.abspath(os.path.join(current_script_dir, os.pardir)) # Project root
        except Exception as e:
            print(f"Dev Mode: Error determining base_path: {e}")
            base_path = os.path.abspath(".") # Fallback
        
        resolved_path = os.path.join(base_path, relative_path)
        # print(f"Dev Mode: Trying path: {resolved_path}")
        # print(f"Dev Mode: Full path exists: {os.path.exists(resolved_path)}")

    return resolved_path
