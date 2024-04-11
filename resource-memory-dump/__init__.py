import qrenderdoc as qrd
import renderdoc as rd

from typing import Optional

class Window(qrd.CaptureViewer):
    def hoge(self):
        pass
        
    def __init__(self, ctx: qrd.CaptureContext, version: str):
        super().__init__()

        self.mqt: qrd.MiniQtHelper = ctx.Extensions().GetMiniQtHelper()

        self.ctx = ctx
        self.version = version
        self.topWindow = self.mqt.CreateToplevelWidget("Resources", lambda c, w, d: window_closed())

        vert = self.mqt.CreateVerticalContainer()
        self.mqt.AddWidget(self.topWindow, vert)

        self.resourceList = self.mqt.CreateTextBox(False, False)

        self.mqt.AddWidget(vert, self.resourceList)

        ctx.AddCaptureViewer(self)

    def OnCaptureLoaded(self):
        self.UpdateResourceList()

    def OnCaptureClosed(self):
        self.mqt.SetWidgetText(self.resourceList, "Resources:")

    def OnSelectedEventChanged(self, event):
        self.UpdateResourceList()

    def OnEventChanged(self, event):
        pass

    def UpdateResourceList(self):
        buffers = self.ctx.GetBuffers()
        textures = self.ctx.GetTextures()
        buffer_details = list(map(lambda b: ['buffer', self.ctx.GetResourceName(b.resourceId), b.length], buffers))
        texture_details = list(map(lambda t: ['texture', self.ctx.GetResourceName(t.resourceId), t.byteSize], textures))
        # sorted_list = sorted(buffer_details + texture_details, key=lambda x: -x[2])

        resource_list = "<html><body><table><tr><th>Type</th><th>Name</th><th>Size(MB)</th></tr>"
        for resource in (buffer_details + texture_details):
            rounded = round(resource[2] / 1000000, 4)
            resource_list += f"<tr><td>{resource[0]}</td><td>{resource[1]}</td><td>{rounded}</td>\n"
        resource_list += "</table></body></html>"

        self.mqt.SetWidgetText(self.resourceList, resource_list)


cur_window: Optional[Window] = None

def window_closed():
    global cur_window
    if cur_window is not None:
        cur_window.ctx.RemoveCaptureViewer(cur_window)
    cur_window = None


def open_window_callback(ctx: qrd.CaptureContext, data):
    global cur_window

    mqt = ctx.Extensions().GetMiniQtHelper()

    if cur_window is None:
        cur_window = Window(ctx, extiface_version)
        if ctx.HasEventBrowser():
            ctx.AddDockWindow(cur_window.topWindow, qrd.DockReference.TopOf, ctx.GetEventBrowser().Widget(), 0.1)
        else:
            ctx.AddDockWindow(cur_window.topWindow, qrd.DockReference.MainToolArea, None)

    ctx.RaiseDockWindow(cur_window.topWindow)

extiface_version = ''

def register(version: str, ctx: qrd.CaptureContext):
    global extiface_version
    extiface_version = version

    print("Registering Resources Extension for RenderDoc version {}".format(version))
    ctx.Extensions().RegisterWindowMenu(qrd.WindowMenu.Window, ["Resources Memory Dump"], open_window_callback)

def unregister():
    print("Unregistering Resources Extension")

    global cur_window

    if cur_window is not None:
        cur_window.ctx.Extensions().GetMiniQtHelper().CloseToplevelWidget(cur_window.topWindow)
        cur_window = None