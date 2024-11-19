import openvr
from openvr import HmdMatrix34_t, IVROverlay, VRApplication_Overlay
import os
import asyncio
import time


PATH_ICON = os.path.join(os.path.dirname(__file__), 'Untitled.png')
UPDATE_RATE = 1
COLOR = [1, 1, 1]
TRANSPARENCY = 1
X_POS = 0
Y_POS = -0.2
DEPTH = 1
WIDTH = 0.2


def mat34Id():
    matrix = HmdMatrix34_t()

    matrix[0][0] = 1
    matrix[1][1] = 1
    matrix[2][2] = 1

    return matrix


class UIElement:
    def __init__(self, overlayRoot: IVROverlay, key: str, name: str, pos: tuple) -> None:
        self.overlay = overlayRoot
        self.overlayKey = key
        self.overlayName = name

        self.handle = self.overlay.createOverlay(self.overlayKey, self.overlayName)

        self.set_image(PATH_ICON)
        self.set_color(COLOR)
        self.set_transparency(TRANSPARENCY)
        self.overlay.setOverlayWidthInMeters(self.handle, WIDTH * DEPTH)
        self.set_position(pos)
        self.overlay.showOverlay(self.handle)


    def set_image(self, path: str):
        self.overlay.setOverlayFromFile(self.handle, path)


    def set_color(self, color: list):
        self.overlay.setOverlayColor(self.handle, color[0], color[1], color[2])


    def set_transparency(self, value: float):
        self.overlay.setOverlayAlpha(self.handle, value)


    def set_position(self, pos: tuple):
        self.transform = mat34Id()
        self.transform[0][3] = pos[0] * DEPTH
        self.transform[1][3] = pos[1] * DEPTH
        self.transform[2][3] = -DEPTH

        self.overlay.setOverlayTransformTrackedDeviceRelative(
            self.handle, 
            openvr.k_unTrackedDeviceIndex_Hmd, 
            self.transform
        )


class UIManager:
    def __init__(self) -> None:
        self.overlay = IVROverlay()

        self.uiElement = UIElement(
            self.overlay, 
            "avatar", 
            "avatar", 
            (X_POS, Y_POS)
        )


    def update(self):
        pass


async def main_loop(ui: UIManager):
    while True:
        startTime = time.monotonic()
        ui.update()
        
        sleepTime = (1 / UPDATE_RATE) - (time.monotonic() - startTime)
        if sleepTime > 0:
            await asyncio.sleep(sleepTime)


async def init_main():
    ui = UIManager()
    await main_loop(ui)


openvr.init(VRApplication_Overlay)
asyncio.run(init_main())
