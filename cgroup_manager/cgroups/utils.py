import psutil


def check_if_process_exists(pid):
    """Return True if process exists"""
    for process in psutil.process_iter(attrs=['pid']):
        if process.info['pid'] == pid:
            return True
    return False
