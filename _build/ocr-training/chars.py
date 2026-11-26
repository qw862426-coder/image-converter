def charset():
    hangul=[]
    for hi in range(0xB0,0xC9):
        for lo in range(0xA1,0xFF):
            try: hangul.append(bytes([hi,lo]).decode('euc-kr'))
            except Exception: pass
    jamo=[chr(c) for c in range(0x3131,0x3164)]
    ascii_=[chr(c) for c in range(33,127)]
    extra=list('·…‘’“”※→←↑↓○●□■△▲☆★~₩°%')
    return hangul, jamo, ascii_, extra + latin_ext()

def latin_ext():
    """Letters with accents for German, French, Spanish, Portuguese, Italian, Turkish, Polish, Indonesian (no extra
    letters) and Vietnamese, plus common symbols. Appended at the end so the first 2,518 numbers keep their meaning."""
    import unicodedata as u
    out=[]
    def add(cs):
        for c in cs:
            if c not in out: out.append(c)
    add('ÄÖÜäöüßàâæçéèêëîïôœùûÿÀÂÆÇÉÈÊËÎÏÔŒÙÛŸáíñóúÁÍÑÓÚãõÃÕìòÌÒğışĞİŞąćęłńśźżĄĆĘŁŃŚŹŻ')
    base='aăâeêioôơuưy'; tones=['','\u0300','\u0301','\u0309','\u0303','\u0323']
    for b in base+base.upper():
        for t in tones: add(u.normalize('NFC',b+t))
    add('đĐ')
    add('¿¡«»€£¥¢§©®™±×÷–—•„‚‹›')
    have=set([chr(c) for c in range(33,127)])|set('·…‘’“”※→←↑↓○●□■△▲☆★~₩°%')
    return [c for c in out if c not in have and len(c)==1]
if __name__=='__main__':
    h,j,a,e=charset(); print(len(h),len(j),len(a),len(e))
