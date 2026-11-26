How the Image to text model was made (PicShifter's own OCR, no third-party OCR code)

1. gen.py final   - renders every character (2,350 Hangul, 51 jamo, ASCII, symbols) with Noto Sans/Serif CJK KR,
                    WenQuanYi Zen Hei and several Latin fonts, with blur, width, slant and stroke variations,
                    and computes the glyph features in feat.py (8-direction gradient histograms + position).
2. lda.py         - learns a linear projection (LDA, 128 dimensions) and one prototype per character.
3. The export step in this session wrote image-to-text/ocr-model.bin and ocr-meta.json.
4. mktest.py / runtest.js - render test paragraphs and measure the character error rate of engine.js.

feat.py and image-to-text/engine.js must compute exactly the same features.

--- 2026-11-27: sentence context and neural network ---
Sentence context (deployed): corpus_all.py collects PicShifter's own Korean/English page text, lm_all.py counts
how often each character appears and which follows which -> image-to-text/ocr-lm.json. engine.js picks the most
likely chain of characters (Viterbi over the top 6 guesses per piece; weights LDAT=4, GAMMA=0.4).
For fair tests use corpus.py/lm.py, which leave out the HEIC article shown in the screenshot test.
Results: 8 rendered tests 3.5% -> 3.0% wrong; real screenshot 11.2% -> 6.8% wrong (shotcer.py).

Neural network (NOT deployed yet): gen2.py (single glyph samples) -> cnn.py (NumPy CNN, 13 epochs, 85.4% on
held-back samples) -> gen3.py pages + extract.js (pieces cut by the real reader) -> cnn_ft.py (5 more epochs,
86.5%) -> export_cnn.py -> ocr-net.bin/.json (8-bit, 954 KB). engine.js uses it when those files exist
(BETA=network/prototype mix). It reaches 2.5% on the rendered tests but 7.6-8.1% on the real screenshot:
it only saw Noto/WQY fonts, so it needs more font variety before it goes live.
