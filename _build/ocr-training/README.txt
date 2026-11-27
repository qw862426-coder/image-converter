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

--- 2026-11-27 (v2, deployed): accented Latin letters + more Korean typefaces + neural network on ---
Characters: 2,721 = old 2,518 + 203 accented letters/symbols (German, French, Spanish, Portuguese, Italian,
Turkish, Polish, Vietnamese; see chars.py latin_ext). New ones are appended, so old numbers keep their meaning.
Fonts (fonts.py): Noto CJK, WQY, Pretendard, IBM Plex Sans KR, Spoqa Han Sans Neo, D2Coding (GitHub release
downloads, all OFL) + Latin fonts (DejaVu, Free*, Carlito/Caladea, Inter, TeX Gyre). Kept out of training for
honest tests: Wanted Sans (Korean) and TeX Gyre Adventor (Latin). fonts.has() skips characters a font lacks.
Steps: gen_v2.py train|hold -> lda2.py (out2/ocr-model.bin, ocr-meta.json)
       gen2b.py train2g 3 300000 ; gen3b.py tr 1800 200000 ; gen3b.py va 150 990000 ; extract.js (MD=out2)
       cnn_v2.py cnn_ft.npz 4 cnn_v2a.npz 1e-3 -> export_cnn.py cnn_v2a.npz out2
       corpus2.py all|held ; lm2.py all|held   (site text in ko/en/de/es/fr/pt)
Engine: lines that are mostly Latin are read again without Korean letters, measured from baseline to tall-letter
tops, and prefer splitting pieces (latLambda -2). Network scores are softened (netT 3) and mixed with the prototype
distance (beta 2), then sentence context (gamma 0.4).
Results (errors per 100 characters):            before v2   v2 (deployed)
  8 rendered tests (Noto/WQY)                        3.0        1.8
  unseen typefaces + European/Vietnamese (mktest2)  35.0       14.4
  real screenshot (Apple font, HEIC article)         6.8        4.8
Long screenshot in a browser: about 4.6 s (was about 2 s). Files: model 615 KB, network 1.0 MB, counts 67 KB.

--- 2026-11-27 (deployed): Japanese and Chinese readers, picked under "Text language" on the page ---
Separate model sets, files with -ja / -zh in image-to-text/. worker.js downloads only the chosen set.
Characters (cjk.py): ja 3,269 = JIS X 0208 level-1 kanji 2,965 + kana + ASCII + punctuation;
                     zh 3,885 = GB2312 level-1 hanzi 3,755 + ASCII + full-width punctuation.
Fonts: ja Noto Sans/Serif CJK JP, IBM Plex Sans JP, LXGW WenKai (held out: BIZ UD Gothic);
       zh Noto Sans/Serif CJK SC, WQY Zen Hei, IBM Plex Sans SC, LXGW WenKai (held out: LXGW Neo XiHei).
Steps (L = ja or zh): gen_cjk.py L lda train|hold ; lda_cjk.py L ; gen_cjk.py L glyph 2 <seed> ;
  gen3_cjk.py L tr 1200 <seed> ; gen3_cjk.py L va 100 <seed> ; extract.js (MD=out_L) ;
  cnn_cjk.py L cnn_v2a.npz 5 cnn_L.npz 1.5e-3 (drawing layers from the Korean network, new output layer) ;
  NOEVAL=1 export_cnn.py cnn_L.npz out_L ; lm_cjk.py L ; meta gets gamma 0.5, netT 2.
Engine: no spaces next to Japanese/Chinese characters; half-width , : ( ) ! ? next to them become full-width;
  a lone Latin letter between them is replaced by the best Japanese/Chinese character when nearly as likely.
Test errors per 100 characters (mktest_cjk.py, own sentences, incl. held-out fonts, small and photo-like text):
  ja: prototypes only 7.7 -> deployed 4.8      zh: prototypes only 5.2 -> deployed 3.5

--- 2026-11-27 (deployed): Russian, the first method only (prototype reader, no network, no character counts) ---
Characters: 66 Russian letters + ASCII + « » — – № etc. (175). Fonts: DejaVu, Free*, Carlito, Noto CJK, WQY,
Pretendard, Spoqa, D2Coding; held out: Inter. Steps: gen_cjk.py ru lda train|hold ; lda_cjk.py ru ;
meta: extras=false (the worker skips network/count files), latLambda -0.3.
Engine for Russian: line height from the tops of clearly taller letters (capitals, б, ф), because lower-case
Russian letters are short copies of capitals; look-alike Latin/Russian letters follow the word's alphabet;
3/0 inside Russian words become з/о, round letters inside numbers become 0; ь + I becomes ы.
Test errors per 100 characters (own sentences, Inter held out + DejaVu): 34.9 at first -> 6.3 (serif 16 px: 21).
