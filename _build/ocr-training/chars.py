def charset():
    hangul=[]
    for hi in range(0xB0,0xC9):
        for lo in range(0xA1,0xFF):
            try: hangul.append(bytes([hi,lo]).decode('euc-kr'))
            except Exception: pass
    jamo=[chr(c) for c in range(0x3131,0x3164)]
    ascii_=[chr(c) for c in range(33,127)]
    extra=list('·…‘’“”※→←↑↓○●□■△▲☆★~₩°%')
    return hangul, jamo, ascii_, extra
if __name__=='__main__':
    h,j,a,e=charset(); print(len(h),len(j),len(a),len(e))
