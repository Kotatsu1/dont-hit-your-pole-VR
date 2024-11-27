import tkinter as tk
from threading import Thread
import openvr
from openvr import HmdMatrix34_t, IVROverlay, VRApplication_Overlay, VRControllerState_t
import os
import asyncio
import time
from copy import deepcopy
import json
import math


config = {
    'transparency': 0.6,
    'height': 60,
    'color': [255, 255, 255],
    'size': 0.06
}


def rgb_to_normalized(rgb: list):
    return [round(x / 255.0, 1) for x in rgb]


def config_exists():
    config_exists = os.path.exists('config.json')
    if config_exists:
        return True

    return False


def create_config():
    if not config_exists():
        with open("config.json", "w") as f:
            f.write(json.dumps(config))


def find_config():
    if config_exists():
        global config
        with open('config.json', 'r') as f:
            config = json.loads(f.read())

    else:
        create_config()


find_config()

PATH_ICON = os.path.join(os.path.dirname(__file__), 'texture.png')
UPDATE_RATE = 60
TRANSPARENCY = config['transparency']


def mat34Id():
    matrix = HmdMatrix34_t()

    matrix[0][0] = 1
    matrix[1][1] = 1
    matrix[2][2] = 1

    return matrix


class UIElement:
    def __init__(self, overlay: IVROverlay, key: str, name: str) -> None:
        self.overlay = overlay
        self.overlay_key = key
        self.overlay_name = name
        self.width = config['size']
        self.color = rgb_to_normalized(config['color'])

        self.handle = self.overlay.createOverlay(self.overlay_key, self.overlay_name)

        self.set_image(PATH_ICON)
        self.set_color(self.color)
        self.set_transparency(TRANSPARENCY)
        self.overlay.setOverlayWidthInMeters(self.handle, self.width)
        self.overlay.setOverlayCurvature(self.handle, 1)
        self.overlay.showOverlay(self.handle)


    def set_image(self, path: str):
        self.overlay.setOverlayFromFile(self.handle, path)


    def set_color(self, color: list):
        self.overlay.setOverlayColor(self.handle, color[0], color[1], color[2])


    def set_transparency(self, value: float):
        self.overlay.setOverlayAlpha(self.handle, value)


    def set_position(self, transform: HmdMatrix34_t):
        tracking_origin = openvr.TrackingUniverseStanding
        self.overlay.setOverlayTransformAbsolute(self.handle, tracking_origin, transform)


class UIManager:
    def __init__(self) -> None:
        self.overlay = IVROverlay()
        self.vr_system = openvr.VRSystem()

        self.height = config['height']
        self.offset = config['size'] / math.pi

        self.first = UIElement(self.overlay, "1", "1")
        self.second = UIElement(self.overlay, "2", "2")

        self.placing_object = True
        self.tracked_device_index = 0
        self.get_right_controller_device_index()


    def check_trigger_press(self):
        controller_state: VRControllerState_t = self.vr_system.getControllerState(self.tracked_device_index)[1]
        trigger_value = controller_state.rAxis[1].x

        if trigger_value > 0.5:
            return True

        return False


    def get_right_controller_device_index(self):
        for device_index in range(0, openvr.k_unMaxTrackedDeviceCount):
            device_class = self.vr_system.getTrackedDeviceClass(device_index)
            if device_class != openvr.TrackedDeviceClass_Controller:
                continue
            
            device_name = self.vr_system.getStringTrackedDeviceProperty(device_index, openvr.Prop_ModelNumber_String)
            role = self.vr_system.getInt32TrackedDeviceProperty(device_index, openvr.Prop_ControllerRoleHint_Int32)

            if role == openvr.TrackedControllerRole_RightHand:
                self.tracked_device_index = device_index
                print(f"Right hand controller found: index {device_index} name {device_name}")
                return device_index


    def update(self):
        poses = self.vr_system.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0, 0)
        
        if poses[self.tracked_device_index].bPoseIsValid:
            base_transform = poses[self.tracked_device_index].mDeviceToAbsoluteTracking

            # will be used to find distance to pole from hmd
            # transform[1][3] += .1 #z
            # transform[0][3] += .1 #x
            # transform[2][3] += .1 #y

            self.first.set_position(self._get_transformed_position(base_transform, direction='right'))
            self.second.set_position(self._get_transformed_position(base_transform, direction='left'))


    def _get_transformed_position(self, base_transform, direction: str):
        transform = deepcopy(base_transform)

        if direction == 'right':
            transform[0][0], transform[0][1], transform[0][2] = 0, 0, 1
            transform[1][0], transform[1][1], transform[1][2] = 0, 1 + self.height, 0
            transform[2][0], transform[2][1], transform[2][2] = -1, 0, 0


        elif direction == 'left':
            transform[0][0], transform[0][1], transform[0][2] = 0, 0, -1
            transform[1][0], transform[1][1], transform[1][2] = 0, 1 + self.height, 0
            transform[2][0], transform[2][1], transform[2][2] = 1, 0, 0

            transform[0][3] += self.offset

        return transform

vr_loop_running = True

async def vr_loop(ui: UIManager):
    global vr_loop_running

    while vr_loop_running:
        start_time = time.monotonic()

        if ui.check_trigger_press():
            ui.placing_object = False

        if ui.placing_object:
            ui.update()
        
        sleep_time = (1 / UPDATE_RATE) - (time.monotonic() - start_time)
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)

ui = None

async def init_main():
    global ui
    ui_manager = UIManager()
    ui = ui_manager
    await vr_loop(ui)


root = tk.Tk()

def on_closing():
    global vr_loop_running
    vr_loop_running = False
    root.quit()
    exit()

def on_button_click():
    ui.placing_object = True

root.title("Don't hit your pole!")
root.geometry("800x600")
root.protocol("WM_DELETE_WINDOW", on_closing)

root.configure(bg="lightblue")

button = tk.Button(
    root,
    text="Replace Pole",
    command=on_button_click,
    font=("Arial", 30),
    width=20,
    height=3,
    bg="orange",
    fg="white",
    relief="solid",
    bd=5,
    padx=20, pady=20
)

button.pack(padx=20, pady=40)

def main_loop():
    openvr.init(VRApplication_Overlay)
    asyncio.run(init_main())


th = Thread(target=main_loop)
th.start()
root.mainloop()
