"""列出所有可见窗口 — 把读卡程序那个窗口标题发给我"""
import ctypes, ctypes.wintypes
u=ctypes.windll.user32
W=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.wintypes.HWND,ctypes.wintypes.LPARAM)
r=[]
def e(h,l):
    if u.IsWindowVisible(h):
        b=ctypes.create_unicode_buffer(256)
        u.GetWindowTextW(h,b,256)
        t=b.value
        if t and len(t)>1:
            c=ctypes.create_unicode_buffer(256)
            u.GetClassNameW(h,c,256)
            r.append(f"{h} | {c.value} | {t}")
    return True
u.EnumWindows(W(e),0)
for x in sorted(r): print(x)
input("\n复制上面所有内容发给我")
