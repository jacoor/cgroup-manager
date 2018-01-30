import psutil


def check_if_process_exists(pid):
    """Return True if process exists"""
    for p in psutil.process_iter(attrs=['pid']):
        if p.info['pid'] == pid:
            return True
    return False
