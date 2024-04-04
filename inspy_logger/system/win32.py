"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/system/win32.py
 

Description:
    

"""


__all__ = [
    'get_user_name',
]


def get_user_name():
    import ctypes

    GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
    NameDisplay = 3

    size = ctypes.pointer(ctypes.c_ulong(0))
    GetUserNameEx(NameDisplay, None, size)

    name = ctypes.create_unicode_buffer(size.contents.value)
    GetUserNameEx(NameDisplay, name, size)

    return name.value


import winreg


def get_company_name():
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
        company_name, reg_type = winreg.QueryValueEx(registry_key, "RegisteredOrganization")
        winreg.CloseKey(registry_key)
        return company_name
    except WindowsError:
        return "Company name not found in the registry."
