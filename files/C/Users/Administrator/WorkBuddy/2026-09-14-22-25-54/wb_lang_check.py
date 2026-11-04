# -*- coding: utf-8 -*-
import ctypes, os, sys
sys.stdout.reconfigure(encoding='utf-8')
k32 = ctypes.windll.kernel32

# LANGID 返回值的函数
ver = ctypes.WinDLL('version')
ver.GetFileVersionInfoSizeW.argtypes = [ctypes.c_wchar_p, ctypes.c_void_p]
ver.GetFileVersionInfoW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p]
ver.VerQueryValueW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint)]
print('GetUserDefaultUILanguage    :', hex(k32.GetUserDefaultUILanguage()))
print('GetSystemDefaultUILanguage  :', hex(k32.GetSystemDefaultUILanguage()))

# 缓冲区返回的函数
def buf_call(fnname):
    fn = getattr(k32, fnname)
    fn.restype = ctypes.c_uint
    fn.argtypes = [ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_wchar_p]
    buf = ctypes.create_unicode_buffer(64)
    n = fn(buf, 64, None)
    return buf.value if n else '?'

try:
    print('GetSystemPreferredUILanguage:', buf_call('GetSystemPreferredUILanguage'))
except Exception as e:
    print('GetSystemPreferredUILanguage n/a:', e)
try:
    print('GetUserPreferredUILanguage  :', buf_call('GetUserPreferredUILanguage'))
except Exception as e:
    print('GetUserPreferredUILanguage n/a:', e)
print()

def version_info(path):
    """列出文件版本资源中所有语言的 FileDescription"""
    size = ver.GetFileVersionInfoSizeW(path, None)
    if not size:
        return None
    data = ctypes.create_string_buffer(size)
    if not ver.GetFileVersionInfoW(path, 0, size, data):
        return None
    # 先枚举翻译表
    ptr = ctypes.c_void_p()
    ln = ctypes.c_uint()
    res = []
    if ver.VerQueryValueW(data, '\\VarFileInfo\\Translation', ctypes.byref(ptr), ctypes.byref(ln)):
        # Translation 是 DWORD 数组 (langid, charset)
        n = ln.value // 4
        arr = (ctypes.c_uint16 * (n * 2)).from_address(ptr.value)
        langs = ['%04X%04X' % (arr[i*2], arr[i*2+1]) for i in range(n)]
    else:
        langs = ['080404b0', '040904b0']
    for lang in langs:
        key = '\\StringFileInfo\\%s\\FileDescription' % lang
        if ver.VerQueryValueW(data, key, ctypes.byref(ptr), ctypes.byref(ln)) and ln.value:
            s = ctypes.wstring_at(ptr.value, ln.value)
            res.append((lang, s))
    return res

for p in [r'C:\Windows\regedit.exe',
          r'C:\Windows\zh-CN\regedit.exe.mui',
          r'C:\Windows\System32\control.exe',
          r'C:\Windows\System32\winver.exe']:
    print('===', p, '===')
    if not os.path.exists(p):
        print('文件不存在')
        continue
    r = version_info(p)
    if r:
        for lang, desc in r:
            print('  ', lang, '->', desc)
    else:
        print('   (无版本信息)')
