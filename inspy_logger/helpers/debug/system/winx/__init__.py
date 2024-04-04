from packaging import version
import platform

WIN_11_VERSION = version.parse('10.0.2200')


def is_win_11(os_version):
    return version.parse(os_version) >= WIN_11_VERSION

def is_64bit():
    return platform.architecture()[0] == '64bit'

def get_win_version():
    release, build_num, service_pack, _ = platform.win32_ver()

    if release == '10' and is_win_11(build_num):
        release = '11'

    ver = {
        'release': f'Windows {release}',
        'build': build_num,
        'service_pack': service_pack.replace('SP', ''),


    }
