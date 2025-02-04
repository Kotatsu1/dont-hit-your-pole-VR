import threading
import openvr
from openvr import HmdMatrix34_t, IVROverlay, VRApplication_Overlay, VRSystem
import os
import asyncio
import time
from copy import deepcopy
from utils import rgb_to_normalized
from utils import config, save_config
import math
from typees import BaseStation


PATH_ICON = os.path.join(os.path.dirname(__file__), 'texture.png')
UPDATE_RATE = 10
TRANSPARENCY = config['transparency']


class PoleHalf:
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


class PoleTracking:
    def __init__(self) -> None:
        self.pole_offset_x = config['x']
        self.pole_offset_y = config['y']
        self.pole_offset_z = config['z']
        self.height = config['height']
        self.offset = config['size'] / math.pi

        self.__run_pole_thread()


    async def __async_startup(self):
        openvr.init(VRApplication_Overlay)
        self.vr_system = VRSystem()
        self.overlay = IVROverlay()

        station = self.get_first_base_station()
        coords = self.get_base_station_coordinates(station)
        station.matrix = coords
        self.base_station = station
        print(self.base_station)

        self.first_half = PoleHalf(self.overlay, "1", "1")
        self.second_half = PoleHalf(self.overlay, "2", "2")

        while True:
            start_time = time.monotonic()
            self.update()

            sleep_time = (1 / UPDATE_RATE) - (time.monotonic() - start_time)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)


    def __startup(self):
        asyncio.run(self.__async_startup())


    def __run_pole_thread(self):
        thread = threading.Thread(target=self.__startup)
        thread.start()


    def get_first_base_station(self) -> BaseStation:
        existing_station = config["base_station_serial"]

        for device_index in range(openvr.k_unMaxTrackedDeviceCount):
            if not self.vr_system.isTrackedDeviceConnected(device_index):
                continue

            device_class = self.vr_system.getTrackedDeviceClass(device_index)
            if device_class == openvr.TrackedDeviceClass_TrackingReference:
                serial = self.vr_system.getStringTrackedDeviceProperty(
                    device_index, openvr.Prop_SerialNumber_String
                )

                station = BaseStation(device_index, serial)

                if existing_station:
                    print('check exsisting')
                    if serial != existing_station:
                        continue
                else:
                    existing_station = station
                    self.save_config()

                return station


    def get_base_station_coordinates(self, base_station: BaseStation):
        poses = self.vr_system.getDeviceToAbsoluteTrackingPose(
            openvr.TrackingUniverseStanding, 0, openvr.k_unMaxTrackedDeviceCount
        )

        pose = poses[base_station.index]
        matrix = pose.mDeviceToAbsoluteTracking

        return matrix


    def set_pole_offset(self, pole_offset: dict):
        self.pole_offset_x = pole_offset["x"]
        self.pole_offset_y = pole_offset["y"]
        self.pole_offset_z = pole_offset["z"]

        global config
        config["x"] = pole_offset["x"]
        config["y"] = pole_offset["y"]
        config["z"] = pole_offset["z"]


    def save_config(self):
        print('Saving config')
        save_config()


    def update(self):
        poses = self.vr_system.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0, 0)
        
        if poses[self.base_station.index].bPoseIsValid:
            station_transform = poses[self.base_station.index].mDeviceToAbsoluteTracking

            station_transform = self.clear_rotation(station_transform)

            station_transform[0][3] += self.pole_offset_x
            station_transform[1][3] += self.pole_offset_y
            station_transform[2][3] += self.pole_offset_z

            self.first_half.set_position(self._get_transformed_position(station_transform, direction='right'))
            self.second_half.set_position(self._get_transformed_position(station_transform, direction='left'))
    

    def clear_rotation(self, poses):
        poses[0][2] = 0
        poses[1][2] = 0
        poses[2][2] = 0
        poses[0][1] = 0
        poses[1][1] = 0
        poses[2][1] = 0
        poses[0][0] = 0
        poses[1][0] = 0
        poses[1][0] = 0

        return poses


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

