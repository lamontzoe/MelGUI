import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2

# Your regions
BODY_REGIONS = [
    {'name': 'Head (Front)', 'rect': (235, 84, 370, 220)},
    {'name': 'Neck (Front)', 'rect': (263, 216, 345, 244)},
    {'name': 'Chest', 'rect': (220, 244, 391, 390)},
    {'name': 'Abdomen', 'rect': (232, 390, 391, 500)},
    {'name': 'Pelvis', 'rect': (222, 500, 395, 575)},
    {'name': 'Left Upper Arm (Front)',  'rect': (165, 244, 221, 407)},
    {'name': 'Left Lower Arm (Front)',  'rect': (110, 407, 211, 527)},
    {'name': 'Left Hand (Front)',       'rect': (104, 527, 197, 625)},
    {'name': 'Right Upper Arm (Front)', 'rect': (387, 244, 450, 407)},
    {'name': 'Right Lower Arm (Front)', 'rect': (388, 407, 470, 527)},
    {'name': 'Right Hand (Front)',      'rect': (412, 527, 504, 625)},
    {'name': 'Left Upper Leg (Front)',  'rect': (209, 575, 301, 726)},
    {'name': 'Left Lower Leg (Front)',  'rect': (217, 726, 297, 886)},
    {'name': 'Left Foot (Front)',       'rect': (231, 886, 299, 944)},
    {'name': 'Right Upper Leg (Front)', 'rect': (305, 575, 394, 726)},
    {'name': 'Right Lower Leg (Front)', 'rect': (311, 726, 381, 886)},
    {'name': 'Right Foot (Front)',      'rect': (310, 886, 386, 944)},
    {'name': 'Head (Back)', 'rect': (650, 84, 780, 220)},
    {'name': 'Neck (Back)', 'rect': (678, 216, 760, 244)},
    {'name': 'Upper Back', 'rect': (635, 244, 808, 390)},
    {'name': 'Lower Back', 'rect': (647, 390, 810, 500)},
    {'name': 'Buttox (Back)', 'rect': (637, 500, 810, 585)},
    {'name': 'Left Upper Arm (Back)', 'rect': (580, 244, 639, 407)},
    {'name': 'Left Lower Arm (Back)', 'rect': (525, 407, 629, 527)},
    {'name': 'Left Hand (Back)', 'rect': (519, 527, 615, 625)},
    {'name': 'Right Upper Arm (Back)', 'rect': (802, 244, 868, 407)},
    {'name': 'Right Lower Arm (Back)', 'rect': (803, 407, 888, 527)},
    {'name': 'Right Hand (Back)', 'rect': (827, 527, 922, 625)},
    {'name': 'Left Upper Leg (Back)', 'rect': (624, 585, 719, 726)},
    {'name': 'Left Lower Leg (Back)', 'rect': (632, 726, 715, 886)},
    {'name': 'Left Foot (Back)', 'rect': (646, 886, 717, 944)},
    {'name': 'Right Upper Leg (Back)', 'rect': (720, 585, 812, 726)},
    {'name': 'Right Lower Leg (Back)', 'rect': (726, 726, 799, 886)},
    {'name': 'Right Foot (Back)', 'rect': (725, 886, 804, 944)}
]

# Load your body map image
img_path = "Resources/icon_body.png"  # CHANGE THIS!
img = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)
fig, ax = plt.subplots(figsize=(12, 12))
ax.imshow(img)

# Draw rectangles for each region
for region in BODY_REGIONS:
    x1, y1, x2, y2 = region['rect']
    width = x2 - x1
    height = y2 - y1
    # Use a different color for back regions
    color = 'tab:blue' if 'Back' in region['name'] else 'tab:red'
    rect = patches.Rectangle((x1, y1), width, height, linewidth=2, edgecolor=color, facecolor='none')
    ax.add_patch(rect)
    ax.text(x1 + 3, y1 + 18, region['name'], fontsize=8, color=color, bbox=dict(facecolor='white', alpha=0.5, lw=0))

plt.axis('off')
plt.tight_layout()
plt.show()

BACK_BODY_REGIONS = [
    {'name': 'Head (Back)', 'rect': (470, 84, 608, 220)},
    {'name': 'Neck (Back)', 'rect': (498, 216, 583, 244)},
    {'name': 'Chest (Back)', 'rect': (455, 244, 529, 340)},
    {'name': 'Abdomen (Back)', 'rect': (467, 340, 529, 433)},
    {'name': 'Pelvis (Back)', 'rect': (457, 433, 533, 509)},
    {'name': 'Left Upper Arm (Back)', 'rect': (400, 244, 459, 407)},
    {'name': 'Left Lower Arm (Back)', 'rect': (345, 407, 449, 527)},
    {'name': 'Left Hand (Back)', 'rect': (339, 527, 435, 625)},
    {'name': 'Right Upper Arm (Back)','rect': (622, 244, 688, 407)},
    {'name': 'Right Lower Arm (Back)','rect': (623, 407, 708, 527)},
    {'name': 'Right Hand (Back)',     'rect': (647, 527, 742, 625)},
    {'name': 'Left Upper Leg (Back)', 'rect': (444, 509, 539, 726)},
    {'name': 'Left Lower Leg (Back)', 'rect': (452, 726, 535, 886)},
    {'name': 'Left Foot (Back)',      'rect': (466, 886, 537, 944)},
    {'name': 'Right Upper Leg (Back)','rect': (540, 509, 632, 726)},
    {'name': 'Right Lower Leg (Back)','rect': (546, 726, 619, 886)},
    {'name': 'Right Foot (Back)',     'rect': (545, 886, 624, 944)},
]

# Adjust the x coordinates
def shift_back_regions(regions, x_shift=180):
    new_regions = []
    for reg in regions:
        x1, y1, x2, y2 = reg['rect']
        new_rect = (x1 + x_shift, y1, x2 + x_shift, y2)
        new_regions.append({'name': reg['name'], 'rect': new_rect})
    return new_regions

SHIFTED_BACK_BODY_REGIONS = shift_back_regions(BACK_BODY_REGIONS, x_shift=180)

# Print new coordinates
for reg in SHIFTED_BACK_BODY_REGIONS:
    print(reg)