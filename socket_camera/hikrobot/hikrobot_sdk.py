from typing import Optional, Any
import threading
import os
from ctypes import *
from .MvImport.CameraParams_const import *
from .MvImport.CameraParams_header import *
from .MvImport.MvCameraControl_class import *
from .MvImport.MvErrorDefine_const import *
from .MvImport.MvISPErrorDefine_const import *
from .MvImport.PixelType_header import *


class DeviceManager:
    """Thread-safe enumerator and cache. Call enumerate() to get MV_CC_DEVICE_INFO_LIST."""
    _lock = threading.Lock()
    _device_list: Optional[MV_CC_DEVICE_INFO_LIST] = None

    TLAYER_TYPE = (
        MV_GIGE_DEVICE | MV_USB_DEVICE
    )

    @classmethod
    def enumerate(cls) -> MV_CC_DEVICE_INFO_LIST:
        with cls._lock:
            if cls._device_list is not None:
                return cls._device_list
            device_list = MV_CC_DEVICE_INFO_LIST()
            ret = MvCamera.MV_CC_EnumDevices(cls.TLAYER_TYPE, device_list)
            if ret != 0:
                raise RuntimeError(f"Enum devices failed! ret [0x{ret:x}]")
            cls._device_list = device_list
            return cls._device_list
    
    
    @classmethod
    def find_camera(cls, serial_number: str) -> Optional[MV_CC_DEVICE_INFO]:
        """Find a camera by serial number and return MV_CC_DEVICE_INFO or None."""
        device_list = cls.enumerate()

        for i in range(device_list.nDeviceNum):
            di = cast(device_list.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
            
            try:
                if di.nTLayerType == MV_GIGE_DEVICE:
                    raw = bytearray(di.SpecialInfo.stGigEInfo.chSerialNumber)
                else:
                    raw = bytearray(di.SpecialInfo.stUsb3VInfo.chSerialNumber)
          
                sn = bytes(raw).split(b"", 1)[0].decode(errors="ignore")
            
            except Exception:
                sn = ""

            if sn == serial_number:
                return di
        
        return None

    
    @classmethod
    def refresh(cls) -> MV_CC_DEVICE_INFO_LIST:
        with cls._lock:
            device_list = MV_CC_DEVICE_INFO_LIST()
            ret = MvCamera.MV_CC_EnumDevices(cls.TLAYER_TYPE, device_list)
            if ret != 0:
                raise RuntimeError(f"Refresh devices failed! ret [0x{ret:x}]")
            cls._device_list = device_list
            return cls._device_list


class CameraDevice:
    """Thin wrapper for single camera operations using the Mv SDK.

    Usage:
        device_info = cast(device_list.pDeviceInfo[idx], POINTER(MV_CC_DEVICE_INFO)).contents
        cam = CameraDevice(device_info)
        cam.create_handle_and_open()
        cam.start_grabbing()
        data = cam.get_one_frame(1000)
        cam.stop_grabbing()
        cam.close_and_destroy()
    """

    def __init__(self, device_info: MV_CC_DEVICE_INFO):
        self._camera = MvCamera()
        self._device_info = device_info
        self._is_open = False

    def create_handle_and_open(self) -> bool:
        ret = self._camera.MV_CC_CreateHandle(self._device_info)
        if ret != 0:
            return False
        ret = self._camera.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
        if ret != 0:
            self._camera.MV_CC_DestroyHandle()
            return False
        self._is_open = True
        return True

    def close_and_destroy(self) -> None:
        try:
            if self._is_open:
                self._camera.MV_CC_CloseDevice()
        except Exception:
            raise RuntimeError("Unble to Close the MVS camera")
        try:
            self._camera.MV_CC_DestroyHandle()
        except Exception:
            raise RuntimeError("Unble to Destory Handle of the MVS camera")
        self._is_open = False

    def start_grabbing(self) -> bool:
        ret = self._camera.MV_CC_StartGrabbing()
        return ret == 0

    def stop_grabbing(self) -> bool:
        ret = self._camera.MV_CC_StopGrabbing()
        return ret == 0

    def get_one_frame(self, timeout_ms: int = 1000) -> Optional[tuple]:
        
        try:
            stFrameInfo = MV_FRAME_OUT_INFO_EX()
            memset(byref(stFrameInfo), 0, sizeof(stFrameInfo))

            stParam = MVCC_INTVALUE()
            memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))
            ret = self._camera.MV_CC_GetIntValue('PayloadSize', stParam)
            if ret != 0:
                return None
            nPayloadSize = stParam.nCurValue

            buf = (c_ubyte * nPayloadSize)()
            ret = self._camera.MV_CC_GetOneFrameTimeout(buf, nPayloadSize, stFrameInfo, timeout_ms)
            if ret != 0:
                return None

            n_frame_len = stFrameInfo.nFrameLen
            data_bytes = b''
            if n_frame_len > 0:
                data_bytes = string_at(buf, n_frame_len)
            return data_bytes, stFrameInfo
        
        except Exception:
            return None

    def convert_to_rgb(self, raw_bytes: bytes, frame_info: MV_FRAME_OUT_INFO_EX) -> Optional[bytes]:
        try:
            stConvert = MV_CC_PIXEL_CONVERT_PARAM()
            memset(byref(stConvert), 0, sizeof(stConvert))

            stConvert.nWidth = frame_info.nWidth
            stConvert.nHeight = frame_info.nHeight
            if raw_bytes:
                src_buf = (c_ubyte * len(raw_bytes)).from_buffer_copy(raw_bytes)
                stConvert.pSrcData = cast(src_buf, POINTER(c_ubyte))
                stConvert.nSrcDataLen = len(raw_bytes)
            else:
                stConvert.pSrcData = None
                stConvert.nSrcDataLen = 0

            stConvert.enSrcPixelType = frame_info.enPixelType
            stConvert.enDstPixelType = PixelType_Gvsp_RGB8_Packed

            nRGBSize = frame_info.nWidth * frame_info.nHeight * 3
            pRGBData = (c_ubyte * nRGBSize)()
            stConvert.pDstBuffer = cast(pRGBData, POINTER(c_ubyte))
            stConvert.nDstBufferSize = nRGBSize

            ret = self._camera.MV_CC_ConvertPixelType(stConvert)
            if ret != 0:
                return None

            return string_at(stConvert.pDstBuffer, stConvert.nDstLen)
        except Exception:
            return None

    def set_value(self, name: str, value: Any) -> bool:
        try:
            if isinstance(value, bool):
                return self._camera.MV_CC_SetBoolValue(name, value) == 0
            if isinstance(value, int):
                return self._camera.MV_CC_SetIntValue(name, int(value)) == 0
            if isinstance(value, float):
                return self._camera.MV_CC_SetFloatValue(name, float(value)) == 0
            if isinstance(value, str):
                ret = self._camera.MV_CC_SetCommandValue(name)
                return ret == 0
            return self._camera.MV_CC_SetEnumValue(name, int(value)) == 0
        except Exception:
            return False
    
    def _register_exception_callback(self):
        try:
            if os.name == 'nt':
                CB_TYPE = WINFUNCTYPE(None, c_uint, c_void_p)
            else:
                CB_TYPE = CFUNCTYPE(None, c_uint, c_void_p)


            @CB_TYPE
            def _exception_cb(msg_type, p_user):
                """On SDK exception: mark closed, stop grabbing, release resources."""
                try:
                    self._camera.MV_CC_StopGrabbing()
                except Exception:
                    raise RuntimeError("Unable to stop grabbing on exception")
                try:
                    self._camera.MV_CC_CloseDevice()
                except Exception:
                    raise RuntimeError("Unable to Close Device on exception")
                try:
                    self._camera.MV_CC_DestroyHandle()
                except Exception:
                    raise RuntimeError("Unable to Destroy handle on exception")
                self._is_open = False


            self._exception_cb = _exception_cb
            try:
                self._camera.MV_CC_RegisterExceptionCallBack(self._exception_cb, None)
            except Exception:
                return False
        except Exception:
            return False


