import winreg
import re

def subkeys(key):
    i = 0
    while True:
        try:
            yield winreg.EnumKey(key, i)
            i += 1
        except OSError:
            break

def is_guid(text):
    return re.fullmatch(r'\{[0-9A-Fa-f\-]{36}\}', text) is not None

def traverse_registry_tree(hkey, keypath, tabs=0):
    changed = False
    try:
        key = winreg.OpenKey(hkey, keypath, 0, winreg.KEY_READ)
    except FileNotFoundError:
        return False

    for subkeyname in list(subkeys(key)):
        subkeypath = f"{keypath}\\{subkeyname}"
        
        if traverse_registry_tree(hkey, subkeypath, tabs+1):
            changed = True

        if is_guid(subkeyname):
            try:
                winreg.DeleteKey(hkey, subkeypath)
                print(f"Deleted: {subkeypath}")
                print("Trial has been reset!\n")
                changed = True
            except PermissionError:
                print(f"Permission denied: {subkeypath}")
            except FileNotFoundError:
                pass

    if tabs == 0 and not changed:
        print("No key to delete found! No changes were made to your registry.")

    return changed

keypath = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Shell Extensions\Approved"
traverse_registry_tree(winreg.HKEY_CURRENT_USER, keypath)
