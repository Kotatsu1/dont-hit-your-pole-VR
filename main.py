import openvr
from openvr import HmdMatrix34_t, IVROverlay, VRApplication_Overlay
import os
import asyncio
import time
import keyboard
from copy import deepcopy


PATH_ICON = os.path.join(os.path.dirname(__file__), 'Untitled.png')
UPDATE_RATE = 90
COLOR = [1, 1, 1]
TRANSPARENCY = 1
DEPTH = 1
WIDTH = 0.2


def mat34Id():
    matrix = HmdMatrix34_t()
    matrix[0][0] = 1
    matrix[1][1] = 1
    matrix[2][2] = 1
    return matrix


class UIElement:
    def __init__(self, overlayRoot: IVROverlay, key: str, name: str) -> None:
        self.overlay = overlayRoot
        self.overlayKey = key
        self.overlayName = name

        self.handle = self.overlay.createOverlay(self.overlayKey, self.overlayName)

        self.set_image(PATH_ICON)
        self.set_color(COLOR)
        self.set_transparency(TRANSPARENCY)
        self.overlay.setOverlayWidthInMeters(self.handle, WIDTH * DEPTH)
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

        self.first = UIElement(self.overlay, "1", "1")
        self.second = UIElement(self.overlay, "2", "2")
        self.third = UIElement(self.overlay, "3", "3")
        self.fourth = UIElement(self.overlay, "4", "4")

        self.placing_object = True
        self.tracked_device_index = 1


    def get_devices(self):
        for device_index in range(0, openvr.k_unMaxTrackedDeviceCount):
            device_class = self.vr_system.getTrackedDeviceClass(device_index)
            if device_class == openvr.TrackedDeviceClass_Invalid:
                continue

            device_name = self.vr_system.getStringTrackedDeviceProperty(device_index, openvr.Prop_ModelNumber_String)
            print(f"index {device_index} name {device_name}")

        print('--------------')
            

    def update(self):
        poses = self.vr_system.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0, 0)
        
        if poses[self.tracked_device_index].bPoseIsValid:
            base_transform = poses[self.tracked_device_index].mDeviceToAbsoluteTracking

            first_transform = deepcopy(base_transform)
            second_transform = deepcopy(base_transform)
            third_transform = deepcopy(base_transform)
            fourth_transform = deepcopy(base_transform)


            #right
            first_transform[0][0] = 0
            first_transform[0][1] = 0
            first_transform[0][2] = 1
            first_transform[1][0] = 0
            first_transform[1][1] = 1
            first_transform[1][2] = 0
            first_transform[2][0] = -1
            first_transform[2][1] = 0
            first_transform[2][2] = 0

            #left
            second_transform[0][0] = 0
            second_transform[0][1] = 0
            second_transform[0][2] = -1
            second_transform[1][0] = 0
            second_transform[1][1] = 1
            second_transform[1][2] = 0
            second_transform[2][0] = 1
            second_transform[2][1] = 0
            second_transform[2][2] = 0

            #front
            third_transform[0][0] = 1
            third_transform[0][1] = 0
            third_transform[0][2] = 0
            third_transform[1][0] = 0
            third_transform[1][1] = 1
            third_transform[1][2] = 0
            third_transform[2][0] = 0
            third_transform[2][1] = 0
            third_transform[2][2] = 1

            fourth_transform[0][0] = -1
            fourth_transform[0][1] = 0
            fourth_transform[0][2] = 0
            fourth_transform[1][0] = 0
            fourth_transform[1][1] = 1
            fourth_transform[1][2] = 0
            fourth_transform[2][0] = 0
            fourth_transform[2][1] = 0
            fourth_transform[2][2] = -1

            first_transform[0][3] += 0.1
            second_transform[0][3] -= 0.1
            third_transform[2][3] += 0.1
            fourth_transform[2][3] -= 0.1


            self.first.set_position(first_transform)
            self.second.set_position(second_transform)
            self.third.set_position(third_transform)
            self.fourth.set_position(fourth_transform)


async def main_loop(ui: UIManager):
    while True:
        startTime = time.monotonic()

        if keyboard.is_pressed('q'):
            ui.placing_object = not ui.placing_object

        if ui.placing_object:
            ui.update()
        
        sleepTime = (1 / UPDATE_RATE) - (time.monotonic() - startTime)
        if sleepTime > 0:
            await asyncio.sleep(sleepTime)


async def init_main():
    ui = UIManager()
    await main_loop(ui)


openvr.init(VRApplication_Overlay)
asyncio.run(init_main())
