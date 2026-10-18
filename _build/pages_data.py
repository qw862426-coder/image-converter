# Content for the feature landing pages. Each page reuses a tool (image or doc) with a preset.
# 'meta' gives title/desc/h1/sub in 8 languages; 'en'/'ko' hold the article shown under the tool.

PAGES = []

def page(slug, base, preset, meta, en, ko):
    PAGES.append(dict(slug=slug, base=base, preset=preset, meta=meta, en=en, ko=ko))

def M(**langs):
    return langs

# ---------------------------------------------------------------- HEIC to JPG
page('heic-to-jpg', 'image', {'fmt': 'jpg', 'quality': 92, 'accept': 'image/*,.heic,.heif'},
M(
 en=dict(title='HEIC to JPG Converter – Free, No Upload | PicShifter', desc='Convert iPhone HEIC photos to JPG for free. Many photos at once, right in your browser. Your photos are never uploaded.', h1='HEIC to JPG', sub='Turn iPhone HEIC photos into JPG files that open anywhere. Converted on your device.'),
 ko=dict(title='아이폰 사진 HEIC JPG 변환 | PicShifter', desc='아이폰 HEIC 사진을 무료로 JPG로 바꾸세요. 여러 장을 한 번에, 브라우저에서 바로. 사진은 업로드되지 않습니다.', h1='HEIC를 JPG로', sub='아이폰 HEIC 사진을 어디서나 열리는 JPG로 바꿔요. 내 기기 안에서 변환돼요.'),
 ja=dict(title='HEICをJPGに変換 – 無料・アップロード不要 | PicShifter', desc='iPhoneのHEIC写真を無料でJPGに変換。複数枚をまとめてブラウザで変換でき、写真はアップロードされません。', h1='HEICをJPGに', sub='iPhoneのHEIC写真を、どこでも開けるJPGに変換します。処理は端末内で行われます。'),
 zh=dict(title='HEIC 转 JPG – 免费，无需上传 | PicShifter', desc='免费将 iPhone 的 HEIC 照片转换为 JPG。可批量转换，直接在浏览器中完成，照片不会上传。', h1='HEIC 转 JPG', sub='把 iPhone 的 HEIC 照片转换成到处都能打开的 JPG。在你的设备上完成转换。'),
 es=dict(title='Convertir HEIC a JPG – Gratis, sin subir archivos | PicShifter', desc='Convierte fotos HEIC del iPhone a JPG gratis. Varias a la vez, en tu navegador. Tus fotos nunca se suben.', h1='HEIC a JPG', sub='Convierte las fotos HEIC del iPhone en JPG que se abren en cualquier sitio. Todo en tu dispositivo.'),
 pt=dict(title='Converter HEIC para JPG – Grátis, sem envio | PicShifter', desc='Converta fotos HEIC do iPhone para JPG de graça. Várias de uma vez, no navegador. Suas fotos nunca são enviadas.', h1='HEIC para JPG', sub='Transforme fotos HEIC do iPhone em JPG que abrem em qualquer lugar. Tudo no seu dispositivo.'),
 fr=dict(title='Convertir HEIC en JPG – Gratuit, sans envoi | PicShifter', desc='Convertissez gratuitement les photos HEIC de l’iPhone en JPG. Plusieurs à la fois, dans votre navigateur, sans envoi.', h1='HEIC en JPG', sub='Transformez les photos HEIC de l’iPhone en JPG lisibles partout. Conversion sur votre appareil.'),
 de=dict(title='HEIC in JPG umwandeln – kostenlos, ohne Upload | PicShifter', desc='Wandle iPhone-HEIC-Fotos kostenlos in JPG um. Mehrere auf einmal, direkt im Browser. Deine Fotos werden nie hochgeladen.', h1='HEIC zu JPG', sub='Mach aus iPhone-HEIC-Fotos JPG-Dateien, die sich überall öffnen lassen. Umgewandelt auf deinem Gerät.'),
),
en='''<h2>Why HEIC photos won’t open</h2>
<p>Since iOS 11 in 2017, iPhones save photos as HEIC by default. HEIC keeps the same picture quality as JPG in a smaller file, but many Windows programs, websites, print shops and older phones still can’t open it. Converting to JPG fixes that.</p>
<h2>How to convert HEIC to JPG</h2>
<ol><li>Tap the box above and choose your HEIC photos. You can pick many at once.</li><li>JPG is already selected. Leave quality at 92% for nearly identical photos, or lower it for smaller files.</li><li>Press <b>Convert</b>, then <b>Save</b> or <b>Save all</b>.</li></ol>
<h2>Frequently asked questions</h2>
<h3>Will my photos lose quality?</h3><p>At 90% or higher the difference is very hard to see. JPG files are usually somewhat larger than the HEIC originals.</p>
<h3>Can I stop my iPhone from taking HEIC photos?</h3><p>Yes. Go to <b>Settings → Camera → Formats</b> and choose <b>Most Compatible</b>. New photos will be saved as JPG.</p>
<h3>Are my photos uploaded?</h3><p>No. The conversion runs inside your browser, so your photos stay on your phone or computer.</p>''',
ko='''<h2>HEIC 사진이 안 열리는 이유</h2>
<p>아이폰은 2017년 iOS 11부터 사진을 기본으로 HEIC 형식으로 저장해요. HEIC는 JPG와 화질은 비슷하면서 용량이 작지만, 윈도우 프로그램, 일부 홈페이지, 사진 인화점, 오래된 휴대폰에서는 아직 열리지 않아요. JPG로 바꾸면 해결돼요.</p>
<h2>HEIC를 JPG로 바꾸는 법</h2>
<ol><li>위 상자를 눌러 HEIC 사진을 골라요. 여러 장을 한 번에 고를 수 있어요.</li><li>JPG가 이미 선택돼 있어요. 화질은 92% 그대로 두면 원본과 거의 같고, 낮추면 용량이 작아져요.</li><li><b>변환하기</b>를 누르고 <b>저장</b> 또는 <b>전체 저장</b>을 눌러요.</li></ol>
<h2>자주 묻는 질문</h2>
<h3>화질이 떨어지나요?</h3><p>90% 이상이면 눈으로 차이를 느끼기 어려워요. JPG 파일은 보통 HEIC 원본보다 용량이 조금 더 커요.</p>
<h3>아이폰이 처음부터 JPG로 찍게 할 수 있나요?</h3><p>네. <b>설정 → 카메라 → 포맷</b>에서 <b>높은 호환성</b>을 고르면 앞으로 찍는 사진은 JPG로 저장돼요.</p>
<h3>사진이 업로드되나요?</h3><p>아니요. 변환은 브라우저 안에서 이뤄져서 사진이 휴대폰이나 컴퓨터 밖으로 나가지 않아요.</p>''')

# ---------------------------------------------------------------- PNG to JPG
page('png-to-jpg', 'image', {'fmt': 'jpg', 'quality': 90},
M(
 en=dict(title='PNG to JPG Converter – Free, No Upload | PicShifter', desc='Convert PNG images to JPG for free and make them smaller. Batch conversion in your browser, no upload.', h1='PNG to JPG', sub='Turn PNG images into smaller JPG files. Converted on your device.'),
 ko=dict(title='PNG JPG 변환 | PicShifter', desc='PNG 이미지를 무료로 JPG로 바꿔 용량을 줄이세요. 여러 장을 브라우저에서 한 번에 변환, 업로드 없음.', h1='PNG를 JPG로', sub='PNG 이미지를 용량이 작은 JPG로 바꿔요. 내 기기 안에서 변환돼요.'),
 ja=dict(title='PNGをJPGに変換 – 無料・アップロード不要 | PicShifter', desc='PNG画像を無料でJPGに変換して軽くできます。ブラウザでまとめて変換、アップロード不要。', h1='PNGをJPGに', sub='PNG画像を軽いJPGに変換します。処理は端末内で行われます。'),
 zh=dict(title='PNG 转 JPG – 免费，无需上传 | PicShifter', desc='免费将 PNG 图片转换为更小的 JPG。在浏览器中批量转换，无需上传。', h1='PNG 转 JPG', sub='把 PNG 图片转换成更小的 JPG 文件。在你的设备上完成转换。'),
 es=dict(title='Convertir PNG a JPG – Gratis, sin subir archivos | PicShifter', desc='Convierte imágenes PNG a JPG gratis y redúcelas. Conversión por lotes en tu navegador, sin subir nada.', h1='PNG a JPG', sub='Convierte imágenes PNG en archivos JPG más ligeros. Todo en tu dispositivo.'),
 pt=dict(title='Converter PNG para JPG – Grátis, sem envio | PicShifter', desc='Converta imagens PNG para JPG de graça e deixe-as menores. Conversão em lote no navegador, sem envio.', h1='PNG para JPG', sub='Transforme imagens PNG em arquivos JPG menores. Tudo no seu dispositivo.'),
 fr=dict(title='Convertir PNG en JPG – Gratuit, sans envoi | PicShifter', desc='Convertissez gratuitement vos images PNG en JPG plus légers. Conversion par lot dans le navigateur, sans envoi.', h1='PNG en JPG', sub='Transformez vos images PNG en fichiers JPG plus légers. Conversion sur votre appareil.'),
 de=dict(title='PNG in JPG umwandeln – kostenlos, ohne Upload | PicShifter', desc='Wandle PNG-Bilder kostenlos in kleinere JPG-Dateien um. Stapelumwandlung im Browser, ohne Upload.', h1='PNG zu JPG', sub='Mach aus PNG-Bildern kleinere JPG-Dateien. Umgewandelt auf deinem Gerät.'),
),
en='''<h2>When to turn a PNG into a JPG</h2>
<p>PNG keeps every pixel exactly, which is great for screenshots and logos but makes photos large. JPG is built for photos: it drops detail you can’t easily see, so the same picture is often several times smaller. Use JPG when a site or form has a size limit, or when you want to send many photos quickly.</p>
<h2>How to convert</h2>
<ol><li>Choose your PNG files in the box above.</li><li>JPG is selected. Around 80–90% quality is a good balance between size and sharpness.</li><li>Press <b>Convert</b> and save the results. Each file shows how much smaller it became.</li></ol>
<h2>Frequently asked questions</h2>
<h3>What happens to transparent backgrounds?</h3><p>JPG can’t store transparency, so transparent areas become white. Keep PNG (or use WebP) if you need a see-through background.</p>
<h3>Should screenshots be JPG?</h3><p>Screenshots with text often look crisper as PNG. Converting them to JPG can add faint blur around letters, especially at low quality.</p>
<h3>Is there a file limit?</h3><p>No limit is set by the site. Very large images may be slower on phones.</p>''',
ko='''<h2>PNG를 JPG로 바꾸면 좋을 때</h2>
<p>PNG는 점 하나하나를 그대로 저장해서 캡처나 로고에는 좋지만, 사진은 용량이 커져요. JPG는 사진용 형식이라 눈에 잘 띄지 않는 부분을 덜어내서, 같은 사진도 몇 배 작아지는 경우가 많아요. 홈페이지나 서류 제출에 용량 제한이 있을 때, 사진을 여러 장 빨리 보내야 할 때 JPG가 좋아요.</p>
<h2>바꾸는 법</h2>
<ol><li>위 상자에서 PNG 파일을 골라요.</li><li>JPG가 선택돼 있어요. 화질은 80~90% 정도가 용량과 선명도의 균형이 좋아요.</li><li><b>변환하기</b>를 누르고 저장해요. 파일마다 얼마나 작아졌는지 보여줘요.</li></ol>
<h2>자주 묻는 질문</h2>
<h3>투명한 배경은 어떻게 되나요?</h3><p>JPG는 투명을 저장할 수 없어서 투명한 부분은 흰색이 돼요. 투명 배경이 필요하면 PNG나 WebP를 쓰세요.</p>
<h3>화면 캡처도 JPG가 좋나요?</h3><p>글자가 있는 캡처는 PNG가 더 선명한 경우가 많아요. JPG로 바꾸면, 특히 화질을 낮췄을 때 글자 주변이 살짝 번져 보일 수 있어요.</p>
<h3>파일 개수 제한이 있나요?</h3><p>사이트에서 정한 제한은 없어요. 아주 큰 이미지는 휴대폰에서 시간이 더 걸릴 수 있어요.</p>''')

# ---------------------------------------------------------------- JPG to PNG
page('jpg-to-png', 'image', {'fmt': 'png'},
M(
 en=dict(title='JPG to PNG Converter – Free, No Upload | PicShifter', desc='Convert JPG photos to PNG for free. Lossless output for editing and design, converted in your browser with no upload.', h1='JPG to PNG', sub='Turn JPG photos into PNG files for editing and design. Converted on your device.'),
 ko=dict(title='JPG PNG 변환 | PicShifter', desc='JPG 사진을 무료로 PNG로 바꾸세요. 편집과 디자인용 무손실 파일, 브라우저에서 변환, 업로드 없음.', h1='JPG를 PNG로', sub='JPG 사진을 편집·디자인용 PNG 파일로 바꿔요. 내 기기 안에서 변환돼요.'),
 ja=dict(title='JPGをPNGに変換 – 無料・アップロード不要 | PicShifter', desc='JPG写真を無料でPNGに変換。編集やデザインに使えるロスレス形式で、ブラウザ内で変換します。', h1='JPGをPNGに', sub='JPG写真を編集・デザイン向けのPNGに変換します。処理は端末内で行われます。'),
 zh=dict(title='JPG 转 PNG – 免费，无需上传 | PicShifter', desc='免费将 JPG 照片转换为 PNG，无损输出便于编辑和设计，在浏览器中完成，无需上传。', h1='JPG 转 PNG', sub='把 JPG 照片转换成便于编辑和设计的 PNG。在你的设备上完成转换。'),
 es=dict(title='Convertir JPG a PNG – Gratis, sin subir archivos | PicShifter', desc='Convierte fotos JPG a PNG gratis. Salida sin pérdidas para editar y diseñar, en tu navegador y sin subir nada.', h1='JPG a PNG', sub='Convierte fotos JPG en archivos PNG para editar y diseñar. Todo en tu dispositivo.'),
 pt=dict(title='Converter JPG para PNG – Grátis, sem envio | PicShifter', desc='Converta fotos JPG para PNG de graça. Saída sem perdas para edição e design, no navegador e sem envio.', h1='JPG para PNG', sub='Transforme fotos JPG em arquivos PNG para edição e design. Tudo no seu dispositivo.'),
 fr=dict(title='Convertir JPG en PNG – Gratuit, sans envoi | PicShifter', desc='Convertissez gratuitement vos photos JPG en PNG, sans perte, pour l’édition et le design. Dans le navigateur, sans envoi.', h1='JPG en PNG', sub='Transformez vos photos JPG en PNG pour l’édition et le design. Conversion sur votre appareil.'),
 de=dict(title='JPG in PNG umwandeln – kostenlos, ohne Upload | PicShifter', desc='Wandle JPG-Fotos kostenlos in PNG um. Verlustfreie Ausgabe für Bearbeitung und Design, im Browser ohne Upload.', h1='JPG zu PNG', sub='Mach aus JPG-Fotos PNG-Dateien für Bearbeitung und Design. Umgewandelt auf deinem Gerät.'),
),
en='''<h2>Why convert JPG to PNG</h2>
<p>Every time a JPG is edited and saved again, it loses a little more detail. PNG never throws detail away, so it’s a safer format while you’re still editing, adding text, or using an image in a design tool. Some upload forms and print services also ask for PNG.</p>
<h2>How to convert</h2>
<ol><li>Choose your JPG photos above.</li><li>PNG is already selected. PNG has no quality slider because it keeps everything.</li><li>Press <b>Convert</b> and save your PNG files.</li></ol>
<h2>Frequently asked questions</h2>
<h3>Will the photo look better as PNG?</h3><p>No. Converting can’t bring back detail the JPG already lost. It only stops further loss from now on.</p>
<h3>Why is the PNG so much bigger?</h3><p>PNG stores every pixel without compression tricks made for photos, so photo PNGs are often several times larger than the JPG.</p>
<h3>Does this make the background transparent?</h3><p>No. The picture stays the same. To cut out the background, use <a href="/remove-background/">Remove background</a>.</p>''',
ko='''<h2>JPG를 PNG로 바꾸는 이유</h2>
<p>JPG는 편집하고 다시 저장할 때마다 조금씩 화질이 떨어져요. PNG는 화질을 버리지 않아서, 편집 중이거나 글자를 넣거나 디자인 프로그램에서 쓸 때 더 안전해요. 일부 제출 양식이나 인쇄 업체도 PNG를 요구해요.</p>
<h2>바꾸는 법</h2>
<ol><li>위에서 JPG 사진을 골라요.</li><li>PNG가 이미 선택돼 있어요. PNG는 화질을 버리지 않아서 화질 조절이 없어요.</li><li><b>변환하기</b>를 누르고 PNG 파일을 저장해요.</li></ol>
<h2>자주 묻는 질문</h2>
<h3>PNG로 바꾸면 사진이 더 좋아지나요?</h3><p>아니요. JPG에서 이미 사라진 부분은 되살릴 수 없어요. 앞으로 더 나빠지는 것만 막아줘요.</p>
<h3>PNG가 왜 이렇게 커요?</h3><p>PNG는 사진용 압축 기법 없이 점을 모두 저장해서, 사진을 PNG로 바꾸면 JPG보다 몇 배 커지는 경우가 많아요.</p>
<h3>배경이 투명해지나요?</h3><p>아니요, 그림은 그대로예요. 배경을 지우려면 <a href="/remove-background/">배경 지우기</a>를 쓰세요.</p>''')

# ---------------------------------------------------------------- WebP to JPG
page('webp-to-jpg', 'image', {'fmt': 'jpg', 'quality': 90},
M(
 en=dict(title='WebP to JPG Converter – Free, No Upload | PicShifter', desc='Convert WebP images saved from websites to JPG for free. Batch conversion in your browser, no upload.', h1='WebP to JPG', sub='Turn WebP images from websites into JPG files that open everywhere. Converted on your device.'),
 ko=dict(title='WebP JPG 변환 | PicShifter', desc='웹사이트에서 저장한 WebP 이미지를 무료로 JPG로 바꾸세요. 브라우저에서 여러 장 변환, 업로드 없음.', h1='WebP를 JPG로', sub='웹에서 저장한 WebP 이미지를 어디서나 열리는 JPG로 바꿔요. 내 기기 안에서 변환돼요.'),
 ja=dict(title='WebPをJPGに変換 – 無料・アップロード不要 | PicShifter', desc='Webサイトから保存したWebP画像を無料でJPGに変換。ブラウザでまとめて変換、アップロード不要。', h1='WebPをJPGに', sub='Webから保存したWebP画像を、どこでも開けるJPGに変換します。処理は端末内で行われます。'),
 zh=dict(title='WebP 转 JPG – 免费，无需上传 | PicShifter', desc='免费将网页上保存的 WebP 图片转换为 JPG。在浏览器中批量转换，无需上传。', h1='WebP 转 JPG', sub='把网页上保存的 WebP 图片转换成到处都能打开的 JPG。在你的设备上完成转换。'),
 es=dict(title='Convertir WebP a JPG – Gratis, sin subir archivos | PicShifter', desc='Convierte imágenes WebP guardadas de páginas web a JPG gratis. Por lotes en tu navegador, sin subir nada.', h1='WebP a JPG', sub='Convierte imágenes WebP de páginas web en JPG que se abren en cualquier sitio. Todo en tu dispositivo.'),
 pt=dict(title='Converter WebP para JPG – Grátis, sem envio | PicShifter', desc='Converta imagens WebP salvas de sites para JPG de graça. Em lote no navegador, sem envio.', h1='WebP para JPG', sub='Transforme imagens WebP de sites em JPG que abrem em qualquer lugar. Tudo no seu dispositivo.'),
 fr=dict(title='Convertir WebP en JPG – Gratuit, sans envoi | PicShifter', desc='Convertissez gratuitement en JPG les images WebP enregistrées depuis des sites web. Par lot dans le navigateur, sans envoi.', h1='WebP en JPG', sub='Transformez les images WebP des sites web en JPG lisibles partout. Conversion sur votre appareil.'),
 de=dict(title='WebP in JPG umwandeln – kostenlos, ohne Upload | PicShifter', desc='Wandle von Websites gespeicherte WebP-Bilder kostenlos in JPG um. Stapelweise im Browser, ohne Upload.', h1='WebP zu JPG', sub='Mach aus WebP-Bildern von Websites JPG-Dateien, die sich überall öffnen lassen. Umgewandelt auf deinem Gerät.'),
),
en='''<h2>What is a WebP file?</h2>
<p>WebP is an image format Google introduced in 2010 to make websites load faster. Many sites now serve their pictures as WebP, so when you save an image from a browser you often get a .webp file. Some photo editors, office programs and upload forms still won’t accept it.</p>
<h2>How to convert WebP to JPG</h2>
<ol><li>Choose your WebP images above.</li><li>JPG is selected. Keep quality around 90% to look the same as the original.</li><li>Press <b>Convert</b> and save the JPG files.</li></ol>
<h2>Frequently asked questions</h2>
<h3>Can I convert animated WebP?</h3><p>Only the first frame is converted, so the result is a still image.</p>
<h3>What about transparent WebP images?</h3><p>JPG has no transparency, so those areas turn white. Pick PNG in the format menu to keep them see-through.</p>
<h3>Is it allowed to convert images from websites?</h3><p>Converting the file format is fine, but the picture itself may still be protected by copyright. Check you have the right to use it.</p>''',
ko='''<h2>WebP 파일이 뭐예요?</h2>
<p>WebP는 홈페이지를 빨리 뜨게 하려고 구글이 2010년에 내놓은 이미지 형식이에요. 요즘은 많은 사이트가 그림을 WebP로 보여줘서, 브라우저에서 이미지를 저장하면 .webp 파일이 되는 경우가 많아요. 그런데 일부 사진 편집 프로그램, 문서 프로그램, 제출 양식은 아직 WebP를 받지 않아요.</p>
<h2>WebP를 JPG로 바꾸는 법</h2>
<ol><li>위에서 WebP 이미지를 골라요.</li><li>JPG가 선택돼 있어요. 화질을 90% 정도로 두면 원본과 거의 같아 보여요.</li><li><b>변환하기</b>를 누르고 JPG 파일을 저장해요.</li></ol>
<h2>자주 묻는 질문</h2>
<h3>움직이는 WebP도 되나요?</h3><p>첫 번째 장면만 변환돼서 멈춘 이미지가 돼요.</p>
<h3>투명한 WebP는요?</h3><p>JPG는 투명을 저장할 수 없어서 그 부분이 흰색이 돼요. 투명을 유지하려면 형식에서 PNG를 고르세요.</p>
<h3>웹사이트 이미지를 변환해도 되나요?</h3><p>파일 형식을 바꾸는 건 괜찮지만, 그림 자체는 저작권으로 보호될 수 있어요. 쓸 권리가 있는지 확인하세요.</p>''')

# ---------------------------------------------------------------- JPG to PDF
page('jpg-to-pdf', 'image', {'fmt': 'pdf', 'quality': 85},
M(
 en=dict(title='JPG to PDF – Combine Images into One PDF, Free | PicShifter', desc='Combine JPG, PNG and HEIC photos into a single PDF for free. Great for receipts and documents. Runs in your browser, no upload.', h1='JPG to PDF', sub='Put one or many photos into a single PDF file. Converted on your device.'),
 ko=dict(title='JPG PDF 변환 | PicShifter', desc='JPG, PNG, HEIC 사진 여러 장을 무료로 PDF 하나로 합치세요. 영수증·서류 제출에 좋아요. 브라우저에서 처리, 업로드 없음.', h1='JPG를 PDF로', sub='사진 한 장 또는 여러 장을 PDF 파일 하나로 만들어요. 내 기기 안에서 변환돼요.'),
 ja=dict(title='JPGをPDFに – 複数の画像を1つのPDFに・無料 | PicShifter', desc='JPG・PNG・HEICの写真を無料で1つのPDFにまとめます。レシートや書類の提出に便利。ブラウザで処理、アップロード不要。', h1='JPGをPDFに', sub='1枚または複数の写真を1つのPDFファイルにまとめます。処理は端末内で行われます。'),
 zh=dict(title='JPG 转 PDF – 多张图片合成一个 PDF，免费 | PicShifter', desc='免费将 JPG、PNG、HEIC 照片合并成一个 PDF，适合提交收据和文件。在浏览器中处理，无需上传。', h1='JPG 转 PDF', sub='把一张或多张照片放进一个 PDF 文件。在你的设备上完成转换。'),
 es=dict(title='JPG a PDF – Une imágenes en un solo PDF gratis | PicShifter', desc='Une fotos JPG, PNG y HEIC en un solo PDF gratis. Ideal para recibos y documentos. En tu navegador, sin subir nada.', h1='JPG a PDF', sub='Pon una o varias fotos en un solo archivo PDF. Todo en tu dispositivo.'),
 pt=dict(title='JPG para PDF – Junte imagens em um só PDF, grátis | PicShifter', desc='Junte fotos JPG, PNG e HEIC em um único PDF de graça. Ótimo para recibos e documentos. No navegador, sem envio.', h1='JPG para PDF', sub='Coloque uma ou várias fotos em um único arquivo PDF. Tudo no seu dispositivo.'),
 fr=dict(title='JPG en PDF – Réunir des images dans un seul PDF, gratuit | PicShifter', desc='Réunissez gratuitement des photos JPG, PNG et HEIC dans un seul PDF. Idéal pour tickets et documents. Dans le navigateur, sans envoi.', h1='JPG en PDF', sub='Placez une ou plusieurs photos dans un seul fichier PDF. Conversion sur votre appareil.'),
 de=dict(title='JPG in PDF – Bilder zu einer PDF zusammenfügen, kostenlos | PicShifter', desc='Füge JPG-, PNG- und HEIC-Fotos kostenlos zu einer PDF zusammen. Ideal für Belege und Dokumente. Im Browser, ohne Upload.', h1='JPG zu PDF', sub='Pack ein oder mehrere Fotos in eine einzige PDF-Datei. Umgewandelt auf deinem Gerät.'),
),
en='''<h2>One PDF from many photos</h2>
<p>Forms and email often ask for “one PDF” instead of a pile of photos. This page puts every image you choose into a single PDF, one image per page, in the order you added them. Each page takes the size of its photo, so nothing is stretched or cropped.</p>
<h2>How to make a PDF from images</h2>
<ol><li>Choose your photos above, in the order you want the pages.</li><li>PDF is selected and <b>Combine into one PDF</b> is on. Turn it off to get a separate PDF for each photo.</li><li>Lower the quality to about 70% if the PDF must stay under a size limit.</li><li>Press <b>Convert</b> and save the PDF.</li></ol>
<h2>Frequently asked questions</h2>
<h3>Can I use HEIC or PNG photos too?</h3><p>Yes. Any image the converter can open can go into the PDF.</p>
<h3>My photos are of paper documents. Can they look like a scan?</h3><p>Use <a href="/scan/">Photo to scan</a>. It straightens the page and removes shadows before making the PDF.</p>
<h3>Are transparent areas kept?</h3><p>No. Transparent parts become white in the PDF.</p>''',
ko='''<h2>사진 여러 장을 PDF 하나로</h2>
<p>서류 제출이나 메일에서 사진 여러 장 대신 "PDF 파일 하나"를 요구할 때가 많아요. 이 페이지는 고른 사진을 한 장당 한 쪽씩, 추가한 순서대로 PDF 하나에 담아요. 각 쪽은 사진 크기에 맞춰져서 늘어나거나 잘리지 않아요.</p>
<h2>사진으로 PDF 만드는 법</h2>
<ol><li>위에서 사진을 원하는 쪽 순서대로 골라요.</li><li>PDF가 선택돼 있고 <b>PDF 파일 하나로 합치기</b>가 켜져 있어요. 끄면 사진마다 PDF가 따로 만들어져요.</li><li>용량 제한이 있으면 화질을 70% 정도로 낮춰요.</li><li><b>변환하기</b>를 누르고 PDF를 저장해요.</li></ol>
<h2>자주 묻는 질문</h2>
<h3>HEIC나 PNG 사진도 되나요?</h3><p>네. 변환기가 열 수 있는 이미지는 모두 PDF에 넣을 수 있어요.</p>
<h3>종이 서류를 찍은 사진인데 스캔본처럼 만들 수 있나요?</h3><p><a href="/scan/">사진 → 스캔본</a>을 쓰세요. 종이를 반듯하게 펴고 그림자를 지운 다음 PDF로 만들어줘요.</p>
<h3>투명한 부분은 유지되나요?</h3><p>아니요. PDF에서는 투명한 부분이 흰색이 돼요.</p>''')

# ---------------------------------------------------------------- PDF to JPG
page('pdf-to-jpg', 'image', {'fmt': 'jpg', 'quality': 90, 'accept': 'application/pdf,.pdf'},
M(
 en=dict(title='PDF to JPG – Convert PDF Pages to Images, Free | PicShifter', desc='Turn every page of a PDF into a JPG image for free. Works in your browser, no upload.', h1='PDF to JPG', sub='Save each page of a PDF as a JPG image. Converted on your device.'),
 ko=dict(title='PDF JPG 변환 | PicShifter', desc='PDF의 모든 페이지를 무료로 JPG 이미지로 바꾸세요. 브라우저에서 처리, 업로드 없음.', h1='PDF를 JPG로', sub='PDF의 쪽마다 JPG 이미지로 저장해요. 내 기기 안에서 변환돼요.'),
 ja=dict(title='PDFをJPGに – PDFのページを画像に変換・無料 | PicShifter', desc='PDFの全ページを無料でJPG画像に変換。ブラウザで処理、アップロード不要。', h1='PDFをJPGに', sub='PDFの各ページをJPG画像として保存します。処理は端末内で行われます。'),
 zh=dict(title='PDF 转 JPG – 把 PDF 页面转成图片，免费 | PicShifter', desc='免费将 PDF 的每一页转换为 JPG 图片。在浏览器中完成，无需上传。', h1='PDF 转 JPG', sub='把 PDF 的每一页保存为 JPG 图片。在你的设备上完成转换。'),
 es=dict(title='PDF a JPG – Convierte páginas PDF en imágenes gratis | PicShifter', desc='Convierte cada página de un PDF en una imagen JPG gratis. En tu navegador, sin subir nada.', h1='PDF a JPG', sub='Guarda cada página de un PDF como imagen JPG. Todo en tu dispositivo.'),
 pt=dict(title='PDF para JPG – Converta páginas de PDF em imagens, grátis | PicShifter', desc='Transforme cada página de um PDF em imagem JPG de graça. No navegador, sem envio.', h1='PDF para JPG', sub='Salve cada página de um PDF como imagem JPG. Tudo no seu dispositivo.'),
 fr=dict(title='PDF en JPG – Convertir les pages d’un PDF en images, gratuit | PicShifter', desc='Transformez gratuitement chaque page d’un PDF en image JPG. Dans votre navigateur, sans envoi.', h1='PDF en JPG', sub='Enregistrez chaque page d’un PDF en image JPG. Conversion sur votre appareil.'),
 de=dict(title='PDF in JPG – PDF-Seiten als Bilder speichern, kostenlos | PicShifter', desc='Wandle jede Seite einer PDF kostenlos in ein JPG-Bild um. Im Browser, ohne Upload.', h1='PDF zu JPG', sub='Speichere jede Seite einer PDF als JPG-Bild. Umgewandelt auf deinem Gerät.'),
),
en='''<h2>When you need a PDF as pictures</h2>
<p>Images are easier to post on social media, paste into chats and presentations, or upload where PDFs aren’t accepted. This page renders every page of your PDF and saves it as its own JPG.</p>
<h2>How to convert PDF to JPG</h2>
<ol><li>Choose a PDF above. You can add several PDFs at once.</li><li>JPG is selected. Choose PNG instead if the pages are mostly text and you want the sharpest letters.</li><li>Press <b>Convert</b>. Each page gets its own <b>1, 2, 3…</b> save button.</li></ol>
<h2>Frequently asked questions</h2>
<h3>How sharp are the images?</h3><p>Pages are drawn at twice the normal screen size, which is clear enough for reading on phones and in slides.</p>
<h3>Do Korean, Japanese and Chinese PDFs work?</h3><p>Yes. The character maps for these languages are included, so text shows correctly in most PDFs, even ones that don’t embed their fonts.</p>
<h3>Can I open password-protected PDFs?</h3><p>Not yet. Remove the password first.</p>''',
ko='''<h2>PDF를 그림으로 바꿔야 할 때</h2>
<p>이미지는 SNS에 올리거나, 메신저·발표 자료에 붙이거나, PDF를 받지 않는 곳에 올리기 편해요. 이 페이지는 PDF의 모든 쪽을 그려서 쪽마다 JPG로 저장해줘요.</p>
<h2>PDF를 JPG로 바꾸는 법</h2>
<ol><li>위에서 PDF를 골라요. 여러 개를 한 번에 넣어도 돼요.</li><li>JPG가 선택돼 있어요. 글자 위주의 문서라 글씨를 가장 선명하게 하고 싶으면 PNG를 고르세요.</li><li><b>변환하기</b>를 누르면 쪽마다 <b>1, 2, 3…</b> 저장 버튼이 생겨요.</li></ol>
<h2>자주 묻는 질문</h2>
<h3>이미지가 얼마나 선명한가요?</h3><p>보통 화면 크기의 두 배로 그려서, 휴대폰이나 발표 자료에서 읽기에 충분히 선명해요.</p>
<h3>한글·일본어·중국어 PDF도 되나요?</h3><p>네. 이런 언어용 문자 정보가 들어 있어서, 글꼴이 포함되지 않은 PDF도 대부분 글자가 제대로 보여요.</p>
<h3>암호가 걸린 PDF도 열 수 있나요?</h3><p>아직은 안 돼요. 암호를 먼저 풀어주세요.</p>''')

# ---------------------------------------------------------------- Compress image
page('compress-image', 'image', {'fmt': 'jpg', 'quality': 70},
M(
 en=dict(title='Compress Image – Reduce JPG, PNG & HEIC File Size, Free | PicShifter', desc='Make photos smaller for email, forms and websites. Compress JPG, PNG and HEIC images for free in your browser, no upload.', h1='Compress images', sub='Shrink photo file sizes while keeping them looking good. Everything happens on your device.'),
 ko=dict(title='사진 용량 줄이기 | PicShifter', desc='메일·서류 제출·홈페이지용으로 사진 용량을 줄이세요. JPG, PNG, HEIC를 브라우저에서 무료로 압축, 업로드 없음.', h1='사진 용량 줄이기', sub='보기 좋은 화질은 유지하면서 사진 용량을 줄여요. 모든 작업은 내 기기 안에서 이뤄져요.'),
 ja=dict(title='画像を圧縮 – JPG・PNG・HEICのサイズを小さく・無料 | PicShifter', desc='メールや提出フォーム、Webサイト向けに写真を軽くします。JPG・PNG・HEICをブラウザで無料圧縮、アップロード不要。', h1='画像を圧縮', sub='見た目を保ったまま写真のファイルサイズを小さくします。処理は端末内で行われます。'),
 zh=dict(title='图片压缩 – 减小 JPG、PNG、HEIC 文件大小，免费 | PicShifter', desc='为邮件、表单和网站压缩照片。在浏览器中免费压缩 JPG、PNG 和 HEIC，无需上传。', h1='压缩图片', sub='在保持观感的同时减小照片文件大小。所有操作都在你的设备上完成。'),
 es=dict(title='Comprimir imágenes – Reduce el tamaño de JPG, PNG y HEIC gratis | PicShifter', desc='Haz tus fotos más ligeras para correos, formularios y webs. Comprime JPG, PNG y HEIC gratis en tu navegador, sin subir nada.', h1='Comprimir imágenes', sub='Reduce el tamaño de tus fotos sin que pierdan buen aspecto. Todo ocurre en tu dispositivo.'),
 pt=dict(title='Comprimir imagens – Reduza o tamanho de JPG, PNG e HEIC, grátis | PicShifter', desc='Deixe fotos menores para e-mail, formulários e sites. Comprima JPG, PNG e HEIC de graça no navegador, sem envio.', h1='Comprimir imagens', sub='Diminua o tamanho das fotos mantendo a boa aparência. Tudo acontece no seu dispositivo.'),
 fr=dict(title='Compresser une image – Réduire JPG, PNG et HEIC, gratuit | PicShifter', desc='Allégez vos photos pour l’e-mail, les formulaires et le web. Compressez JPG, PNG et HEIC gratuitement dans le navigateur, sans envoi.', h1='Compresser des images', sub='Réduisez le poids de vos photos tout en gardant une belle image. Tout se passe sur votre appareil.'),
 de=dict(title='Bilder komprimieren – JPG, PNG und HEIC verkleinern, kostenlos | PicShifter', desc='Mach Fotos kleiner für E-Mail, Formulare und Websites. Komprimiere JPG, PNG und HEIC kostenlos im Browser, ohne Upload.', h1='Bilder komprimieren', sub='Verkleinere Fotodateien, ohne dass sie schlechter aussehen. Alles passiert auf deinem Gerät.'),
),
en='''<h2>Why compress photos</h2>
<p>Phone photos are often 3–10 MB each. Email attachments, job and school applications and website uploads frequently have limits of a few megabytes. Saving a photo as JPG at a lower quality removes detail you can barely see and can make the file several times smaller.</p>
<h2>How to compress</h2>
<ol><li>Choose your photos above.</li><li>The quality is set to 70%, which usually shrinks files a lot with little visible change. Go lower for smaller files, higher for sharper ones.</li><li>For website images, choose <b>WebP</b> in the format menu. It is usually smaller than JPG at the same quality.</li><li>Press <b>Convert</b>. Each file shows the old size, the new size and the percentage saved.</li></ol>
<h2>Frequently asked questions</h2>
<h3>How small can I go?</h3><p>Below about 50% you may start to see blocky patches, especially in skies and skin. Try a few settings and compare.</p>
<h3>Does this change the width and height?</h3><p>No. The image keeps its size in pixels; only the file gets smaller.</p>
<h3>Why did a file get bigger?</h3><p>If the original was already heavily compressed, or was a small PNG graphic, re-saving may not help. Keep the original in that case.</p>''',
ko='''<h2>사진 용량을 줄여야 하는 이유</h2>
<p>휴대폰 사진은 한 장에 3~10MB인 경우가 많아요. 그런데 메일 첨부, 입사·입학 지원서, 홈페이지 업로드는 몇 MB로 제한된 곳이 많죠. 사진을 화질을 조금 낮춘 JPG로 저장하면 눈에 거의 띄지 않는 부분만 덜어내서 용량이 몇 배 줄어들 수 있어요.</p>
<h2>줄이는 법</h2>
<ol><li>위에서 사진을 골라요.</li><li>화질이 70%로 맞춰져 있어요. 보통 눈에 띄는 차이 없이 용량이 많이 줄어요. 더 작게 하려면 낮추고, 더 선명하게 하려면 올려요.</li><li>홈페이지용 이미지라면 형식에서 <b>WebP</b>를 고르세요. 같은 화질이면 보통 JPG보다 작아요.</li><li><b>변환하기</b>를 누르면 파일마다 원래 용량, 줄어든 용량, 몇 % 줄었는지 보여줘요.</li></ol>
<h2>자주 묻는 질문</h2>
<h3>얼마나 낮춰도 되나요?</h3><p>50% 아래로 내려가면 하늘이나 피부 같은 곳에 네모난 얼룩이 보이기 시작할 수 있어요. 몇 가지 값으로 비교해 보세요.</p>
<h3>사진 가로세로 크기도 바뀌나요?</h3><p>아니요. 픽셀 크기는 그대로고 파일 용량만 줄어요.</p>
<h3>왜 오히려 커진 파일이 있죠?</h3><p>원본이 이미 많이 압축됐거나 작은 PNG 그림이면 다시 저장해도 줄지 않을 수 있어요. 그럴 땐 원본을 쓰세요.</p>''')

# ---------------------------------------------------------------- PNG to ICO
page('png-to-ico', 'image', {'fmt': 'ico'},
M(
 en=dict(title='PNG to ICO – Favicon & Icon Maker, Free | PicShifter', desc='Convert PNG, JPG or SVG images into ICO icons and website favicons with 16–256 px sizes in one file. Free, in your browser.', h1='PNG to ICO', sub='Make a website favicon or Windows icon from any image. Created on your device.'),
 ko=dict(title='PNG ICO 변환 | PicShifter', desc='PNG, JPG, SVG 이미지를 16~256px 크기가 한 파일에 담긴 ICO 아이콘·파비콘으로 무료 변환. 브라우저에서 처리.', h1='PNG를 ICO로', sub='아무 이미지로 홈페이지 파비콘이나 윈도우 아이콘을 만들어요. 내 기기 안에서 만들어져요.'),
 ja=dict(title='PNGをICOに – ファビコン・アイコン作成・無料 | PicShifter', desc='PNG・JPG・SVG画像を、16〜256pxのサイズを1つにまとめたICOアイコンやファビコンに無料で変換。ブラウザ内で処理。', h1='PNGをICOに', sub='好きな画像からWebサイトのファビコンやWindowsアイコンを作ります。処理は端末内で行われます。'),
 zh=dict(title='PNG 转 ICO – 免费制作网站图标和 favicon | PicShifter', desc='把 PNG、JPG 或 SVG 图片转换为包含 16–256 px 多种尺寸的 ICO 图标和网站 favicon。免费，在浏览器中完成。', h1='PNG 转 ICO', sub='用任意图片制作网站 favicon 或 Windows 图标。在你的设备上生成。'),
 es=dict(title='PNG a ICO – Crea favicons e iconos gratis | PicShifter', desc='Convierte imágenes PNG, JPG o SVG en iconos ICO y favicons con tamaños de 16 a 256 px en un solo archivo. Gratis, en tu navegador.', h1='PNG a ICO', sub='Crea el favicon de tu web o un icono de Windows a partir de cualquier imagen. Todo en tu dispositivo.'),
 pt=dict(title='PNG para ICO – Crie favicons e ícones grátis | PicShifter', desc='Converta imagens PNG, JPG ou SVG em ícones ICO e favicons com tamanhos de 16 a 256 px em um só arquivo. Grátis, no navegador.', h1='PNG para ICO', sub='Crie o favicon do seu site ou um ícone do Windows a partir de qualquer imagem. Tudo no seu dispositivo.'),
 fr=dict(title='PNG en ICO – Créer favicon et icônes, gratuit | PicShifter', desc='Convertissez des images PNG, JPG ou SVG en icônes ICO et favicons de 16 à 256 px dans un seul fichier. Gratuit, dans le navigateur.', h1='PNG en ICO', sub='Créez le favicon de votre site ou une icône Windows à partir de n’importe quelle image. Sur votre appareil.'),
 de=dict(title='PNG in ICO – Favicon und Icons erstellen, kostenlos | PicShifter', desc='Wandle PNG-, JPG- oder SVG-Bilder in ICO-Icons und Website-Favicons mit 16–256 px in einer Datei um. Kostenlos im Browser.', h1='PNG zu ICO', sub='Erstelle ein Website-Favicon oder Windows-Icon aus einem beliebigen Bild. Erstellt auf deinem Gerät.'),
),
en='''<h2>What an ICO file is for</h2>
<p>ICO is the icon format used by Windows and by the small “favicon” that appears on browser tabs and bookmarks. One ICO file can hold several sizes so each place can pick the sharpest one. This page creates 16, 32, 48, 64, 128 and 256 pixel versions in a single file.</p>
<h2>How to make a favicon</h2>
<ol><li>Choose a square image, ideally a PNG with a transparent background and at least 256×256 pixels.</li><li>ICO is already selected. Non-square images are centred and padded so nothing is cut off.</li><li>Press <b>Convert</b> and save the file as <b>favicon.ico</b>.</li><li>Upload it to the main folder of your website. Most browsers look for /favicon.ico automatically.</li></ol>
<h2>Frequently asked questions</h2>
<h3>Why does my icon look blurry at 16 px?</h3><p>Detailed logos lose clarity when they’re that small. A simplified version of the logo, or just its first letter, usually works better.</p>
<h3>Can I make a mouse cursor?</h3><p>Yes. Choose <b>CUR</b> in the format menu to make a Windows cursor file.</p>
<h3>Is transparency kept?</h3><p>Yes. Transparent areas stay transparent in every size.</p>''',
ko='''<h2>ICO 파일은 어디에 쓰나요?</h2>
<p>ICO는 윈도우 아이콘과, 브라우저 탭·즐겨찾기에 보이는 작은 "파비콘"에 쓰이는 형식이에요. ICO 파일 하나에 여러 크기를 담을 수 있어서, 보이는 곳마다 가장 선명한 크기를 골라 써요. 이 페이지는 16, 32, 48, 64, 128, 256픽셀 크기를 파일 하나에 만들어줘요.</p>
<h2>파비콘 만드는 법</h2>
<ol><li>정사각형 이미지를 골라요. 배경이 투명한 PNG, 256×256픽셀 이상이면 가장 좋아요.</li><li>ICO가 이미 선택돼 있어요. 정사각형이 아니면 가운데에 놓고 빈 곳을 채워서 잘리지 않게 해요.</li><li><b>변환하기</b>를 누르고 <b>favicon.ico</b>라는 이름으로 저장해요.</li><li>홈페이지의 가장 바깥 폴더에 올려요. 대부분의 브라우저가 /favicon.ico를 알아서 찾아요.</li></ol>
<h2>자주 묻는 질문</h2>
<h3>16픽셀에서 아이콘이 흐려 보여요.</h3><p>복잡한 로고는 그렇게 작아지면 알아보기 어려워요. 로고를 단순하게 하거나 첫 글자만 쓰면 더 잘 보여요.</p>
<h3>마우스 커서도 만들 수 있나요?</h3><p>네. 형식에서 <b>CUR</b>를 고르면 윈도우 커서 파일이 만들어져요.</p>
<h3>투명한 부분이 유지되나요?</h3><p>네. 모든 크기에서 투명한 부분은 그대로 투명해요.</p>''')

# ---------------------------------------------------------------- Documents
DOC_ACCEPT = {'word': '.docx', 'excel': '.xlsx,.xlsm,.xls,.ods,.csv', 'ppt': '.pptx', 'hwp': '.hwp,.hwpx'}

page('word-to-pdf', 'doc', {'accept': '.docx,.doc'},
M(
 en=dict(title='Word to PDF – Convert DOCX to PDF Free, No Upload | PicShifter', desc='Convert Word (DOCX) documents to PDF for free, right in your browser. No sign-up and no upload.', h1='Word to PDF', sub='Turn Word (DOCX) documents into PDF. Everything happens on your device.'),
 ko=dict(title='워드 PDF 변환 | PicShifter', desc='워드(DOCX) 문서를 브라우저에서 바로 무료로 PDF로 바꾸세요. 가입도 업로드도 필요 없어요.', h1='워드를 PDF로', sub='워드(DOCX) 문서를 PDF로 바꿔요. 모든 작업은 내 기기 안에서 이뤄져요.'),
 ja=dict(title='WordをPDFに – DOCXを無料でPDF変換 | PicShifter', desc='Word（DOCX）文書をブラウザで無料でPDFに変換。登録もアップロードも不要です。', h1='WordをPDFに', sub='Word（DOCX）文書をPDFに変換します。処理は端末内で行われます。'),
 zh=dict(title='Word 转 PDF – 免费将 DOCX 转为 PDF | PicShifter', desc='在浏览器中免费将 Word（DOCX）文档转换为 PDF，无需注册，无需上传。', h1='Word 转 PDF', sub='把 Word（DOCX）文档转换为 PDF。所有操作都在你的设备上完成。'),
 es=dict(title='Word a PDF – Convierte DOCX a PDF gratis | PicShifter', desc='Convierte documentos de Word (DOCX) a PDF gratis en tu navegador. Sin registro y sin subir archivos.', h1='Word a PDF', sub='Convierte documentos de Word (DOCX) en PDF. Todo ocurre en tu dispositivo.'),
 pt=dict(title='Word para PDF – Converta DOCX em PDF grátis | PicShifter', desc='Converta documentos do Word (DOCX) em PDF de graça no navegador. Sem cadastro e sem envio.', h1='Word para PDF', sub='Transforme documentos do Word (DOCX) em PDF. Tudo acontece no seu dispositivo.'),
 fr=dict(title='Word en PDF – Convertir un DOCX en PDF gratuitement | PicShifter', desc='Convertissez gratuitement vos documents Word (DOCX) en PDF dans le navigateur. Sans inscription ni envoi.', h1='Word en PDF', sub='Transformez vos documents Word (DOCX) en PDF. Tout se passe sur votre appareil.'),
 de=dict(title='Word in PDF – DOCX kostenlos in PDF umwandeln | PicShifter', desc='Wandle Word-Dokumente (DOCX) kostenlos im Browser in PDF um. Ohne Anmeldung und ohne Upload.', h1='Word zu PDF', sub='Mach aus Word-Dokumenten (DOCX) eine PDF. Alles passiert auf deinem Gerät.'),
),
en='''<h2>Why send Word files as PDF</h2>
<p>A Word file can look different on someone else’s computer if they have other fonts or another version of Word, and it can be edited by mistake. A PDF looks the same everywhere, which is why job applications, schools and offices usually ask for one.</p>
<h2>How to convert Word to PDF</h2>
<ol><li>Choose your .docx files above. You can add several at once.</li><li>Press <b>Convert to PDF</b> and wait for the progress bar.</li><li>Press <b>Save</b> to download each PDF.</li></ol>
<h2>Frequently asked questions</h2>
<h3>Will the layout stay the same?</h3><p>Text, tables, pictures and page breaks are kept. Complex layouts, text boxes and fonts that aren’t on your device may look slightly different, so check the PDF before you send it.</p>
<h3>Can I select the text in the PDF?</h3><p>No. Pages are saved as images, so the text can’t be selected or searched.</p>
<h3>What about old .doc files?</h3><p>Open them in Word or another editor and save as .docx first.</p>''',
ko='''<h2>워드 파일을 PDF로 보내는 이유</h2>
<p>워드 파일은 받는 사람의 컴퓨터에 다른 글꼴이나 다른 버전의 워드가 있으면 모양이 달라질 수 있고, 실수로 수정될 수도 있어요. PDF는 어디서 열어도 똑같이 보여서 입사 지원, 학교 과제, 회사 서류는 대부분 PDF를 요구해요.</p>
<h2>워드를 PDF로 바꾸는 법</h2>
<ol><li>위에서 .docx 파일을 골라요. 여러 개를 한 번에 넣어도 돼요.</li><li><b>PDF로 변환</b>을 누르고 진행 막대가 끝날 때까지 기다려요.</li><li><b>저장</b>을 눌러 PDF를 받아요.</li></ol>
<h2>자주 묻는 질문</h2>
<h3>모양이 그대로 유지되나요?</h3><p>글자, 표, 그림, 페이지 나누기는 유지돼요. 복잡한 배치, 글상자, 내 기기에 없는 글꼴은 조금 달라 보일 수 있으니 보내기 전에 PDF를 확인하세요.</p>
<h3>PDF에서 글자를 선택할 수 있나요?</h3><p>아니요. 페이지가 그림으로 저장돼서 글자를 선택하거나 검색할 수 없어요.</p>
<h3>예전 .doc 파일은요?</h3><p>워드나 다른 편집 프로그램에서 열어 .docx로 저장한 뒤 사용하세요.</p>''')

page('excel-to-pdf', 'doc', {'accept': '.xlsx,.xlsm,.xls,.ods,.csv'},
M(
 en=dict(title='Excel to PDF – Convert XLSX, XLS & CSV to PDF Free | PicShifter', desc='Convert Excel spreadsheets (XLSX, XLS, CSV) to PDF for free. Every sheet becomes printable pages. Runs in your browser, no upload.', h1='Excel to PDF', sub='Turn Excel sheets into PDF pages you can print or share. Everything happens on your device.'),
 ko=dict(title='엑셀 PDF 변환 | PicShifter', desc='엑셀 파일(XLSX, XLS, CSV)을 무료로 PDF로 바꾸세요. 시트마다 인쇄용 페이지로. 브라우저에서 처리, 업로드 없음.', h1='엑셀을 PDF로', sub='엑셀 시트를 인쇄하거나 공유하기 좋은 PDF로 바꿔요. 모든 작업은 내 기기 안에서 이뤄져요.'),
 ja=dict(title='ExcelをPDFに – XLSX・XLS・CSVを無料でPDF変換 | PicShifter', desc='Excel（XLSX・XLS・CSV）を無料でPDFに変換。各シートを印刷用ページにします。ブラウザで処理、アップロード不要。', h1='ExcelをPDFに', sub='Excelのシートを、印刷や共有に便利なPDFに変換します。処理は端末内で行われます。'),
 zh=dict(title='Excel 转 PDF – 免费将 XLSX、XLS、CSV 转为 PDF | PicShifter', desc='免费将 Excel 表格（XLSX、XLS、CSV）转换为 PDF，每个工作表都变成可打印页面。在浏览器中处理，无需上传。', h1='Excel 转 PDF', sub='把 Excel 工作表转换成便于打印和分享的 PDF。所有操作都在你的设备上完成。'),
 es=dict(title='Excel a PDF – Convierte XLSX, XLS y CSV a PDF gratis | PicShifter', desc='Convierte hojas de Excel (XLSX, XLS, CSV) a PDF gratis. Cada hoja se convierte en páginas imprimibles. En tu navegador, sin subir nada.', h1='Excel a PDF', sub='Convierte hojas de Excel en páginas PDF para imprimir o compartir. Todo ocurre en tu dispositivo.'),
 pt=dict(title='Excel para PDF – Converta XLSX, XLS e CSV em PDF grátis | PicShifter', desc='Converta planilhas do Excel (XLSX, XLS, CSV) em PDF de graça. Cada aba vira páginas para imprimir. No navegador, sem envio.', h1='Excel para PDF', sub='Transforme planilhas do Excel em páginas PDF para imprimir ou compartilhar. Tudo no seu dispositivo.'),
 fr=dict(title='Excel en PDF – Convertir XLSX, XLS et CSV en PDF gratuitement | PicShifter', desc='Convertissez gratuitement vos classeurs Excel (XLSX, XLS, CSV) en PDF. Chaque feuille devient des pages imprimables. Dans le navigateur, sans envoi.', h1='Excel en PDF', sub='Transformez vos feuilles Excel en pages PDF à imprimer ou partager. Tout se passe sur votre appareil.'),
 de=dict(title='Excel in PDF – XLSX, XLS und CSV kostenlos in PDF umwandeln | PicShifter', desc='Wandle Excel-Tabellen (XLSX, XLS, CSV) kostenlos in PDF um. Jedes Blatt wird zu druckbaren Seiten. Im Browser, ohne Upload.', h1='Excel zu PDF', sub='Mach aus Excel-Blättern PDF-Seiten zum Drucken oder Teilen. Alles passiert auf deinem Gerät.'),
),
en='''<h2>Sharing spreadsheets as PDF</h2>
<p>A PDF is the easiest way to send a price list, schedule or report to someone who just needs to read or print it. They don’t need Excel, and they can’t change your numbers by accident.</p>
<h2>How to convert Excel to PDF</h2>
<ol><li>Choose your .xlsx, .xls or .csv files above.</li><li>Press <b>Convert to PDF</b>.</li><li>Save the PDF. Each sheet starts on a new page with its name at the top.</li></ol>
<h2>What to expect</h2>
<ul><li>Cell values are shown as they appear in Excel, including number formats.</li><li>Long sheets continue over several A4 pages; very wide sheets switch to landscape.</li><li>Charts, images, colours and print settings from Excel are not included. For those, use “Save as PDF” in Excel itself.</li></ul>
<h2>Frequently asked questions</h2>
<h3>Are formulas kept?</h3><p>The PDF shows the calculated results, not the formulas.</p>
<h3>Can I convert a CSV file?</h3><p>Yes. CSV files are read as a single sheet.</p>''',
ko='''<h2>엑셀을 PDF로 공유하면 좋은 점</h2>
<p>가격표, 일정표, 보고서를 그냥 보거나 인쇄만 하면 되는 사람에게 보낼 때는 PDF가 가장 편해요. 받는 사람에게 엑셀이 없어도 되고, 실수로 숫자가 바뀔 일도 없어요.</p>
<h2>엑셀을 PDF로 바꾸는 법</h2>
<ol><li>위에서 .xlsx, .xls, .csv 파일을 골라요.</li><li><b>PDF로 변환</b>을 눌러요.</li><li>PDF를 저장해요. 시트마다 새 페이지에서 시작하고 맨 위에 시트 이름이 적혀요.</li></ol>
<h2>이렇게 나와요</h2>
<ul><li>셀 값은 숫자 서식을 포함해 엑셀에서 보이는 그대로 나와요.</li><li>긴 시트는 A4 여러 장으로 이어지고, 아주 넓은 시트는 가로 방향이 돼요.</li><li>차트, 그림, 셀 색깔, 엑셀의 인쇄 설정은 들어가지 않아요. 이런 게 필요하면 엑셀에서 "PDF로 저장"을 쓰세요.</li></ul>
<h2>자주 묻는 질문</h2>
<h3>수식도 남나요?</h3><p>PDF에는 수식이 아니라 계산된 결과가 나와요.</p>
<h3>CSV 파일도 되나요?</h3><p>네. CSV는 시트 하나로 읽어요.</p>''')

page('ppt-to-pdf', 'doc', {'accept': '.pptx,.ppt'},
M(
 en=dict(title='PowerPoint to PDF – Convert PPTX to PDF Free | PicShifter', desc='Convert PowerPoint (PPTX) presentations to PDF for free. One slide per page, in your browser with no upload.', h1='PowerPoint to PDF', sub='Turn PowerPoint slides into a PDF you can share or print. Everything happens on your device.'),
 ko=dict(title='PPT PDF 변환 | PicShifter', desc='파워포인트(PPTX) 발표 자료를 무료로 PDF로 바꾸세요. 슬라이드 한 장이 한 페이지로, 브라우저에서 처리, 업로드 없음.', h1='PPT를 PDF로', sub='파워포인트 슬라이드를 공유하거나 인쇄하기 좋은 PDF로 바꿔요. 모든 작업은 내 기기 안에서 이뤄져요.'),
 ja=dict(title='PowerPointをPDFに – PPTXを無料でPDF変換 | PicShifter', desc='PowerPoint（PPTX）のプレゼンを無料でPDFに変換。1スライド1ページで、ブラウザ内で処理、アップロード不要。', h1='PowerPointをPDFに', sub='PowerPointのスライドを共有や印刷に便利なPDFに変換します。処理は端末内で行われます。'),
 zh=dict(title='PPT 转 PDF – 免费将 PowerPoint PPTX 转为 PDF | PicShifter', desc='免费将 PowerPoint（PPTX）演示文稿转换为 PDF，每张幻灯片一页，在浏览器中处理，无需上传。', h1='PPT 转 PDF', sub='把 PowerPoint 幻灯片转换成便于分享和打印的 PDF。所有操作都在你的设备上完成。'),
 es=dict(title='PowerPoint a PDF – Convierte PPTX a PDF gratis | PicShifter', desc='Convierte presentaciones de PowerPoint (PPTX) a PDF gratis. Una diapositiva por página, en tu navegador y sin subir nada.', h1='PowerPoint a PDF', sub='Convierte diapositivas de PowerPoint en un PDF para compartir o imprimir. Todo ocurre en tu dispositivo.'),
 pt=dict(title='PowerPoint para PDF – Converta PPTX em PDF grátis | PicShifter', desc='Converta apresentações do PowerPoint (PPTX) em PDF de graça. Um slide por página, no navegador e sem envio.', h1='PowerPoint para PDF', sub='Transforme slides do PowerPoint em um PDF para compartilhar ou imprimir. Tudo no seu dispositivo.'),
 fr=dict(title='PowerPoint en PDF – Convertir un PPTX en PDF gratuitement | PicShifter', desc='Convertissez gratuitement vos présentations PowerPoint (PPTX) en PDF. Une diapositive par page, dans le navigateur, sans envoi.', h1='PowerPoint en PDF', sub='Transformez vos diapositives PowerPoint en PDF à partager ou imprimer. Tout se passe sur votre appareil.'),
 de=dict(title='PowerPoint in PDF – PPTX kostenlos in PDF umwandeln | PicShifter', desc='Wandle PowerPoint-Präsentationen (PPTX) kostenlos in PDF um. Eine Folie pro Seite, im Browser ohne Upload.', h1='PowerPoint zu PDF', sub='Mach aus PowerPoint-Folien eine PDF zum Teilen oder Drucken. Alles passiert auf deinem Gerät.'),
),
en='''<h2>Why share slides as PDF</h2>
<p>Presentation files are large and depend on the fonts and version of PowerPoint on each computer. A PDF opens on any phone or laptop and is the usual way to hand out slides after a class or meeting.</p>
<h2>How to convert PowerPoint to PDF</h2>
<ol><li>Choose your .pptx files above.</li><li>Press <b>Convert to PDF</b>.</li><li>Save the PDF. Each slide becomes one landscape page.</li></ol>
<h2>What to expect</h2>
<ul><li>Text, shapes, pictures, tables and slide backgrounds are included.</li><li>Animations, transitions, videos and speaker notes are not.</li><li>Complex charts, SmartArt and special effects may look different from PowerPoint.</li></ul>
<h2>Frequently asked questions</h2>
<h3>Can I convert old .ppt files?</h3><p>Not directly. Open the file in PowerPoint, Keynote or another editor and save it as .pptx first.</p>
<h3>Can I edit the PDF afterwards?</h3><p>The pages are saved as images, so the text can’t be edited or selected.</p>''',
ko='''<h2>발표 자료를 PDF로 공유하는 이유</h2>
<p>발표 파일은 용량이 크고, 컴퓨터마다 글꼴이나 파워포인트 버전이 달라 모양이 바뀔 수 있어요. PDF는 어느 휴대폰이나 노트북에서도 열려서, 수업이나 회의가 끝난 뒤 자료를 나눠줄 때 주로 써요.</p>
<h2>PPT를 PDF로 바꾸는 법</h2>
<ol><li>위에서 .pptx 파일을 골라요.</li><li><b>PDF로 변환</b>을 눌러요.</li><li>PDF를 저장해요. 슬라이드 한 장이 가로 페이지 한 장이 돼요.</li></ol>
<h2>이렇게 나와요</h2>
<ul><li>글자, 도형, 그림, 표, 슬라이드 배경은 들어가요.</li><li>애니메이션, 화면 전환, 동영상, 발표자 메모는 들어가지 않아요.</li><li>복잡한 차트, SmartArt, 특수 효과는 파워포인트와 다르게 보일 수 있어요.</li></ul>
<h2>자주 묻는 질문</h2>
<h3>예전 .ppt 파일도 되나요?</h3><p>바로는 안 돼요. 파워포인트, 키노트 같은 프로그램에서 열어 .pptx로 저장한 뒤 사용하세요.</p>
<h3>PDF를 나중에 수정할 수 있나요?</h3><p>페이지가 그림으로 저장돼서 글자를 고치거나 선택할 수 없어요.</p>''')

page('hwp-to-pdf', 'doc', {'accept': '.hwp,.hwpx'},
M(
 en=dict(title='HWP to PDF – Convert Hangul (HWP) Files to PDF Free | PicShifter', desc='Convert Korean Hangul word processor files (HWP) to PDF for free, without installing Hancom Office. Runs in your browser, no upload.', h1='HWP to PDF', sub='Open and convert Korean Hangul (HWP) documents to PDF without Hancom Office. Everything happens on your device.'),
 ko=dict(title='한글 HWP PDF 변환 | PicShifter', desc='한글(HWP) 파일을 한컴오피스 설치 없이 무료로 PDF로 바꾸세요. 브라우저에서 처리, 업로드 없음.', h1='한글(HWP)을 PDF로', sub='한컴오피스 없이도 한글(HWP) 문서를 PDF로 바꿔요. 모든 작업은 내 기기 안에서 이뤄져요.'),
 ja=dict(title='HWPをPDFに – 韓国語ワープロ「ハングル」文書を無料でPDF変換 | PicShifter', desc='韓国のワープロソフト「ハングル」（HWP）のファイルを、Hancom Officeなしで無料でPDFに変換。ブラウザ内で処理。', h1='HWPをPDFに', sub='Hancom Officeがなくても、ハングル（HWP）文書をPDFに変換できます。処理は端末内で行われます。'),
 zh=dict(title='HWP 转 PDF – 免费将韩文 Hangul（HWP）文件转为 PDF | PicShifter', desc='无需安装 Hancom Office，免费将韩国文字处理软件 Hangul 的 HWP 文件转换为 PDF。在浏览器中处理，无需上传。', h1='HWP 转 PDF', sub='无需 Hancom Office，也能把 Hangul（HWP）文档转换为 PDF。所有操作都在你的设备上完成。'),
 es=dict(title='HWP a PDF – Convierte archivos Hangul (HWP) a PDF gratis | PicShifter', desc='Convierte archivos del procesador de textos coreano Hangul (HWP) a PDF gratis, sin instalar Hancom Office. En tu navegador, sin subir nada.', h1='HWP a PDF', sub='Convierte documentos coreanos de Hangul (HWP) a PDF sin Hancom Office. Todo ocurre en tu dispositivo.'),
 pt=dict(title='HWP para PDF – Converta arquivos Hangul (HWP) em PDF grátis | PicShifter', desc='Converta arquivos do editor de texto coreano Hangul (HWP) em PDF de graça, sem instalar o Hancom Office. No navegador, sem envio.', h1='HWP para PDF', sub='Converta documentos coreanos do Hangul (HWP) em PDF sem o Hancom Office. Tudo no seu dispositivo.'),
 fr=dict(title='HWP en PDF – Convertir des fichiers Hangul (HWP) en PDF gratuitement | PicShifter', desc='Convertissez gratuitement en PDF les fichiers du traitement de texte coréen Hangul (HWP), sans installer Hancom Office. Dans le navigateur, sans envoi.', h1='HWP en PDF', sub='Convertissez des documents coréens Hangul (HWP) en PDF sans Hancom Office. Tout se passe sur votre appareil.'),
 de=dict(title='HWP in PDF – Hangul-Dateien (HWP) kostenlos in PDF umwandeln | PicShifter', desc='Wandle Dateien des koreanischen Textprogramms Hangul (HWP) kostenlos in PDF um, ohne Hancom Office. Im Browser, ohne Upload.', h1='HWP zu PDF', sub='Wandle koreanische Hangul-Dokumente (HWP) ohne Hancom Office in PDF um. Alles passiert auf deinem Gerät.'),
),
en='''<h2>What is an HWP file?</h2>
<p>HWP is the document format of Hangul (Hancom Office), the word processor widely used by Korean government offices, schools and companies. People outside Korea, and many Mac and phone users, can’t open HWP files without installing extra software. Converting to PDF lets anyone read and print them.</p>
<h2>How to convert HWP to PDF</h2>
<ol><li>Choose your .hwp files above.</li><li>Press <b>Convert to PDF</b>.</li><li>Save the PDF. Pages keep the paper size set in the document, usually A4.</li></ol>
<h2>Frequently asked questions</h2>
<h3>Are HWPX files supported?</h3><p>Not yet. In Hangul, use “Save as” and choose the HWP format, then convert.</p>
<h3>Will it look exactly like Hangul?</h3><p>Text, tables and pictures are kept, but complex layouts and some fonts can look slightly different. Check the PDF before submitting it.</p>
<h3>Do I need to install anything?</h3><p>No. The HWP reader runs inside your browser.</p>''',
ko='''<h2>HWP 파일이 안 열릴 때</h2>
<p>HWP는 관공서, 학교, 회사에서 많이 쓰는 한글(한컴오피스) 문서 형식이에요. 그런데 한글 프로그램이 없는 컴퓨터, 맥, 휴대폰에서는 따로 프로그램을 설치하지 않으면 열리지 않아요. PDF로 바꾸면 누구나 열어보고 인쇄할 수 있어요.</p>
<h2>한글을 PDF로 바꾸는 법</h2>
<ol><li>위에서 .hwp 파일을 골라요.</li><li><b>PDF로 변환</b>을 눌러요.</li><li>PDF를 저장해요. 문서에 정해진 용지 크기(보통 A4)를 그대로 써요.</li></ol>
<h2>자주 묻는 질문</h2>
<h3>HWPX 파일도 되나요?</h3><p>아직은 안 돼요. 한글에서 "다른 이름으로 저장"으로 HWP 형식을 골라 저장한 뒤 변환하세요.</p>
<h3>한글에서 보던 것과 똑같나요?</h3><p>글자, 표, 그림은 유지되지만 복잡한 배치나 일부 글꼴은 조금 다를 수 있어요. 제출 전에 PDF를 확인하세요.</p>
<h3>프로그램을 설치해야 하나요?</h3><p>아니요. HWP 읽기 도구가 브라우저 안에서 작동해요.</p>''')

# Short names for the "related tools" list
NAMES = {
 'heic-to-jpg': ('HEIC to JPG', 'HEIC → JPG'), 'png-to-jpg': ('PNG to JPG', 'PNG → JPG'), 'jpg-to-png': ('JPG to PNG', 'JPG → PNG'),
 'webp-to-jpg': ('WebP to JPG', 'WebP → JPG'), 'jpg-to-pdf': ('JPG to PDF', 'JPG → PDF'), 'pdf-to-jpg': ('PDF to JPG', 'PDF → JPG'),
 'compress-image': ('Compress images', '사진 용량 줄이기'), 'png-to-ico': ('PNG to ICO (favicon)', 'PNG → ICO (파비콘)'),
 'word-to-pdf': ('Word to PDF', '워드 → PDF'), 'excel-to-pdf': ('Excel to PDF', '엑셀 → PDF'), 'ppt-to-pdf': ('PowerPoint to PDF', 'PPT → PDF'),
 'hwp-to-pdf': ('HWP to PDF', '한글(HWP) → PDF'), 'scan': ('Photo to scan', '사진 → 스캔본'), 'remove-background': ('Remove background', '배경 지우기'),
}
