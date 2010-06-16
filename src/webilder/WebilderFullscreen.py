import os
import gtk
import pango
from webshots import wbz

class FullscreenViewer(gtk.Window):
    def __init__(self, parent, data):
        gtk.Window.__init__(self)
        self._data = data
        self._parent = parent

    def quit(self, *args):
        self.destroy()

    def expose(self, widget, event):
        area = event.area
        gc = widget.get_style().fg_gc[gtk.STATE_NORMAL]
        widget.window.draw_drawable(gc, self.pixmap, area[0], area[1],
            area[0], area[1],
               area[2], area[3])
        return False

    def prepare_window(self):
        # We need to know the width and height of the monitor which is going
        # to show the full screen picture. We try to guess which monitor it is going
        # to be by inspecting where the mouse pointer is at.
        x, y, _ = gtk.gdk.get_default_root_window().get_pointer()
        monitor = gtk.gdk.Screen().get_monitor_at_point(x, y)
        rect = gtk.gdk.Screen().get_monitor_geometry(monitor)

        self.W, self.H = rect.width, rect.height
        self.p_title = self._data['title']
        self.p_album = self._data['album']
        self.p_credit= self._data['credit']

        drawing_area = gtk.DrawingArea()

        evt_box = gtk.EventBox()
        evt_box.add(drawing_area)
        self.add(evt_box)
        evt_box.connect('key-press-event', self.quit)
        evt_box.connect('button-press-event', self.quit)
        self.connect('key-press-event', self.quit)
        drawing_area.connect('configure-event', self.configure)
        drawing_area.connect('expose-event', self.expose)
        drawing_area.set_events(gtk.gdk.EXPOSURE_MASK)
        self.pixbuf = gtk.gdk.pixbuf_new_from_file(
            self._data['filename'])

        w,h = self.pixbuf.get_width(), self.pixbuf.get_height()
        if self.H>=h*self.W/w:
            self.new_w, self.new_h = self.W, h*self.W/w
        else:
            self.new_w, self.new_h = w*self.H/h, self.H
        self.pixbuf=self.pixbuf.scale_simple(self.new_w, self.new_h,
            gtk.gdk.INTERP_BILINEAR)

    def configure(self, widget, event):
        self.pixmap = gtk.gdk.Pixmap(self.window, self.W, self.H)
        gc = widget.get_style().black_gc
        self.pixmap.draw_rectangle(gc, True,
            0, 0, self.W, self.H)
        cx, cy = (self.W - self.new_w)/2, (self.H-self.new_h)/2
        self.pixmap.draw_pixbuf(gc, self.pixbuf, 0, 0,
            cx, cy,
            self.new_w, self.new_h)
        context = self.create_pango_context()
        fsize=context.get_font_description().get_size()*3/2
        font = context.get_font_description()
        font.set_size(fsize)
        context.set_font_description(font)
        layout = pango.Layout(context)
        layout.set_alignment(pango.ALIGN_CENTER)
        layout.set_markup(self.p_title+'\n'+self.p_credit)
        psize_x, psize_y = layout.get_pixel_size()
        self.pixmap.draw_layout(gc, (self.W-psize_x)/2, cy+23,
                layout)
        self.pixmap.draw_layout(widget.get_style().white_gc,
                (self.W-psize_x)/2-3, cy+20,
                layout)

    def run(self):
        self.fullscreen()
        self.prepare_window()
        self.show_all()
