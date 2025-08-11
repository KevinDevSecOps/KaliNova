# File: rf_necromancer.py
from gnuradio import blocks, gr, analog
import numpy as np

class RF_Necromancer(gr.top_block):
    def __init__(self, freq=433.92e6):
        gr.top_block.__init__(self)
        self.sdr = blocks.hackrf_source(freq=freq, samp_rate=2e6)
        self.signal = analog.sig_source_c(2e6, analog.GR_SIN_WAVE, 0, 1, 0)
        self.amp = blocks.multiply_const_cc(0.5)  # Evita saturación
        self.sink = blocks.hackrf_sink(freq=freq, samp_rate=2e6)
        
        # Conecta todo
        self.connect(self.signal, self.amp, self.sink)
        
    def inject_firmware(self, file_path):
        raw_data = np.fromfile(file_path, dtype=np.uint8)
        self.signal.set_data(raw_data.tolist())  # Inyecta bytes como señal

if __name__ == "__main__":
    necro = RF_Necromancer(freq=868e6)
    necro.inject_firmware("firmware_custom.bin")  # Tu firmware malicioso/benigno
    necro.run()