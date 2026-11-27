Background removal models used by /remove-background/

u2netp.onnx       U^2-Net (small), Copyright Xuebin Qin et al., Apache License 2.0 — https://github.com/xuebinqin/U-2-Net
isnet.onnx.*      ISNet "isnet-general-use" (Highly Accurate Dichotomous Image Segmentation), Xuebin Qin et al.,
                  Apache License 2.0 — https://github.com/xuebinqin/DIS ; ONNX file distributed with rembg by Daniel Gatis
                  (MIT) — https://github.com/danielgatis/rembg . Large conv weights stored as 8-bit (one scale per output
                  channel), the rest as 16-bit, with _build/bg/shrink.py (178.6 MB -> 48.4 MB). Split into parts to fit
                  the hosting file-size limit; the page joins them back together. Used by "High quality" since 2026-11-27
                  (replaced the smaller "silueta" model).

Object removal model used by /remove-object/

migan.onnx.*      MI-GAN (512, Places2) by Picsart AI Research, MIT License — https://github.com/Picsart-AI-Research/MI-GAN
                  Converted to ONNX from the TorchScript release distributed with IOPaint (Apache License 2.0,
                  https://github.com/Sanster/IOPaint). Split into parts to fit the hosting file-size limit.

lama.onnx.*       Big LaMa (Resolution-robust Large Mask Inpainting with Fourier Convolutions) by Samsung AI Center
                  Moscow et al., Apache License 2.0 — https://github.com/advimman/lama
                  Weights from the TorchScript release distributed with IOPaint (Apache License 2.0,
                  https://github.com/Sanster/IOPaint). Converted to ONNX for a fixed 512x512 input with
                  _build/lama/lama2onnx.py (Fourier units written as matrix products; large layers stored as 8-bit,
                  the rest as 16-bit). Split into parts to fit the hosting file-size limit.
