High-quality object removal (2026-11-27): Big LaMa in the browser.
1. Download the TorchScript weights released with IOPaint:
   https://github.com/Sanster/models/releases/download/add_big_lama/big-lama.pt  (md5 e3aa4aaa15225a33ec84f9f4bc47e500)
2. python3 lama2onnx.py big-lama.pt lama512m.onnx 512 mix 400000
   (layers with >= 400,000 weights stored as 8-bit per output channel, the rest 16-bit; 71 MB)
3. split -b 24000000 -d -a 1 lama512m.onnx ../../models/lama.onnx.part
Fourier units are written as matrix products, so the old onnxruntime WebAssembly build (1.13) runs it
without an FFT operator. Browser output matches Python onnxruntime to 5e-7.
Test (compare.py, person-shaped hole on a brick wall, error inside the hole vs the true background):
  MI-GAN 13.1, LaMa float32 8.8, LaMa 8-bit everywhere 10.2 (green tint), LaMa mixed 8/16-bit 8.9.
Page test (2-core test machine, Chromium): fast mode about 3 s, high quality about 16 s per erase.
