"""Preview controls matching socket_camera/hikrobot_stream.py, without MVS imports."""
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
        import gi
        gi.require_version('Gtk', '3.0')
        gi.require_version('Gdk', '3.0')
        from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
        self.Gtk, self.Gdk = Gtk, Gdk
        self.GdkPixbuf, self.GLib = GdkPixbuf, GLib
        self.target = target
        self.name = f"Hikrobot {target} - Q/Esc quit, S save"
        self.zoom = 1.0
        self.frame = None
        self.closed = False
        self.error = None
        self.window = Gtk.Window(title=self.name)
        self.window.set_default_size(*DEFAULT_WINDOW_SIZE)
        self.area = Gtk.DrawingArea()
        self.area.add_events(Gdk.EventMask.SCROLL_MASK |
                             Gdk.EventMask.SMOOTH_SCROLL_MASK |
                             Gdk.EventMask.BUTTON_PRESS_MASK)
        self.area.connect('scroll-event', self.on_scroll)
        self.area.connect('button-press-event', self.on_button)
        self.area.connect('draw', self.on_draw)
        self.window.connect('key-press-event', self.on_key)
        self.window.connect('destroy', self.on_destroy)
        self.window.add(self.area)
        self.window.show_all()
        self.set_zoom(1.0)

    def set_zoom(self, zoom):
        self.zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom))
        self.window.set_title(f"{self.name} | Zoom {self.zoom:.2f}x")
        self.area.queue_draw()

    def on_scroll(self, _widget, event):
        if event.direction == self.Gdk.ScrollDirection.UP:
            steps = 1.0
        elif event.direction == self.Gdk.ScrollDirection.DOWN:
            steps = -1.0
        elif event.direction == self.Gdk.ScrollDirection.SMOOTH:
            valid, _dx, dy = event.get_scroll_deltas()
            steps = -dy if valid else 0.0
        else:
            return False
        self.set_zoom(self.zoom * ZOOM_STEP ** max(-20, min(20, steps)))
        return True

    def on_button(self, _widget, event):
        if event.button == 2:
            self.set_zoom(1.0)
            return True
        return False

    def on_key(self, _widget, event):
        key = self.Gdk.keyval_name(event.keyval)
        if key in ('q', 'Q', 'Escape'):
            self.close()
            return True
        if key in ('s', 'S') and self.frame is not None:
            path = Path(f"camera_{self.target}.jpg").resolve()
            try:
                if not cv2.imwrite(str(path), self.frame):
                    raise RuntimeError(f"保存失败: {path}")
                print(f"已保存: {path}", flush=True)
            except Exception as exc:
                self.error = exc
            return True
        return False

    def on_draw(self, widget, context):
        if self.frame is None:
            return False
        try:
            width, height = widget.get_allocated_width(), widget.get_allocated_height()
            canvas = render_on_canvas(self.frame, (width, height), self.zoom)
            rgb = cv2.cvtColor(canvas, cv2.COLOR_GRAY2RGB if canvas.ndim == 2 else cv2.COLOR_BGR2RGB)
            pixbuf = self.GdkPixbuf.Pixbuf.new_from_bytes(
                self.GLib.Bytes.new(rgb.tobytes()), self.GdkPixbuf.Colorspace.RGB,
                False, 8, width, height, width * 3)
            self.Gdk.cairo_set_source_pixbuf(context, pixbuf, 0, 0)
            context.paint()
        except Exception as exc:
            self.error = exc
        return False

    def on_destroy(self, _widget):
        self.closed = True

    def close(self):
        if not self.closed:
            self.window.destroy()

    def update(self, frame=None):
        if self.closed:
            return False
        if frame is not None:
            self.frame = frame
            self.area.queue_draw()
        while self.Gtk.events_pending():
            self.Gtk.main_iteration_do(False)
        if self.error:
            raise self.error
        return not self.closed
