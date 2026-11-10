"""Windows OpenCV preview with wheel zoom and full-resolution snapshots."""
from pathlib import Path
import cv2
import numpy as np

DEFAULT_WINDOW_SIZE = (1200, 800)
CANVAS_COLOR = (8, 8, 8)
MIN_ZOOM = 0.05
MAX_ZOOM = 50.0
ZOOM_STEP = 1.15


def render_on_canvas(
    image: np.ndarray, canvas_size: tuple[int, int], zoom: float
) -> np.ndarray:
    """Render an aspect-preserving image on a dark canvas and clip overflow."""
    canvas_width, canvas_height = canvas_size
    image_height, image_width = image.shape[:2]
    fit_scale = min(canvas_width / image_width, canvas_height / image_height)
    scale = fit_scale * zoom
    offset_x = (canvas_width - image_width * scale) / 2
    offset_y = (canvas_height - image_height * scale) / 2
    transform = np.array(
        [[scale, 0.0, offset_x], [0.0, scale, offset_y]], dtype=np.float64
    )
    interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
    return cv2.warpAffine(
        image,
        transform,
        (canvas_width, canvas_height),
        flags=interpolation,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=CANVAS_COLOR,
    )


class Preview:
    def __init__(self, target):
        self.target = target
        self.name = f"USB Camera {target}"
        self.zoom = 1.0
        self.frame = None
        self.closed = False
        cv2.namedWindow(self.name, cv2.WINDOW_NORMAL | cv2.WINDOW_FREERATIO)
        cv2.resizeWindow(self.name, *DEFAULT_WINDOW_SIZE)
        cv2.setMouseCallback(self.name, self.on_mouse)
        self.set_zoom(1.0)

    def set_zoom(self, zoom):
        self.zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom))
        cv2.setWindowTitle(self.name, f"{self.name} - Q/Esc quit, S save | Zoom {self.zoom:.2f}x")

    def on_mouse(self, event, _x, _y, flags, _param):
        if event == cv2.EVENT_MOUSEWHEEL:
            # HighGUI stores a signed Windows wheel delta in the high word.
            delta = (flags >> 16) & 0xffff
            if delta >= 0x8000:
                delta -= 0x10000
            steps = max(-20, min(20, delta / 120.0))
            self.set_zoom(self.zoom * ZOOM_STEP ** steps)
        elif event == cv2.EVENT_MBUTTONDOWN:
            self.set_zoom(1.0)

    def close(self):
        if not self.closed:
            self.closed = True
            cv2.destroyWindow(self.name)

    def update(self, frame=None):
        if self.closed:
            return False
        if cv2.getWindowProperty(self.name, cv2.WND_PROP_VISIBLE) < 1:
            self.closed = True
            return False
        if frame is not None:
            self.frame = frame
        if self.frame is not None:
            _x, _y, width, height = cv2.getWindowImageRect(self.name)
            size = (width, height) if width > 0 and height > 0 else DEFAULT_WINDOW_SIZE
            cv2.imshow(self.name, render_on_canvas(self.frame, size, self.zoom))
        key = cv2.waitKey(1) & 0xff
        if key in (ord('q'), ord('Q'), 27):
            self.close()
        elif key in (ord('s'), ord('S')) and self.frame is not None:
            path = Path(f"usb_camera_{self.target}.jpg").resolve()
            if not cv2.imwrite(str(path), self.frame):
                raise RuntimeError(f"保存失败: {path}")
            print(f"已保存: {path}", flush=True)
        return not self.closed
