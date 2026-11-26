How the Image to text model was made (PicShifter's own OCR, no third-party OCR code)

1. gen.py final   - renders every character (2,350 Hangul, 51 jamo, ASCII, symbols) with Noto Sans/Serif CJK KR,
                    WenQuanYi Zen Hei and several Latin fonts, with blur, width, slant and stroke variations,
                    and computes the glyph features in feat.py (8-direction gradient histograms + position).
2. lda.py         - learns a linear projection (LDA, 128 dimensions) and one prototype per character.
3. The export step in this session wrote image-to-text/ocr-model.bin and ocr-meta.json.
4. mktest.py / runtest.js - render test paragraphs and measure the character error rate of engine.js.

feat.py and image-to-text/engine.js must compute exactly the same features.
