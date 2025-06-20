import winreg

def subkeys(key):
    i = 0
    while True:
        try:
            yield winreg.EnumKey(key, i)
            i += 1
        except OSError:
            break

def is_guid(text):
    if not (text.startswith("{") and text.endswith("}")):
        return False

    core = text[1:-1]
    parts = core.split("-")
    if len(parts) != 5:
        return False

    expected_lengths = [8, 4, 4, 4, 12]
    for part, expected in zip(parts, expected_lengths):
        if len(part) != expected:
            return False
        if not all(c in "0123456789abcdefABCDEF" for c in part):
            return False

    return True

def traverse_registry_tree(hkey, keypath, tabs=0):
    changed = False
    try:
        key = winreg.OpenKey(hkey, keypath, 0, winreg.KEY_READ)
    except FileNotFoundError:
        return False

    for subkeyname in list(subkeys(key)):
        subkeypath = "{}\\{}".format(keypath, subkeyname)

        if traverse_registry_tree(hkey, subkeypath, tabs + 1):
            changed = True

        if is_guid(subkeyname):
            try:
                winreg.DeleteKey(hkey, subkeypath)
                print("Deleted: {}".format(subkeypath))
                print("Trial has been reset!\n")
                changed = True
            except PermissionError:
                print("Permission denied: {}".format(subkeypath))
            except FileNotFoundError:
                pass

    if tabs == 0 and not changed:
        print("No key to delete found! No changes were made to your registry.")

    return changed

keypath = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Shell Extensions\Approved"
traverse_registry_tree(winreg.HKEY_CURRENT_USER, keypath)
