class ThermalCamera:
    def __init__(self):
        import flirpy
        self.cam = flirpy.camera.Lepton()
        
    def capture_heatmap(self):
        return self.cam.grab()
