"""
封装C库接口与结构体  
@author Realman-Aisha  
@date 2024-04-28  
  
@details
此模块通过ctypes库封装了对C库接口的调用，简化了Python与C库之间的交互过程。它会自动加载对应环境的C库，  
封装了设置参数类型、返回值类型等复杂步骤，并创建了与C库中定义的结构体相对应的Python类。  
 
**重要提示**  
- 在使用此模块前，请确保已经根据当前操作系统和Python环境正确安装了C版本的API库，并且库文件的路径正确配置。   
- 请勿直接修改此文件，除非您了解其内部实现并清楚修改可能带来的后果。  
"""

# __docformat__ = "restructuredtext"

# Begin preamble for Python

from enum import IntEnum
import re
import platform
import os.path
import glob
import ctypes.util
import ctypes
import sys
from ctypes import *  # noqa: F401, F403
# @cond HIDE_PRIVATE_CLASSES
_int_types = (ctypes.c_int16, ctypes.c_int32)
if hasattr(ctypes, "c_int64"):
    # Some builds of ctypes apparently do not have ctypes.c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (ctypes.c_int64,)
for t in _int_types:
    if ctypes.sizeof(t) == ctypes.sizeof(ctypes.c_size_t):
        c_ptrdiff_t = t
del t
del _int_types


class UserString:
    def __init__(self, seq):
        if isinstance(seq, bytes):
            self.data = seq
        elif isinstance(seq, UserString):
            self.data = seq.data[:]
        else:
            self.data = str(seq).encode()

    def __bytes__(self):
        return self.data

    def __str__(self):
        return self.data.decode()

    def __repr__(self):
        return repr(self.data)

    def __int__(self):
        return int(self.data.decode())

    def __long__(self):
        return int(self.data.decode())

    def __float__(self):
        return float(self.data.decode())

    def __complex__(self):
        return complex(self.data.decode())

    def __hash__(self):
        return hash(self.data)

    def __le__(self, string):
        if isinstance(string, UserString):
            return self.data <= string.data
        else:
            return self.data <= string

    def __lt__(self, string):
        if isinstance(string, UserString):
            return self.data < string.data
        else:
            return self.data < string

    def __ge__(self, string):
        if isinstance(string, UserString):
            return self.data >= string.data
        else:
            return self.data >= string

    def __gt__(self, string):
        if isinstance(string, UserString):
            return self.data > string.data
        else:
            return self.data > string

    def __eq__(self, string):
        if isinstance(string, UserString):
            return self.data == string.data
        else:
            return self.data == string

    def __ne__(self, string):
        if isinstance(string, UserString):
            return self.data != string.data
        else:
            return self.data != string

    def __contains__(self, char):
        return char in self.data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.__class__(self.data[index])

    def __getslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        return self.__class__(self.data[start:end])

    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        elif isinstance(other, bytes):
            return self.__class__(self.data + other)
        else:
            return self.__class__(self.data + str(other).encode())

    def __radd__(self, other):
        if isinstance(other, bytes):
            return self.__class__(other + self.data)
        else:
            return self.__class__(str(other).encode() + self.data)

    def __mul__(self, n):
        return self.__class__(self.data * n)

    __rmul__ = __mul__

    def __mod__(self, args):
        return self.__class__(self.data % args)

    # the following methods are defined in alphabetical order:
    def capitalize(self):
        return self.__class__(self.data.capitalize())

    def center(self, width, *args):
        return self.__class__(self.data.center(width, *args))

    def count(self, sub, start=0, end=sys.maxsize):
        return self.data.count(sub, start, end)

    def decode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.decode(encoding, errors))
            else:
                return self.__class__(self.data.decode(encoding))
        else:
            return self.__class__(self.data.decode())

    def encode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.encode(encoding, errors))
            else:
                return self.__class__(self.data.encode(encoding))
        else:
            return self.__class__(self.data.encode())

    def endswith(self, suffix, start=0, end=sys.maxsize):
        return self.data.endswith(suffix, start, end)

    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))

    def find(self, sub, start=0, end=sys.maxsize):
        return self.data.find(sub, start, end)

    def index(self, sub, start=0, end=sys.maxsize):
        return self.data.index(sub, start, end)

    def isalpha(self):
        return self.data.isalpha()

    def isalnum(self):
        return self.data.isalnum()

    def isdecimal(self):
        return self.data.isdecimal()

    def isdigit(self):
        return self.data.isdigit()

    def islower(self):
        return self.data.islower()

    def isnumeric(self):
        return self.data.isnumeric()

    def isspace(self):
        return self.data.isspace()

    def istitle(self):
        return self.data.istitle()

    def isupper(self):
        return self.data.isupper()

    def join(self, seq):
        return self.data.join(seq)

    def ljust(self, width, *args):
        return self.__class__(self.data.ljust(width, *args))

    def lower(self):
        return self.__class__(self.data.lower())

    def lstrip(self, chars=None):
        return self.__class__(self.data.lstrip(chars))

    def partition(self, sep):
        return self.data.partition(sep)

    def replace(self, old, new, maxsplit=-1):
        return self.__class__(self.data.replace(old, new, maxsplit))

    def rfind(self, sub, start=0, end=sys.maxsize):
        return self.data.rfind(sub, start, end)

    def rindex(self, sub, start=0, end=sys.maxsize):
        return self.data.rindex(sub, start, end)

    def rjust(self, width, *args):
        return self.__class__(self.data.rjust(width, *args))

    def rpartition(self, sep):
        return self.data.rpartition(sep)

    def rstrip(self, chars=None):
        return self.__class__(self.data.rstrip(chars))

    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)

    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)

    def splitlines(self, keepends=0):
        return self.data.splitlines(keepends)

    def startswith(self, prefix, start=0, end=sys.maxsize):
        return self.data.startswith(prefix, start, end)

    def strip(self, chars=None):
        return self.__class__(self.data.strip(chars))

    def swapcase(self):
        return self.__class__(self.data.swapcase())

    def title(self):
        return self.__class__(self.data.title())

    def translate(self, *args):
        return self.__class__(self.data.translate(*args))

    def upper(self):
        return self.__class__(self.data.upper())

    def zfill(self, width):
        return self.__class__(self.data.zfill(width))


class MutableString(UserString):
    """mutable string objects

    Python strings are immutable objects.  This has the advantage, that
    strings may be used as dictionary keys.  If this property isn't needed
    and you insist on changing string values in place instead, you may cheat
    and use MutableString.

    But the purpose of this class is an educational one: to prevent
    people from inventing their own mutable string class derived
    from UserString and than forget thereby to remove (override) the
    __hash__ method inherited from UserString.  This would lead to
    errors that would be very hard to track down.

    A faster and better solution is to rewrite your program using lists."""

    def __init__(self, string=""):
        self.data = string

    def __hash__(self):
        raise TypeError("unhashable type (it is mutable)")

    def __setitem__(self, index, sub):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + sub + self.data[index + 1:]

    def __delitem__(self, index):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + self.data[index + 1:]

    def __setslice__(self, start, end, sub):
        start = max(start, 0)
        end = max(end, 0)
        if isinstance(sub, UserString):
            self.data = self.data[:start] + sub.data + self.data[end:]
        elif isinstance(sub, bytes):
            self.data = self.data[:start] + sub + self.data[end:]
        else:
            self.data = self.data[:start] + str(sub).encode() + self.data[end:]

    def __delslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        self.data = self.data[:start] + self.data[end:]

    def immutable(self):
        return UserString(self.data)

    def __iadd__(self, other):
        if isinstance(other, UserString):
            self.data += other.data
        elif isinstance(other, bytes):
            self.data += other
        else:
            self.data += str(other).encode()
        return self

    def __imul__(self, n):
        self.data *= n
        return self


class String(MutableString, ctypes.Union):
    _fields_ = [("raw", ctypes.POINTER(ctypes.c_char)),
                ("data", ctypes.c_char_p)]

    def __init__(self, obj=b""):
        if isinstance(obj, (bytes, UserString)):
            self.data = bytes(obj)
        else:
            self.raw = obj

    def __len__(self):
        return self.data and len(self.data) or 0

    def from_param(cls, obj):
        # Convert None or 0
        if obj is None or obj == 0:
            return cls(ctypes.POINTER(ctypes.c_char)())

        # Convert from String
        elif isinstance(obj, String):
            return obj

        # Convert from bytes
        elif isinstance(obj, bytes):
            return cls(obj)

        # Convert from str
        elif isinstance(obj, str):
            return cls(obj.encode())

        # Convert from c_char_p
        elif isinstance(obj, ctypes.c_char_p):
            return obj

        # Convert from POINTER(ctypes.c_char)
        elif isinstance(obj, ctypes.POINTER(ctypes.c_char)):
            return obj

        # Convert from raw pointer
        elif isinstance(obj, int):
            return cls(ctypes.cast(obj, ctypes.POINTER(ctypes.c_char)))

        # Convert from ctypes.c_char array
        elif isinstance(obj, ctypes.c_char * len(obj)):
            return obj

        # Convert from object
        else:
            return String.from_param(obj._as_parameter_)

    from_param = classmethod(from_param)


def ReturnString(obj, func=None, arguments=None):
    return String.from_param(obj)


# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to ctypes.c_void_p.
def UNCHECKED(type):
    if hasattr(type, "_type_") and isinstance(type._type_, str) and type._type_ != "P":
        return type
    else:
        return ctypes.c_void_p


# ctypes doesn't have direct support for variadic functions, so we have to write
# our own wrapper class
class _variadic_function(object):
    def __init__(self, func, restype, argtypes, errcheck):
        self.func = func
        self.func.restype = restype
        self.argtypes = argtypes
        if errcheck:
            self.func.errcheck = errcheck

    def _as_parameter_(self):
        # So we can pass this variadic function as a function pointer
        return self.func

    def __call__(self, *args):
        fixed_args = []
        i = 0
        for argtype in self.argtypes:
            # Typecheck what we can
            fixed_args.append(argtype.from_param(args[i]))
            i += 1
        return self.func(*fixed_args + list(args[i:]))


def ord_if_char(value):
    """
    Simple helper used for casts to simple builtin types:  if the argument is a
    string type, it will be converted to it's ordinal value.

    This function will raise an exception if the argument is string with more
    than one characters.
    """
    return ord(value) if (isinstance(value, bytes) or isinstance(value, str)) else value


# End preamble

_libs = {}
_libdirs = []

# Begin loader

"""
Load libraries - appropriately for all our supported platforms
"""
# ----------------------------------------------------------------------------
# Copyright (c) 2008 David James
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
# __all__ = ["rm_thread_mode_e",
# "rm_robot_arm_model_e",
# "rm_force_type_e",
# "rm_event_type_e",
# "rm_event_push_data_t",
# "rm_arm_current_trajectory_e",
# "rm_realtime_push_config_t",
# "rm_quat_t",
# "rm_position_t",
# "rm_frame_t",
# "rm_envelope_balls_list_t",
# "rm_pose_t",
# "rm_waypoint_t","rm_event_callback_ptr","rm_robot_handle","rm_algo_init_sys_data","rm_euler_t","rm_algo_euler2matrix"]


def _environ_path(name):
    """Split an environment variable into a path-like list elements"""
    if name in os.environ:
        return os.environ[name].split(":")
    return []


class LibraryLoader:
    """
    A base class For loading of libraries ;-)
    Subclasses load libraries for specific platforms.
    """

    # library names formatted specifically for platforms
    name_formats = ["%s"]

    class Lookup:
        """Looking up calling conventions for a platform"""

        mode = ctypes.DEFAULT_MODE

        def __init__(self, path):
            super(LibraryLoader.Lookup, self).__init__()
            self.access = dict(cdecl=ctypes.cdll.LoadLibrary(path))

        def get(self, name, calling_convention="cdecl"):
            """Return the given name according to the selected calling convention"""
            if calling_convention not in self.access:
                raise LookupError(
                    "Unknown calling convention '{}' for function '{}'".format(
                        calling_convention, name
                    )
                )
            return getattr(self.access[calling_convention], name)

        def has(self, name, calling_convention="cdecl"):
            """Return True if this given calling convention finds the given 'name'"""
            if calling_convention not in self.access:
                return False
            return hasattr(self.access[calling_convention], name)

        def __getattr__(self, name):
            return getattr(self.access["cdecl"], name)

    def __init__(self):
        self.other_dirs = []

    def __call__(self, libname):
        """Given the name of a library, load it."""
        paths = self.getpaths(libname)

        for path in paths:
            # noinspection PyBroadException
            try:
                return self.Lookup(path)
            except Exception:  # pylint: disable=broad-except
                pass

        raise ImportError("Could not load %s." % libname)

    def getpaths(self, libname):
        """Return a list of paths where the library might be found."""
        if os.path.isabs(libname):
            yield libname
        else:
            # search through a prioritized series of locations for the library

            # we first search any specific directories identified by user
            for dir_i in self.other_dirs:
                for fmt in self.name_formats:
                    # dir_i should be absolute already
                    yield os.path.join(dir_i, fmt % libname)

            # check if this code is even stored in a physical file
            try:
                this_file = __file__
            except NameError:
                this_file = None

            # then we search the directory where the generated python interface is stored
            if this_file is not None:
                for fmt in self.name_formats:
                    yield os.path.abspath(os.path.join(os.path.dirname(__file__), fmt % libname))

            # now, use the ctypes tools to try to find the library
            for fmt in self.name_formats:
                path = ctypes.util.find_library(fmt % libname)
                if path:
                    yield path

            # then we search all paths identified as platform-specific lib paths
            for path in self.getplatformpaths(libname):
                yield path

            # Finally, we'll try the users current working directory
            for fmt in self.name_formats:
                yield os.path.abspath(os.path.join(os.path.curdir, fmt % libname))

    def getplatformpaths(self, _libname):  # pylint: disable=no-self-use
        """Return all the library paths available in this platform"""
        return []


# Darwin (Mac OS X)


class DarwinLibraryLoader(LibraryLoader):
    """Library loader for MacOS"""

    name_formats = [
        "lib%s.dylib",
        "lib%s.so",
        "lib%s.bundle",
        "%s.dylib",
        "%s.so",
        "%s.bundle",
        "%s",
    ]

    class Lookup(LibraryLoader.Lookup):
        """
        Looking up library files for this platform (Darwin aka MacOS)
        """

        # Darwin requires dlopen to be called with mode RTLD_GLOBAL instead
        # of the default RTLD_LOCAL.  Without this, you end up with
        # libraries not being loadable, resulting in "Symbol not found"
        # errors
        mode = ctypes.RTLD_GLOBAL

    def getplatformpaths(self, libname):
        if os.path.pathsep in libname:
            names = [libname]
        else:
            names = [fmt % libname for fmt in self.name_formats]

        for directory in self.getdirs(libname):
            for name in names:
                yield os.path.join(directory, name)

    @staticmethod
    def getdirs(libname):
        """Implements the dylib search as specified in Apple documentation:

        http://developer.apple.com/documentation/DeveloperTools/Conceptual/
            DynamicLibraries/Articles/DynamicLibraryUsageGuidelines.html

        Before commencing the standard search, the method first checks
        the bundle's ``Frameworks`` directory if the application is running
        within a bundle (OS X .app).
        """

        dyld_fallback_library_path = _environ_path(
            "DYLD_FALLBACK_LIBRARY_PATH")
        if not dyld_fallback_library_path:
            dyld_fallback_library_path = [
                os.path.expanduser("~/lib"),
                "/usr/local/lib",
                "/usr/lib",
            ]

        dirs = []

        if "/" in libname:
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
        else:
            dirs.extend(_environ_path("LD_LIBRARY_PATH"))
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
            dirs.extend(_environ_path("LD_RUN_PATH"))

        if hasattr(sys, "frozen") and getattr(sys, "frozen") == "macosx_app":
            dirs.append(os.path.join(
                os.environ["RESOURCEPATH"], "..", "Frameworks"))

        dirs.extend(dyld_fallback_library_path)

        return dirs


# Posix


class PosixLibraryLoader(LibraryLoader):
    """Library loader for POSIX-like systems (including Linux)"""

    _ld_so_cache = None

    _include = re.compile(r"^\s*include\s+(?P<pattern>.*)")

    name_formats = ["lib%s.so", "%s.so", "%s"]

    class _Directories(dict):
        """Deal with directories"""

        def __init__(self):
            dict.__init__(self)
            self.order = 0

        def add(self, directory):
            """Add a directory to our current set of directories"""
            if len(directory) > 1:
                directory = directory.rstrip(os.path.sep)
            # only adds and updates order if exists and not already in set
            if not os.path.exists(directory):
                return
            order = self.setdefault(directory, self.order)
            if order == self.order:
                self.order += 1

        def extend(self, directories):
            """Add a list of directories to our set"""
            for a_dir in directories:
                self.add(a_dir)

        def ordered(self):
            """Sort the list of directories"""
            return (i[0] for i in sorted(self.items(), key=lambda d: d[1]))

    def _get_ld_so_conf_dirs(self, conf, dirs):
        """
        Recursive function to help parse all ld.so.conf files, including proper
        handling of the `include` directive.
        """

        try:
            with open(conf) as fileobj:
                for dirname in fileobj:
                    dirname = dirname.strip()
                    if not dirname:
                        continue

                    match = self._include.match(dirname)
                    if not match:
                        dirs.add(dirname)
                    else:
                        for dir2 in glob.glob(match.group("pattern")):
                            self._get_ld_so_conf_dirs(dir2, dirs)
        except IOError:
            pass

    def _create_ld_so_cache(self):
        # Recreate search path followed by ld.so.  This is going to be
        # slow to build, and incorrect (ld.so uses ld.so.cache, which may
        # not be up-to-date).  Used only as fallback for distros without
        # /sbin/ldconfig.
        #
        # We assume the DT_RPATH and DT_RUNPATH binary sections are omitted.

        directories = self._Directories()
        for name in (
                "LD_LIBRARY_PATH",
                "SHLIB_PATH",  # HP-UX
                "LIBPATH",  # OS/2, AIX
                "LIBRARY_PATH",  # BE/OS
        ):
            if name in os.environ:
                directories.extend(os.environ[name].split(os.pathsep))

        self._get_ld_so_conf_dirs("/etc/ld.so.conf", directories)

        bitage = platform.architecture()[0]

        unix_lib_dirs_list = []
        if bitage.startswith("64"):
            # prefer 64 bit if that is our arch
            unix_lib_dirs_list += ["/lib64", "/usr/lib64"]

        # must include standard libs, since those paths are also used by 64 bit
        # installs
        unix_lib_dirs_list += ["/lib", "/usr/lib"]
        if sys.platform.startswith("linux"):
            # Try and support multiarch work in Ubuntu
            # https://wiki.ubuntu.com/MultiarchSpec
            if bitage.startswith("32"):
                # Assume Intel/AMD x86 compat
                unix_lib_dirs_list += ["/lib/i386-linux-gnu",
                                       "/usr/lib/i386-linux-gnu"]
            elif bitage.startswith("64"):
                # Assume Intel/AMD x86 compatible
                unix_lib_dirs_list += [
                    "/lib/x86_64-linux-gnu",
                    "/usr/lib/x86_64-linux-gnu",
                ]
            else:
                # guess...
                unix_lib_dirs_list += glob.glob("/lib/*linux-gnu")
        directories.extend(unix_lib_dirs_list)

        cache = {}
        lib_re = re.compile(r"lib(.*)\.s[ol]")
        # ext_re = re.compile(r"\.s[ol]$")
        for our_dir in directories.ordered():
            try:
                for path in glob.glob("%s/*.s[ol]*" % our_dir):
                    file = os.path.basename(path)

                    # Index by filename
                    cache_i = cache.setdefault(file, set())
                    cache_i.add(path)

                    # Index by library name
                    match = lib_re.match(file)
                    if match:
                        library = match.group(1)
                        cache_i = cache.setdefault(library, set())
                        cache_i.add(path)
            except OSError:
                pass

        self._ld_so_cache = cache

    def getplatformpaths(self, libname):
        if self._ld_so_cache is None:
            self._create_ld_so_cache()

        result = self._ld_so_cache.get(libname, set())
        for i in result:
            # we iterate through all found paths for library, since we may have
            # actually found multiple architectures or other library types that
            # may not load
            yield i


# Windows


class WindowsLibraryLoader(LibraryLoader):
    """Library loader for Microsoft Windows"""

    name_formats = ["%s.dll", "lib%s.dll", "%slib.dll", "%s"]

    class Lookup(LibraryLoader.Lookup):
        """Lookup class for Windows libraries..."""

        def __init__(self, path):
            super(WindowsLibraryLoader.Lookup, self).__init__(path)
            self.access["stdcall"] = ctypes.windll.LoadLibrary(path)


# Platform switching

# If your value of sys.platform does not appear in this dict, please contact
# the Ctypesgen maintainers.

loaderclass = {
    "darwin": DarwinLibraryLoader,
    "cygwin": WindowsLibraryLoader,
    "win32": WindowsLibraryLoader,
    "msys": WindowsLibraryLoader,
}

load_library = loaderclass.get(sys.platform, PosixLibraryLoader)()


def add_library_search_dirs(other_dirs):
    """
    Add libraries to search paths.
    If library paths are relative, convert them to absolute with respect to this
    file's directory
    """
    for path in other_dirs:
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        load_library.other_dirs.append(path)


del loaderclass

# End loader

module_path = os.path.abspath(__file__)
package_dir = os.path.dirname(module_path)
dll_path = os.path.join(package_dir, 'libs')

# End loader
if platform.machine() == "x86_64":
    dll_path = os.path.join(dll_path, 'linux_x86')
    add_library_search_dirs([dll_path])
elif sys.platform == "win32":
    if sys.maxsize > 2**32:
        dll_path = os.path.join(dll_path, 'win_64')
        add_library_search_dirs([dll_path])
    else:
        dll_path = os.path.join(dll_path, 'win_32')
        add_library_search_dirs([dll_path])
        print(dll_path)
else:
    dll_path = os.path.join(dll_path, 'linux_arm')
    add_library_search_dirs([dll_path])

# Begin libraries
if sys.platform == "linux":
    libname = "libapi_c.so"
elif sys.platform == "win32":
    libname = "api_c.dll"
_libs[libname] = load_library(libname)

__uint8_t = c_ubyte
__uint16_t = c_ushort
uint8_t = __uint8_t
uint16_t = __uint16_t
# @endcond


class rm_thread_mode_e(IntEnum):
    """线程模式枚举
    """
    # 单线程模式
    RM_SINGLE_MODE_E = 0
    # 双线程模式
    RM_DUAL_MODE_E = RM_SINGLE_MODE_E + 1
    # 多线程模式
    RM_TRIPLE_MODE_E = RM_DUAL_MODE_E + 1


class rm_robot_arm_model_e(IntEnum):
    """  
    机械臂型号枚举  

    此枚举类定义了不同型号的机械臂型号。  

    Attributes:  
        RM_MODEL_RM_65_E (int): RM_65型号  
        RM_MODEL_RM_75_E (int): RM_75型号  
        RM_MODEL_RM_63_I_E (int): RML_63I型号（已弃用）  
        RM_MODEL_RM_63_II_E (int): RML_63II型号  
        RM_MODEL_RM_63_III_E (int): RML_63III型号（已弃用）  
        RM_MODEL_ECO_65_E (int): ECO_65型号  
        RM_MODEL_ECO_62_E (int): ECO_62型号  
        RM_MODEL_GEN_72_E (int): GEN_72型号  

    """

    # RM_65型号
    RM_MODEL_RM_65_E = 0

    # RM_75型号
    RM_MODEL_RM_75_E = RM_MODEL_RM_65_E + 1

    # RML_63I型号（已弃用）
    RM_MODEL_RM_63_I_E = RM_MODEL_RM_75_E + 1

    # RML_63II型号
    RM_MODEL_RM_63_II_E = RM_MODEL_RM_63_I_E + 1

    # RML_63III型号（已弃用）
    RM_MODEL_RM_63_III_E = RM_MODEL_RM_63_II_E + 1

    # ECO_65型号
    RM_MODEL_ECO_65_E = RM_MODEL_RM_63_III_E + 1

    # ECO_62型号
    RM_MODEL_ECO_62_E = RM_MODEL_ECO_65_E + 1

    # GEN_72型号
    RM_MODEL_GEN_72_E = RM_MODEL_ECO_62_E + 1


class rm_force_type_e(IntEnum):
    """机械臂末端版本枚举 
    """
    # 标准版本
    RM_MODEL_RM_B_E = 0
    # 一维力版本
    RM_MODEL_RM_ZF_E = (RM_MODEL_RM_B_E + 1)
    # 六维力版本
    RM_MODEL_RM_SF_E = (RM_MODEL_RM_ZF_E + 1)


class rm_event_type_e(IntEnum):
    """机械臂事件类型枚举 
    """
    # 无事件
    RM_NONE_EVENT_E = 0
    # 当前轨迹到位
    RM_CURRENT_TRAJECTORY_STATE_E = RM_NONE_EVENT_E + 1
    # 在线编程运行结束
    RM_PROGRAM_RUN_FINISH_E = RM_CURRENT_TRAJECTORY_STATE_E + 1


class rm_event_push_data_t(Structure):
    """表示机械臂到位等事件信息的结构体  
    @details 此结构体用于接收关于机械臂的各类事件信息，如规划轨迹到位、在线编程到位等。  
    通过rm_get_arm_event_call_back接口注册回调函数处理本结构体数据。  
    **Attributes**: 
        - handle_id (int) 机械臂连接id，用于标识特定的机械臂连接。
        - event_type (rm_event_type_e) 事件类型枚举，表示具体的事件类型。  
            - 0：无事件  
            - 1：当前规划轨迹到位  
            - 2：当前在线编程到位  
        - trajectory_state (bool) 表示已到位规划轨迹的状态，true-成功，false-失败
        - device (int) 表示当前已到位规划的设备标识符，用于进一步区分不同类型的设备。 
            - 0：关节
            - 1：夹爪
            - 2：灵巧手
            - 3：升降机构
            - 4：扩展关节
            - 其他：保留
        - trajectory_connect (int) 表示当前已到位规划的轨迹是否连接下一条:
            - 0：代表全部到位
            - 1：代表连接下一条轨迹 
        - program_id (int) 当前到位的在线编程。 
    """
    _fields_ = [
        ('handle_id', c_int),
        ('event_type', c_int),
        ('trajectory_state', c_bool),
        ('device', c_int),
        ('trajectory_connect', c_int),
        ('program_id', c_int),
    ]


class rm_arm_current_trajectory_e(IntEnum):
    """机械臂当前规划类型枚举 
    """
    # 无规划
    RM_NO_PLANNING_E = 0
    # 关节空间规划
    RM_JOINT_SPACE_PLANNING_E = 1
    # 笛卡尔空间直线规划
    RM_CARTESIAN_LINEAR_PLANNING_E = 2
    # 笛卡尔空间圆弧规划
    RM_CARTESIAN_ARC_PLANNING_E = 3
    # 示教轨迹复现规划
    RM_TRAJECTORY_REPLAY_PLANNING_E = 4

class rm_udp_custom_config_t(Structure):
    """  
    自定义UDP上报项  

    **Attributes**:  
        - joint_speed (int): 关节速度。1：上报；0：关闭上报；-1：不设置，保持之前的状态
        - lift_state (int): 升降关节信息。1：上报；0：关闭上报；-1：不设置，保持之前的状态
        - expand_state (int): 扩展关节信息（升降关节和扩展关节为二选一，优先显示升降关节）1：上报；0：关闭上报；-1：不设置，保持之前的状态
    """
    _fields_ = [
        ('joint_speed', c_int),
        ('lift_state', c_int),
        ('expand_state', c_int),
    ]

    def __init__(self, joint_speed:int = None,lift_state:int = None,expand_state:int = None) -> None:
        if all(param is None for param in [joint_speed, lift_state, expand_state]):
            return
        else:
            self.joint_speed = joint_speed
            self.lift_state = lift_state
            self.expand_state = expand_state
    
    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result

class rm_realtime_push_config_t(Structure):
    """  
    UDP机械臂状态主动上报接口配置  

    **Attributes**:  
        - cycle (int): 广播周期，5ms的倍数
        - enable (bool): 使能，是否主动上报
        - port (int): 广播的端口号
        - force_coordinate (int): 系统外受力数据的坐标系（力传感器版本支持）
            - 0：传感器坐标系 
            - 1：当前工作坐标系 
            - 2：当前工具坐标系
        - ip (bytes): 自定义的上报目标IP地址
        - custom_config (rm_udp_custom_config_t): 自定义上报项
    """
    _fields_ = [
        ('cycle', c_int),
        ('enable', c_bool),
        ('port', c_int),
        ('force_coordinate', c_int),
        ('ip', c_char * int(28)),
        ('custom_config', rm_udp_custom_config_t),
    ]

    def __init__(self, cycle: int = None, enable: bool = None, port: int = None, force_coordinate: int = None, ip: str = None, custom_config:rm_udp_custom_config_t = None) -> None:
        """
        UDP机械臂状态主动上报接口配置构造函数

        Args:
            cycle (int, optional): 广播周期，5ms的倍数. Defaults to None.
            enable (bool, optional): 使能，是否主动上报. Defaults to None.
            port (int, optional): 广播的端口号. Defaults to None.
            force_coordinate (int, optional): 系统外受力数据的坐标系（力传感器版本支持）. Defaults to None.
                        - 0：传感器坐标系 
                        - 1：当前工作坐标系 
                        - 2：当前工具坐标系
            ip (str, optional): 自定义的上报目标IP地址. Defaults to None.
        """
        if all(param is None for param in [cycle, enable, port, force_coordinate, ip, custom_config]):
            return
        else:
            self.cycle = cycle
            self.enable = enable
            self.port = port
            self.force_coordinate = force_coordinate
            self.ip = ip.encode('utf-8')
            if custom_config==None:
               custom_config=rm_udp_custom_config_t(-1,-1,-1)
            self.custom_config = custom_config

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result


class rm_quat_t(Structure):
    """  
    表示四元数的结构体  

    **Attributes**:  
        - w (float): 四元数的实部（scalar part），通常用于表示旋转的角度和方向。  
        - x (float): 四元数的虚部中的第一个分量（vector part）。  
        - y (float): 四元数的虚部中的第二个分量。  
        - z (float): 四元数的虚部中的第三个分量。    
    """
    _fields_ = [
        ('w', c_float),
        ('x', c_float),
        ('y', c_float),
        ('z', c_float),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result


class rm_position_t(Structure):
    """  
    位置结构体  

    **Attributes**:  
        - x (float): X轴坐标值，单位：m。  
        - y (float): Y轴坐标值，单位：m。  
        - z (float): Z轴坐标值，单位：m。  

    这个结构体通常用于表示机器人、物体或其他任何可以在三维空间中定位的点的位置。  
    """
    _fields_ = [
        ('x', c_float),
        ('y', c_float),
        ('z', c_float),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result


class rm_euler_t(Structure):
    """  
    表示欧拉角（Euler angles）的结构体  

    **Attributes**:  
        - rx (float): 绕X轴旋转的角度，单位：rad。  
        - ry (float): 绕Y轴旋转的角度，单位：rad。  
        - rz (float): 绕Z轴旋转的角度，单位：rad。   
    """
    _fields_ = [
        ('rx', c_float),
        ('ry', c_float),
        ('rz', c_float),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result


class rm_pose_t(Structure):
    """
    表示机械臂位置姿态的结构体  

    **Attributes**:  
        - position (rm_position_t): 位置，单位：m
        - quaternion (rm_quat_t): 四元数
        - euler (rm_euler_t): 欧拉角，单位：rad
    """
    _fields_ = [
        ('position', rm_position_t),
        ('quaternion', rm_quat_t),
        ('euler', rm_euler_t),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result


class rm_frame_name_t(Structure):
    """
    坐标系名称结构体  

    **Attributes**:  
        - name (str): 不超过10个字符
    """
    _fields_ = [
        ('name', c_char * int(12)),
    ]


class rm_frame_t(Structure):
    """  
    表示一个坐标系的结构体  

    **Attributes**:  
        - frame_name (bytes): 坐标系名称，不超过10个字符（包括结尾的null字节）。  
        - pose (rm_pose_t): 坐标系位姿，包含位置和姿态信息。  
        - payload (float): 坐标系末端负载重量，单位：kg。  
        - x (float), y (float), z (float): 坐标系末端负载质心位置坐标。  
    """
    _fields_ = [
        ('frame_name', c_char * 12),  # 11个字符 + 1个null字节
        ('pose', rm_pose_t),
        ('payload', c_float),
        ('x', c_float),
        ('y', c_float),
        ('z', c_float),
    ]

    def __init__(self, frame_name: str = None, pose: tuple[float, float, float, float, float, float] = None, payload: float = None, x: float = None, y: float = None, z: float = None):
        """

        Args:
            frame_name (str, optional): 坐标系名称，不超过10个字符。默认为 None。  
            pose (tuple[float, float, float, float, float, float], optional): 表示坐标系位姿的元组，包含三个位置坐标（x, y, z）和三个欧拉角（rx, ry, rz）。  
            payload (float, optional): 坐标系末端负载重量，单位：kg。默认为 None。  
            x (float, optional): 坐标系末端负载质心位置的 x 坐标，单位：m。默认为 None。  
            y (float, optional): 坐标系末端负载质心位置的 y 坐标，单位：m。默认为 None。  
            z (float, optional): 坐标系末端负载质心位置的 z 坐标，单位：m。默认为 None。  

        Raises:
            ValueError: 如果frame_name的长度超过10个字符
            ValueError: 如果 pose 不是包含6个浮点数的元组，表示(x, y, z, rx, ry, rz)
        """
        if frame_name is not None:
            if len(frame_name) > 10:
                raise ValueError("frame_name must not exceed 10 characters.")
            self.frame_name = frame_name.encode(
                'utf-8')[:11] + b'\0'  # 截断并添加null字节

        if pose is not None:
            if len(pose) != 6:
                raise ValueError(
                    "pose must be a tuple of 6 floats representing (x, y, z, roll, pitch, yaw).")
            pose_value = rm_pose_t()
            pose_value.position = rm_position_t(pose[0], pose[1], pose[2])
            pose_value.euler = rm_euler_t(pose[3], pose[4], pose[5])
            self.pose = pose_value

        if payload is not None:
            self.payload = payload
            self.x = x
            self.y = y
            self.z = z

    def to_dictionary(self) -> dict[str, any]:
        """将rm_frame_t对象转换为字典表现形式

        Returns:
            包含坐标系信息的字典，包括以下键
            - 'name' (str): 坐标系名称  
            - 'pose' (List[float]): 包含位置和欧拉角的列表，按顺序为 [x, y, z, rx, ry, rz]  
            - 'payload' (float): 坐标系末端负载重量，单位：kg
            - 'x' (float): 坐标系末端负载位置，单位：m
            - 'y' (float): 坐标系末端负载位置，单位：m
            - 'z' (float): 坐标系末端负载位置，单位：m
        """
        name = self.frame_name.decode("utf-8")
        position = self.pose.position
        euler = self.pose.euler

        output_dict = {
            "name": name,
            "pose": [round(item, 6) for item in [position.x, position.y, position.z, euler.rx, euler.ry, euler.rz]],
            "payload": float(format(self.payload, ".3f")),
            "x": float(format(self.x, ".3f")),
            "y": float(format(self.y, ".3f")),
            "z": float(format(self.z, ".3f"))
        }
        return output_dict


class rm_ctrl_version_t(Structure):
    """  
    表示控制器ctrl 层软件信息的结构体  

    **Args:**  
        - 无（此结构体通常为调用接口获取数据填充）。  

    **Attributes:**  
        - build_time (bytes): 编译时间。
        - version (bytes): 版本号。
    """
    _fields_ = [
        ('build_time', c_char * int(20)),
        ('version', c_char * int(10)),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result


class rm_dynamic_version_t(Structure):
    """  
    表示动力学版本信息的结构体  

    **Args:**  
        - 无（此结构体通常为调用接口获取数据填充）。  

    **Attributes:**  
        - model_version (bytes): 动力学模型版本号。
    """
    _fields_ = [
        ('model_version', c_char * int(5)),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result


class rm_planinfo_t(Structure):
    """  
    表示控制器plan 层软件信息的结构体  

    **Args:**  
        - 无（此结构体通常为调用接口获取数据填充）。  

    **Attributes:**  
        - build_time (bytes): 编译时间。
        - version (bytes): 版本号。
    """
    _fields_ = [
        ('build_time', c_char * int(20)),
        ('version', c_char * int(10)),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result


class rm_algorithm_version_t(Structure):
    """  
    表示算法库信息的结构体  

    **Args:**  
        - 无（此结构体通常为调用接口获取数据填充）。  

    **Attributes:**  
        - version (bytes): 版本号。
    """
    _fields_ = [
        ('version', c_char * int(20)),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result


class rm_arm_software_version_t(Structure):
    """  
    表示机械臂软件版本信息的结构体  

    **Args**:  
        无（无直接构造参数，此结构体通常由机械臂提供数据并填充，通过访问对应的属性读取信息）。  


    Attributes:  
        product_version (bytes): 机械臂型号
        algorithm_info (rm_algorithm_version_t): 算法库信息
        ctrl_info (rm_ctrl_version_t): ctrl 层软件信息
        dynamic_info (rm_dynamic_version_t): 动力学版本
        plan_info (rm_planinfo_t): plan 层软件信息
    """
    _fields_ = [
        ('product_version', c_char * int(10)),
        ('algorithm_info', rm_algorithm_version_t),
        ('ctrl_info', rm_ctrl_version_t),
        ('dynamic_info', rm_dynamic_version_t),
        ('plan_info', rm_planinfo_t),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result


class rm_current_arm_state_t(Structure):
    """  
    表示机械臂当前状态的结构体  

    **Args**:  
        无（无直接构造参数，此结构体通常由机械臂提供数据并填充，通过访问对应的属性读取信息）。  


    **Attributes:**  
        pose (rm_pose_t): 机械臂的当前位姿信息。  
        joint (float[7]): 机械臂当前关节角度，单位：°。  
        arm_err (uint8_t): 机械臂错误代码。
        sys_err (uint8_t): 控制器错误代码。

    注意：  
    - 这些字段通常由外部系统或硬件提供，并通过适当的接口填充。  
    - 在处理错误代码时，请参考相关的错误代码文档或枚举。  
    """
    _fields_ = [
        ('pose', rm_pose_t),
        ('joint', c_float * int(7)),
        ('arm_err', uint8_t),
        ('sys_err', uint8_t),
    ]

    def to_dictionary(self, arm_dof):
        position = self.pose.position
        euler = self.pose.euler

        output_dict = {
            "joint": list(self.joint[:arm_dof]),
            "pose": [round(item, 6) for item in [position.x, position.y, position.z, euler.rx, euler.ry, euler.rz]],
            "arm_err": float(format(self.arm_err, ".3f")),
            "sys_err": float(format(self.sys_err, ".3f")),
        }
        return output_dict


class rm_joint_status_t(Structure):
    """  
    表示机械臂关节状态的结构体  

    **Args**:  
        无（无直接构造参数，此结构体通常由机械臂提供数据并填充，通过访问对应的属性读取信息）。  


    **Attributes**:  
        joint_current (float[7]): 关节电流，单位mA，精度：0.001mA
        joint_en_flag (bool[7]): 当前关节使能状态 ，1为上使能，0为掉使能
        joint_err_code (uint16_t[7]): 当前关节错误码
        joint_position (float[7]): 关节角度，单位°，精度：0.001°
        joint_temperature (float[7]): 当前关节温度，精度0.001℃
        joint_voltage (float[7]): 当前关节电压，精度0.001V
    """
    _fields_ = [
        ('joint_current', c_float * int(7)),
        ('joint_en_flag', c_bool * int(7)),
        ('joint_err_code', uint16_t * int(7)),
        ('joint_position', c_float * int(7)),
        ('joint_temperature', c_float * int(7)),
        ('joint_voltage', c_float * int(7)),
        ('joint_speed', c_float * int(7)),
    ]


class rm_pos_teach_type_e(IntEnum):
    """位置示教方向枚举 
    """
    # 位置示教，x轴方向
    RM_X_DIR_E = 0
    # 位置示教，y轴方向
    RM_Y_DIR_E = RM_X_DIR_E + 1
    # 位置示教，z轴方向
    RM_Z_DIR_E = RM_Y_DIR_E + 1


class rm_ort_teach_type_e(IntEnum):
    """姿态示教方向枚举 
    """
    # 姿态示教，绕x轴旋转
    RM_RX_ROTATE_E = 0
    # 姿态示教，绕y轴旋转
    RM_RY_ROTATE_E = (RM_RX_ROTATE_E + 1)
    # 姿态示教，绕z轴旋转
    RM_RZ_ROTATE_E = (RM_RY_ROTATE_E + 1)


class rm_wifi_net_t(Structure):
    """  
    无线网络信息结构体  

    **Args**:  
        无（无直接构造参数，此结构体通常由机械臂提供数据并填充，通过访问对应的属性读取信息）。  

    **Attributes**:  
        - channel (int): 如果是 AP 模式，则存在此字段，标识 wifi 热点的物理信道号  
        - ip (str): IP 地址  
        - mac (str): MAC 地址  
        - mask (str): 子网掩码  
        - mode (str): 'ap' 代表热点模式，'sta' 代表联网模式，'off' 代表未开启无线模式  
        - password (str): 密码  
        - ssid (str): 网络名称 (SSID)  
    """
    _fields_ = [
        ('channel', c_int),
        ('ip', c_char * int(16)),
        ('mac', c_char * int(18)),
        ('mask', c_char * int(16)),
        ('mode', c_char * int(5)),
        ('password', c_char * int(16)),
        ('ssid', c_char * int(32)),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        if self.mode.decode('utf-8') == "off":
            del result['password']
            del result['ssid']
            del result['channel']

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result


class rm_arm_all_state_t(Structure):
    """    
    机械臂所有状态参数  

    **Args**:  
        无（无直接构造参数，此结构体通常由机械臂提供数据并填充，通过访问对应的属性读取信息）。  

    **Attributes**:  
        - joint_current (float[7]): 关节电流，单位mA
        - joint_en_flag (int[7]): 关节使能状态
        - joint_temperature (float[7]): 关节温度,单位℃
        - joint_voltage (float[7]): 关节电压，单位V
        - joint_err_code (int[7]): 关节错误码
        - sys_err (int): 机械臂错误代码
    """
    _fields_ = [
        ('joint_current', c_float * int(7)),
        ('joint_en_flag', c_int * int(7)),
        ('joint_temperature', c_float * int(7)),
        ('joint_voltage', c_float * int(7)),
        ('joint_err_code', c_int * int(7)),
        ('sys_err', c_int),
    ]

    def to_dictionary(self):
        output_dict = {
            'joint_current': list(self.joint_current),
            'joint_en_flag': list(self.joint_en_flag),
            'joint_temperature': list(self.joint_temperature),
            'joint_voltage': list(self.joint_voltage),
            'joint_err_code': list(self.joint_err_code),
            'sys_err': self.sys_err,
        }
        return output_dict


class rm_gripper_state_t(Structure):
    """夹爪状态结构体

    **Args**:  
        无（无直接构造参数，此结构体通常由机械臂提供数据并填充，通过访问对应的属性读取信息）。  

    **Attributes**:  
        - enable_state (int): 夹爪使能标志，0 表示未使能，1 表示使能
        - status (int): 夹爪在线状态，0 表示离线， 1表示在线
        - error (int): 夹爪错误信息，低8位表示夹爪内部的错误信息bit5-7 保留bit4 内部通bit3 驱动器bit2 过流 bit1 过温bit0 堵转
        - mode (int): 当前工作状态：1 夹爪张开到最大且空闲，2 夹爪闭合到最小且空闲，3 夹爪停止且空闲，4 夹爪正在闭合，5 夹爪正在张开，6 夹爪闭合过程中遇到力控停止
        - current_force (int): 夹爪当前的压力，单位g
        - temperature (int): 当前温度，单位℃
        - actpos (int): 夹爪开口度

    """
    _fields_ = [
        ('enable_state', c_int),
        ('status', c_int),
        ('error', c_int),
        ('mode', c_int),
        ('current_force', c_int),
        ('temperature', c_int),
        ('actpos', c_int),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result


class rm_force_data_t(Structure):
    """    
    六维力传感器数据结构体  

    **Args**:  
        无（无直接构造参数，此结构体通常由机械臂提供数据并填充，通过访问对应的属性读取信息）。  

    **Attributes**:  
        - force_data (float[6]): 当前力传感器原始数据，力的单位为N；力矩单位为Nm。
        - zero_force_data (float[6]): 当前力传感器系统外受力数据，力的单位为N；力矩单位为Nm。
        - work_zero_force_data (float[6]): 当前工作坐标系下系统外受力数据，力的单位为N；力矩单位为Nm。
        - tool_zero_force_data (float[6]): 当前工具坐标系下系统外受力数据，力的单位为N；力矩单位为Nm。
    """
    _fields_ = [
        ('force_data', c_float * int(6)),
        ('zero_force_data', c_float * int(6)),
        ('work_zero_force_data', c_float * int(6)),
        ('tool_zero_force_data', c_float * int(6)),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result


class rm_fz_data_t(Structure):
    """    
    一维力传感器数据结构体  

    **Args**:  
        无（无直接构造参数，此结构体通常由机械臂提供数据并填充，通过访问对应的属性读取信息）。  

    **Attributes**:  
        - Fz (float): 当前力传感器原始数据，力的单位为N；力矩单位为Nm。  
        - zero_Fz (float): 传感器坐标系下系统外受力数据，力的单位为N；力矩单位为Nm。
        - work_zero_Fz (float): 当前工作坐标系下系统外受力数据，力的单位为N；力矩单位为Nm。
        - tool_zero_Fz (float): 当前工具坐标系下系统外受力数据，力的单位为N；力矩单位为Nm。

    """
    _fields_ = [
        ('Fz', c_float),
        ('zero_Fz', c_float),
        ('work_zero_Fz', c_float),
        ('tool_zero_Fz', c_float),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result


class rm_peripheral_read_write_params_t(Structure):
    """  
    读写外设数据参数结构体  

    **Args**:  
        - port (int, optional): 通讯端口，0-控制器RS485端口，1-末端接口板RS485接口，3-控制器ModbusTCP设备，默认为 None  
        - address (int, optional): 数据起始地址，默认为 None  
        - device (int, optional): 外设设备地址，默认为 None  
        - num (int, optional): 数据数量，默认为 None  

    **Attributes**:  
        - port (int): 通讯端口，0-控制器RS485端口，1-末端接口板RS485接口，3-控制器ModbusTCP设备  
        - address (int): 数据起始地址  
        - device (int): 外设设备地址  
        - num (int): 数据数量  
    """
    _fields_ = [
        ('port', c_int),
        ('address', c_int),
        ('device', c_int),
        ('num', c_int),
    ]

    def __init__(self, port=None, address=None, device=None, num=None):
        if all(param is None for param in [port, address, device, num]):
            return
        else:
            self.port = port
            self.address = address
            self.device = device
            if num is not None:
                self.num = num


class rm_expand_state_t(Structure):
    """  
    表示扩展关节状态的结构体。  

    **Args**:  
        无（无直接构造参数，此结构体通常由机械臂提供数据并填充，通过访问对应的属性读取信息）。  

    **Attributes**:  
        - pos (int): 扩展关节角度，单位度，精度 0.001°(若为升降机构高度，则s单位：mm，精度：1mm，范围：0 ~2300)
        - current (int): 驱动电流，单位：mA，精度：1mA
        - err_flag (int): 驱动错误代码，错误代码类型参考关节错误代码
        - mode (int): 当前工作状态
            - 0：空闲 
            - 1：正方向速度运动 
            - 2：正方向位置运动 
            - 3：负方向速度运动 
            - 4：负方向位置运动
    """
    _fields_ = [
        ('pos', c_int),
        ('current', c_int),
        ('err_flag', c_int),
        ('mode', c_int),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result

# rm_expand_state_t = struct_anon_30


class rm_send_project_t(Structure):
    """  
    用于发送编程文件信息的结构体。  

    **Attributes:**  
        - project_path (c_char * 300): 下发文件路径文件路径及名称
        - project_path_len (c_int): 路径及名称长度
        - plan_speed (c_int): 规划速度比例系数
        - only_save (c_int): 0-运行文件，1-仅保存文件，不运行
        - save_id (c_int): 保存到控制器中的编号
        - step_flag (c_int): 设置单步运行方式模式，1-设置单步模式 0-设置正常运动模式
        - auto_start (c_int): 设置默认在线编程文件，1-设置默认  0-设置非默认
    """
    _fields_ = [
        ('project_path', c_char * int(300)),
        ('project_path_len', c_int),
        ('plan_speed', c_int),
        ('only_save', c_int),
        ('save_id', c_int),
        ('step_flag', c_int),
        ('auto_start', c_int),
    ]

    def __init__(self, project_path: str = None, plan_speed: int = None, only_save: int = None, save_id: int = None, step_flag: int = None, auto_start: int = None):
        """
        在线编程文件下发结构体

        @param project_path (str, optional): 下发文件路径文件路径及名称，默认为None
        @param plan_speed (int, optional): 规划速度比例系数，默认为None
        @param only_save (int, optional): 0-运行文件，1-仅保存文件，不运行，默认为None
        @param save_id (int, optional): 保存到控制器中的编号，默认为None
        @param step_flag (int, optional): 设置单步运行方式模式，1-设置单步模式 0-设置正常运动模式，默认为None
        @param auto_start (int, optional): 设置默认在线编程文件，1-设置默认  0-设置非默认，默认为None
        """
        if all(param is None for param in [project_path, plan_speed, only_save, save_id, step_flag, auto_start]):
            return
        else:
            if project_path is not None:
                # 确保字符串不超过最大长度，并添加null终止符
                self.project_path = project_path.encode('utf-8')

                # 路径及名称长度
                self.project_path_len = len(self.project_path) + 1  # 包括null终止符

            # 规划速度比例系数
            self.plan_speed = plan_speed if plan_speed is not None else 20
            # 0-运行文件，1-仅保存文件，不运行
            self.only_save = only_save if only_save is not None else 0
            # 保存到控制器中的编号
            self.save_id = save_id if save_id is not None else 0
            # 设置单步运行方式模式，1-设置单步模式 0-设置正常运动模式
            self.step_flag = step_flag if step_flag is not None else 0
            # 设置默认在线编程文件，1-设置默认  0-设置非默认
            self.auto_start = auto_start if auto_start is not None else 0


class rm_trajectory_data_t(Structure):
    """    
    在线编程存储信息  

    **Args**:  
        - 无（无直接构造参数，此结构体通常由机械臂提供数据并填充，通过访问对应的属性读取信息）。  

    **Attributes**:  
        - id (int): 在线编程文件id
        - size(int): 文件大小
        - speed(int): 默认运行速度
        - trajectory_name (str): 文件名称
    """
    _fields_ = [
        ('id', c_int),
        ('size', c_int),
        ('speed', c_int),
        ('trajectory_name', c_char * int(32)),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result


class rm_program_trajectorys_t(Structure):
    """
    查询在线编程列表

    **Args**:  
        - 无（无直接构造参数，此结构体通常由机械臂提供数据并填充，通过访问对应的属性读取信息）。  

    **Attributes**:  
        - page_num (int): 页码
        - page_size (int): 每页大小
        - list_size (int): 返回总数量
        - vague_search (bytes): 模糊搜索字符串
        - trajectory_list (list): 符合的在线编程列表（包含 rm_trajectory_data_t 结构体的数组）
    """
    _fields_ = [
        ('page_num', c_int),
        ('page_size', c_int),
        ('list_size', c_int),
        ('vague_search', c_char * int(32)),
        ('trajectory_list', rm_trajectory_data_t * int(100)),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        non_empty_outputs = []
        for i in range(self.list_size):
            if self.trajectory_list[i].trajectory_name != b'':  # 判断列表是否为空
                output = self.trajectory_list[i].to_dict()
                non_empty_outputs.append(output)
        result["trajectory_list"] = non_empty_outputs

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        return result


class rm_program_run_state_t(Structure):
    """  
    机械臂程序运行状态结构体  

    **Args:**  
        - 无（无直接构造参数，此结构体通常由机械臂提供数据并填充，通过访问对应的属性读取信息）  

    **Attributes:**  
        - run_state (int): 运行状态 0 未开始 1运行中 2暂停中  
        - id (int): 运行轨迹编号  
        - edit_id (int): 上次编辑的在线编程编号 id  
        - plan_num (int): 运行行数  
        - total_loop (int): 循环指令数量  
        - step_mode (int): 单步模式，1 为单步模式，0 为非单步模式  
        - plan_speed (int): 全局规划速度比例 1-100  
        - loop_num (int array[100]): 循环行数  
        - loop_cont (int array[100]): 对应循环次数  

    """
    _fields_ = [
        ('run_state', c_int),
        ('id', c_int),
        ('edit_id', c_int),
        ('plan_num', c_int),
        ('total_loop', c_int),
        ('step_mode', c_int),
        ('plan_speed', c_int),
        ('loop_num', c_int * int(100)),
        ('loop_cont', c_int * int(100)),
    ]

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value
        loop_num = []
        loop_cont = []
        for i in range(self.total_loop):
            output = self.loop_num[i]
            loop_num.append(output)
            output1 = self.loop_cont[i]
            loop_cont.append(output1)
        result["loop_num"] = loop_num
        result["loop_cont"] = loop_cont

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value
        if 0 == self.run_state:
            del result['plan_num']
            del result['loop_num']
            del result['loop_cont']
            del result['total_loop']
            del result['step_mode']
            del result['plan_speed']

        return result


class rm_waypoint_t(Structure):
    """  
    机械臂全局路点结构体  
    """
    _fields_ = [
        ('point_name', c_char * int(20)),
        ('joint', c_float * int(7)),
        ('pose', rm_pose_t),
        ('work_frame', c_char * int(12)),
        ('tool_frame', c_char * int(12)),
        ('time', c_char * int(50)),
    ]

    def __init__(self, point_name: str = None, joint: list[float] = None, pose: list[float] = None, work_frame: str = None, tool_frame: str = None, time: str = ''):
        """
        全局路点结构体初始化

        @param point_name (str, optional): 路点名称. 默认为None
        @param joint (list[float], optional): 关节角度列表，长度为7，单位：°. 默认为None
        @param pose (list[float], optional): 位姿信息，包含位置和欧拉角. 默认为None  
                该列表应为 [x, y, z, rx, ry, rz] 格式，其中 [x, y, z] 是位置，[rx, ry, rz] 是欧拉角.  
        @param work_frame (str, optional): 工作坐标系名称. 默认为None  
        @param tool_frame (str, optional):工具坐标系名称. 默认为None
        @param time (str, optional): 路点新增或修改时间. 默认为空字符串  
        """
        if all(param is None for param in [point_name, joint, pose, work_frame, tool_frame]):
            return
        else:
            # 路点名称
            self.point_name = point_name.encode('utf-8')
            # 关节角度
            self.joint = (c_float * ARM_DOF)(*joint)

            pose_value = rm_pose_t()
            pose_value.position = rm_position_t(*pose[:3])
            pose_value.euler = rm_euler_t(*pose[3:])
            # 位姿信息，包含位置和欧拉角
            self.pose = pose_value

            # 工作坐标系名称
            self.work_frame = work_frame.encode('utf-8')
            # 工具坐标系名称
            self.tool_frame = tool_frame.encode('utf-8')

            # 路点新增或修改时间
            self.time = time.encode('utf-8')

    def to_dict(self):
        """将类的变量返回为字典"""
        name = self.point_name.decode("utf-8")
        work_name = self.work_frame.decode("utf-8")
        tool_name = self.tool_frame.decode("utf-8")
        time = self.time.decode("utf-8")
        position = self.pose.position
        euler = self.pose.euler

        output_dict = {
            "point_name": name,
            "joint": [float(format(self.joint[i], ".3f")) for i in range(ARM_DOF)],
            "pose": [position.x, position.y, position.z, euler.rx, euler.ry, euler.rz],
            "work_frame": work_name,
            "tool_frame": tool_name,
            "time": time,
        }
        return output_dict


class rm_waypoint_list_t(Structure):
    """  
    机械臂全局路点列表获取结构体  

    Args:  
        无（无直接构造参数，此结构体通常由机械臂提供数据并填充，通过访问对应的属性读取信息）  

    Attributes:  
        - page_num (int): 页码  
        - page_size (int): 每页大小（即每页包含的路径点数量）  
        - total_size (int): 路点列表的总大小（即总路点数量）  
        - vague_search (bytes): 模糊搜索字符串（用于搜索路径点时的关键字）  
        - list_len (int): 返回符合的全局路点列表长度
        - points_list (rm_waypoint_t array[100]): 返回符合的全局路点列表
    """
    _fields_ = [
        ('page_num', c_int),
        ('page_size', c_int),
        ('total_size', c_int),
        ('vague_search', c_char * int(32)),
        ('list_len', c_int),
        ('points_list', rm_waypoint_t * int(100)),
    ]

    def to_dict(self):
        vague_search = self.vague_search.decode("utf-8")
        non_empty_outputs = []
        for i in range(self.list_len):
            if self.points_list[i].point_name != b'':  # 判断列表是否为空
                output = self.points_list[i].to_dict()
                non_empty_outputs.append(output)

        output_dict = {
            "total_size": self.total_size,
            "list_len": self.list_len,
            "points_list": non_empty_outputs,
        }
        return output_dict


class rm_fence_config_cube_t(Structure):
    """几何模型长方体参数"""
    _fields_ = [
        ('x_min_limit', c_float),
        ('x_max_limit', c_float),
        ('y_min_limit', c_float),
        ('y_max_limit', c_float),
        ('z_min_limit', c_float),
        ('z_max_limit', c_float),
    ]

    def __init__(self, x_min: float = None, x_max: float = None, y_min: float = None, y_max: float = None, z_min: float = None, z_max: float = None):
        """几何模型长方体参数初始化

        Args:
            x_min (float, optional): 长方体基于世界坐标系 X 方向最小位置，单位 m. Defaults to None.
            x_max (float, optional): 长方体基于世界坐标系 X 方向最大位置，单位 m. Defaults to None.
            y_min (float, optional): 长方体基于世界坐标系 Y 方向最小位置，单位 m. Defaults to None.
            y_max (float, optional): 长方体基于世界坐标系 Y 方向最大位置，单位 m. Defaults to None.
            z_min (float, optional): 长方体基于世界坐标系 Z 方向最小位置，单位 m. Defaults to None.
            z_max (float, optional): 长方体基于世界坐标系 Z 方向最大位置，单位 m. Defaults to None.
        """
        if all(param is None for param in [x_min, x_max, y_min, y_max, z_min, z_max]):
            return
        else:
            # 长方体基于世界坐标系 X 方向最小位置，单位 m
            self.x_min_limit = x_min
            # 长方体基于世界坐标系 X 方向最大位置，单位 m
            self.x_max_limit = x_max
            # 长方体基于世界坐标系 Y 方向最小位置，单位 m
            self.y_min_limit = y_min
            # 长方体基于世界坐标系 Y 方向最大位置，单位 m
            self.y_max_limit = y_max
            # 长方体基于世界坐标系 Z 方向最小位置，单位 m
            self.z_min_limit = z_min
            # 长方体基于世界坐标系 Z 方向最大位置，单位 m
            self.z_max_limit = z_max


class rm_fence_config_plane_t(Structure):
    """几何模型点面矢量平面参数"""
    _fields_ = [
        ('x1', c_float),
        ('y1', c_float),
        ('z1', c_float),
        ('x2', c_float),
        ('y2', c_float),
        ('z2', c_float),
        ('x3', c_float),
        ('y3', c_float),
        ('z3', c_float),
    ]

    def __init__(self, x1: float = None, y1: float = None, z1: float = None, x2: float = None, y2: float = None, z2: float = None, x3: float = None, y3: float = None, z3: float = None):
        """几何模型点面矢量平面参数初始化

        Args:
            x1 (float, optional): 点面矢量平面三点法中的第一个点x坐标，单位 m. Defaults to None.
            y1 (float, optional): 点面矢量平面三点法中的第一个点y坐标，单位 m. Defaults to None.
            z1 (float, optional): 点面矢量平面三点法中的第一个点z坐标，单位 m. Defaults to None.
            x2 (float, optional): 点面矢量平面三点法中的第二个点x坐标，单位 m. Defaults to None.
            y2 (float, optional): 点面矢量平面三点法中的第二个点y坐标，单位 m. Defaults to None.
            z2 (float, optional): 点面矢量平面三点法中的第二个点z坐标，单位 m. Defaults to None.
            x3 (float, optional): 点面矢量平面三点法中的第三个点x坐标，单位 m. Defaults to None.
            y3 (float, optional): 点面矢量平面三点法中的第三个点y坐标，单位 m. Defaults to None.
            z3 (float, optional): 点面矢量平面三点法中的第三个点z坐标，单位 m. Defaults to None.
        """
        if all(param is None for param in [x1, y1, z1, x2, y2, z2, x3, y3, z3]):
            return
        else:
            # 点面矢量平面三点法中的第一个点x坐标，单位 m
            self.x1 = x1
            # 点面矢量平面三点法中的第一个点y坐标，单位 m
            self.y1 = y1
            # 点面矢量平面三点法中的第一个点z坐标，单位 m
            self.z1 = z1
            # 点面矢量平面三点法中的第二个点x坐标，单位 m
            self.x2 = x2
            # 点面矢量平面三点法中的第二个点y坐标，单位 m
            self.y2 = y2
            # 点面矢量平面三点法中的第二个点z坐标，单位 m
            self.z2 = z2
            # 点面矢量平面三点法中的第三个点x坐标，单位 m
            self.x3 = x3
            # 点面矢量平面三点法中的第三个点y坐标，单位 m
            self.y3 = y3
            # 点面矢量平面三点法中的第三个点z坐标，单位 m
            self.z3 = z3


class rm_fence_config_sphere_t(Structure):
    """几何模型球体参数"""
    _fields_ = [
        ('x', c_float),
        ('y', c_float),
        ('z', c_float),
        ('radius', c_float),
    ]

    def __init__(self, x: float = None, y: float = None, z: float = None, radius: float = None):
        """几何模型球体参数初始化

        Args:
            x (float, optional): 表示球心在世界坐标系 X 轴的坐标，单位 m. Defaults to None.
            y (float, optional): 表示球心在世界坐标系 Y 轴的坐标，单位 m. Defaults to None.
            z (float, optional): 表示球心在世界坐标系 Z 轴的坐标，单位 m. Defaults to None.
            radius (float, optional): 表示半径，单位 m. Defaults to None.
        """
        if all(param is None for param in [x, y, z, radius]):
            return
        else:
            # 表示球心在世界坐标系 X 轴的坐标，单位 m
            self.x = x
            # 表示球心在世界坐标系 Y 轴的坐标，单位 m
            self.y = y
            # 表示球心在世界坐标系 Z 轴的坐标，单位 m
            self.z = z
            # 表示半径，单位 m
            self.radius = radius


class rm_fence_config_t(Structure):
    """电子围栏参数结构体"""
    _fields_ = [
        ('form', c_int),
        ('name', c_char * int(12)),
        ('cube', rm_fence_config_cube_t),
        ('plan', rm_fence_config_plane_t),
        ('sphere', rm_fence_config_sphere_t),
    ]

    def __init__(self, form=0, name='', cube: rm_fence_config_cube_t=None, plane=None, sphere=None):
        """
        电子围栏参数初始化

        @param form (int, optional): 形状，1 表示长方体，2 表示点面矢量平面，3 表示球体. Defaults to 0.
        @param name (str, optional): 电子围栏名称，不超过 10 个字节，支持字母、数字、下划线. Defaults to ''.
        @param cube (rm_fence_config_cube_t, optional): 长方体参数. Defaults to None.
        @param plane (rm_fence_config_plane_t, optional): 点面矢量平面参数. Defaults to None.
        @param sphere (rm_fence_config_sphere_t, optional): 球体参数. Defaults to None.
        """
        if all(param is None for param in [cube, plane, sphere]):
            return
        else:
            # 形状，1 表示长方体，2 表示点面矢量平面，3 表示球体
            self.form = form
            # 电子围栏名称
            self.name = name.encode('utf-8')[:12]  # 将字符串编码为字节，并限制长度为12

            if cube is not None and self.form == 1:
                # 长方体参数
                self.cube = cube
            else:
                self.cube = rm_fence_config_cube_t()  # 否则创建一个默认的cube实例

            if plane is not None and self.form == 2:
                # 点面矢量平面参数
                self.plane = plane
            else:
                self.plane = rm_fence_config_plane_t()

            if sphere is not None and self.form == 3:
                # 球体参数
                self.sphere = sphere
            else:
                self.sphere = rm_fence_config_sphere_t()

    def to_dict(self):
        name = self.name.decode("utf-8").strip()  # 去除字符串两端的空白字符
        output_dict = {"name": name}

        if self.form == 1:  # 立方体
            output_dict.update({
                "form": "cube",
                "x_min_limit": float(format(self.cube.x_min_limit, ".3f")),
                "x_max_limit": float(format(self.cube.x_max_limit, ".3f")),
                "y_min_limit": float(format(self.cube.y_min_limit, ".3f")),
                "y_max_limit": float(format(self.cube.y_max_limit, ".3f")),
                "z_min_limit": float(format(self.cube.z_min_limit, ".3f")),
                "z_max_limit": float(format(self.cube.z_max_limit, ".3f")),
            })
        elif self.form == 2:  # 点面矢量平面
            output_dict.update({
                "form": "point_face_vector_plane",
                "x1": float(format(self.plan.x1, ".3f")),
                "y1": float(format(self.plan.y1, ".3f")),
                "z1": float(format(self.plan.z1, ".3f")),
                "x2": float(format(self.plan.x2, ".3f")),
                "y2": float(format(self.plan.y2, ".3f")),
                "z2": float(format(self.plan.z2, ".3f")),
                "x3": float(format(self.plan.x3, ".3f")),
                "y3": float(format(self.plan.y3, ".3f")),
                "z3": float(format(self.plan.z3, ".3f")),
            })
        elif self.form == 3:  # 球体
            output_dict.update({
                "form": "sphere",
                "radius": float(format(self.sphere.radius, ".3f")),
                "x": float(format(self.sphere.x, ".3f")),
                "y": float(format(self.sphere.y, ".3f")),
                "z": float(format(self.sphere.z, ".3f")),
            })

        return output_dict


class rm_fence_names_t(Structure):
    """
    几何模型名称结构体

    **Attributes:**  
        - name (bytes): 几何模型名称,不超过10个字符  
    """
    _fields_ = [
        # 几何模型名称,不超过10个字符
        ('name', c_char * int(12)),
    ]


class rm_fence_config_list_t(Structure):
    """
    几何模型参数列表

    **Attributes:**  
        - config (rm_fence_config_t[]): 几何模型参数列表,不超过10个  
    """
    _fields_ = [
        ('config', rm_fence_config_t * int(10)),
    ]


class rm_envelopes_ball_t(Structure):
    """工具坐标系包络参数"""
    _fields_ = [
        ('name', c_char * int(12)),
        ('radius', c_float),
        ('x', c_float),
        ('y', c_float),
        ('z', c_float),
    ]

    def __init__(self, name: str = None, radius: float = None, x: float = None, y: float = None, z: float = None):
        """工具坐标系包络参数初始化

        **Args:** 
            name (str, optional): 工具包络球体的名称，1-10 个字节，支持字母数字下划线. Defaults to None.
            radius (float, optional): 工具包络球体的半径，单位 0.001m. Defaults to None.
            x (float, optional): 工具包络球体球心基于末端法兰坐标系的 X 轴坐标，单位 m. Defaults to None.
            y (float, optional): 工具包络球体球心基于末端法兰坐标系的 Y 轴坐标，单位 m. Defaults to None.
            z (float, optional): 工具包络球体球心基于末端法兰坐标系的 Z 轴坐标，单位 m. Defaults to None.
        """
        if all(param is None for param in [name, radius, x, y, z]):
            return
        else:
            # 工具包络球体的名称，1-10 个字节，支持字母数字下划线
            self.name = name.encode('utf-8')
            # 工具包络球体的半径，单位 0.001m
            self.radius = radius
            # 工具包络球体球心基于末端法兰坐标系的 X 轴坐标，单位 m
            self.x = x
            # 工具包络球体球心基于末端法兰坐标系的 Y 轴坐标，单位 m
            self.y = y
            # 工具包络球体球心基于末端法兰坐标系的 Z 轴坐标，单位 m
            self.z = z

    def to_dictionary(self):
        """输出结果为字典"""
        name = self.name.decode("utf-8")
        # 创建一个字典，包含rm_envelopes_ball_t的所有属性
        output_dict = {
            "name": name,
            "radius": float(format(self.radius, ".3f")),
            "x": float(format(self.x, ".3f")),
            "y": float(format(self.y, ".3f")),
            "z": float(format(self.z, ".3f"))
        }
        return output_dict


class rm_envelope_balls_list_t(Structure):
    """工具的包络参数结构体，包含工具名称、包络球列表以及数量.
    """
    _fields_ = [
        ('balls', rm_envelopes_ball_t * int(5)),
        ('size', c_int),
        ('tool_name', c_char * 12),
    ]

    def __init__(self, tool_name: str = None, balls=None, size=None):
        """工具的包络参数结构体
        @param tool_name (str, optional): 工具的名称。  
        @param balls (list, optional): 一个包含rm_envelopes_ball_t实例的列表，表示包络球。  
        @param size (int, optional): 包络球的数量。  
        """
        if all(param is None for param in [tool_name, balls, size]):
            return
        else:
            # 工具的名称。
            self.tool_name: str = tool_name.encode('utf-8')
            """工具名称"""
            # 包含rm_envelopes_ball_t实例的列表，表示包络球，最多5个。
            self.balls = (rm_envelopes_ball_t * 5)(*balls)
            """包含rm_envelopes_ball_t实例的列表，表示包络球，最多5个。"""
            # 包络球的数量。
            self.size = size
            """包络球的数量。"""

    def to_dictionary(self):
        """将类的变量输出为字典"""
        name = self.tool_name.decode("utf-8")

        output_dict = {
            "tool_name": name,
            "list": [self.balls[i].to_dictionary() for i in range(self.size)],
            "size": self.size,
        }

        return output_dict


class rm_electronic_fence_enable_t(Structure):
    """电子围栏/虚拟墙使能状态结构体"""
    _fields_ = [
        ('enable_state', c_bool),
        ('in_out_side', c_int),
        ('effective_region', c_int),
    ]

    def __init__(self, enable_state: bool = None, in_out_side: int = None, effective_region: int = None):
        """工具的包络参数结构体
        @param enable_state (bool, optional): 电子围栏/虚拟墙使能状态，true 代表使能，false 代表禁使能
        @param in_out_side (int, optional): 0-机器人在电子围栏/虚拟墙内部，1-机器人在电子围栏外部
        @param effective_region (int, optional): 0-电子围栏针对整臂区域生效，1-虚拟墙针对末端生效
        """
        if all(param is None for param in [enable_state, in_out_side, effective_region]):
            return
        else:
            # 电子围栏/虚拟墙使能状态，true 代表使能，false 代表禁使能
            self.enable_state = enable_state
            # 0-机器人在电子围栏/虚拟墙内部，1-机器人在电子围栏外部
            self.in_out_side = in_out_side
            # 0-电子围栏针对整臂区域生效，1-虚拟墙针对末端生效
            self.effective_region = effective_region

    def to_dict(self, recurse=True):
        """将类的变量返回为字典，如果recurse为True，则递归处理ctypes结构字段"""
        result = {}
        for field, ctype in self._fields_:
            value = getattr(self, field)

            if recurse and isinstance(ctype, type) and issubclass(ctype, Structure):
                value = value.to_dict(recurse=recurse)
            result[field] = value

        for key, value in result.items():
            if isinstance(value, bytes):
                try:
                    # 尝试使用 UTF-8 解码
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果不是 UTF-8 编码，则可能需要根据实际情况处理
                    # 这里简单地将字节转换为十六进制字符串作为替代方案
                    result[key] = value.hex()
            else:
                # 值不是字节类型，直接保留
                result[key] = value

        return result


class rm_force_sensor_t(Structure):
    """
    力控数据结构体

    **Attributes**:
        - force (float[6]): 当前力传感器原始数据，力的单位为N；力矩单位为Nm。
        - zero_force (float[6]): 当前力传感器系统外受力数据，力的单位为N；力矩单位为Nm。
        - coordinate (int): 系统外受力数据的坐标系，0为传感器坐标系 1为当前工作坐标系 2为当前工具坐标系
    """
    _fields_ = [
        ('force', c_float * int(6)),
        ('zero_force', c_float * int(6)),
        ('coordinate', c_int),
    ]


class rm_udp_expand_state_t(Structure):
    """  
    扩展关节状态

    **Attributes**:  
        - pos (float): 当前角度  精度 0.001°，单位：°
        - current (int): 当前驱动电流，单位：mA，精度：1mA
        - err_flag (int): 驱动错误代码，错误代码类型参考关节错误代码
        - en_flag (int): 当前关节使能状态 ，1 为上使能，0 为掉使能
        - joint_id (int): 关节id号
        - mode (int): 当前升降状态，0-空闲，1-正方向速度运动，2-正方向位置运动，3-负方向速度运动，4-负方向位置运动
    """
    _fields_ = [
        ('pos', c_float),
        ('current', c_int),
        ('err_flag', c_int),
        ('en_flag', c_int),
        ('joint_id', c_int),
        ('mode', c_int),
    ]

class rm_udp_lift_state_t(Structure):
    """  
    升降机构状态

    **Attributes**:  
        - height (int): 当前升降机构高度，单位：mm，精度：1mm
        - pos (float): 当前角度  精度 0.001°，单位：°
        - current (int): 当前驱动电流，单位：mA，精度：1mA
        - err_flag (int): 驱动错误代码，错误代码类型参考关节错误代码
        - en_flag (int): 当前关节使能状态 ，1 为上使能，0 为掉使能
    """
    _fields_ = [
        ('height', c_int),
        ('pos', c_float),
        ('current', c_int),
        ('err_flag', c_int),
        ('en_flag', c_int),
    ]

class rm_realtime_arm_joint_state_t(Structure):
    """  
    机械臂实时状态推送信息结构体  

    **Attributes**:  
        - errCode (int): 数据解析错误码，-3为数据解析错误，代表推送的数据不完整或格式不正确  
        - arm_ip (bytes): 推送数据的机械臂的IP地址  
        - arm_err (uint16_t): 机械臂错误码  
        - joint_status (rm_joint_status_t): 机械臂关节状态结构体  
        - force_sensor (rm_force_sensor_t): 力传感器数据结构体  
        - sys_err (uint16_t): 系统错误码  
        - waypoint (rm_pose_t): 当前位置姿态结构体  
        - liftState (rm_udp_lift_state_t): 升降关节数据
        - expandState (rm_udp_expand_state_t): 扩展关节数据
    """
    _fields_ = [
        ('errCode', c_int),
        ('arm_ip', c_char * int(16)),
        ('arm_err', uint16_t),
        ('joint_status', rm_joint_status_t),
        ('force_sensor', rm_force_sensor_t),
        ('sys_err', uint16_t),
        ('waypoint', rm_pose_t),
        ('liftState', rm_udp_lift_state_t),
        ('expandState', rm_udp_expand_state_t),
    ]


class rm_inverse_kinematics_params_t(Structure):
    """  
    逆运动学参数结构体。  

    **Args:**  
        - q_in (List[float], optional): 上一时刻关节角度，单位°，默认为None。  
        - q_pose (List[float], optional): 目标位姿，根据flag的值，可以是位置+四元数或位置+欧拉角，默认为None。  
        - flag (int, optional): 标志位，0表示使用四元数，1表示使用欧拉角，默认为None。  
    """
    _fields_ = [
        ('q_in', c_float * int(7)),
        ('q_pose', rm_pose_t),
        ('flag', uint8_t),
    ]

    def __init__(self, q_in: list[float] = None, q_pose: list[float] = None, flag: int = None):
        """逆运动学参数初始化

        Args:
            q_in (list[float], optional): 上一时刻关节角度，单位°. Defaults to None.
            q_pose (list[float], optional): 目标位姿. Defaults to None.
            flag (int, optional): 姿态参数类别：0-四元数；1-欧拉角. Defaults to None.
        """
        if all(param is None for param in [q_in, q_pose, flag]):
            return
        else:
            # 上一时刻关节角度，单位°
            self.q_in = (c_float*7)(*q_in)

            po1 = rm_pose_t()
            po1.position = rm_position_t(*q_pose[:3])
            # 四元数
            if flag == 0:
                po1.quaternion = rm_quat_t(*q_pose[3:])
            # 欧拉角
            elif flag == 1:
                po1.euler = rm_euler_t(*q_pose[3:])
            # 目标位姿。根据flag的值，可以是位置+四元数或位置+欧拉角。
            self.q_pose = po1
            # 姿态数据的类别：0表示使用四元数，1表示使用欧拉角。
            self.flag = flag


class rm_matrix_t(Structure):
    """  
    矩阵结构体  

    **Attributes:**  
        - irow (int): 矩阵的行数。  
        - iline (int): 矩阵的列数。  
        - data (c_float * 16): 矩阵的数据部分，大小为4x4的浮点数矩阵。  
    """
    _fields_ = [
        ('irow', c_short),
        ('iline', c_short),
        ('data', (c_float * 16)),
    ]


    def __init__(self, irow=4, iline=4, data=None):  
            super().__init__()  
            self.irow = irow  
            self.iline = iline  
    
            if data is None:  
                self.data = (c_float * 16)(*([0.0] * 16))  # 初始化所有元素为0.0  
            else:  
                flattened_data = [float(val) for row in data for val in row]  
                if len(flattened_data) != 16:  
                    raise ValueError("Data must contain exactly 16 elements for a 4x4 matrix")  
                self.data = (c_float * 16)(*flattened_data)  

# 定义机械臂事件回调函数类型，该回调函数接受一个类型为 rm_event_push_data_t 的参数
rm_event_callback_ptr = CFUNCTYPE(None, rm_event_push_data_t)
# 定义机械臂实时状态回调函数类型，该回调函数接受一个类型为 rm_realtime_arm_joint_state_t 的参数
rm_realtime_arm_state_callback_ptr = CFUNCTYPE(
    None, rm_realtime_arm_joint_state_t)


class rm_robot_info_t(Structure):
    """  
    机械臂基本信息结构体  

    **Args:**  
        无直接构造参数，所有字段应通过访问属性进行设置。  

    **Attributes:**  
        arm_dof (c_int): 机械臂的自由度数量。  
        arm_model (c_int): 机械臂型号。  
        force_type (c_int): 机械臂末端力控类型。 
    """
    _fields_ = [
        ('arm_dof', c_int),
        ('arm_model', c_int),
        ('force_type', c_int),
    ]

    def to_dictionary(self):
        """将int类型数据转化为字符串，并输出结果为字典
        @return dict: 包含机械臂自由度'arm_dof'、型号'arm_model'、末端力控版本'force_type'值的字典
        """
        arm_dof = self.arm_dof
        model_to_string = {
            rm_robot_arm_model_e.RM_MODEL_RM_65_E: "RM_65",
            rm_robot_arm_model_e.RM_MODEL_RM_75_E: "RM_75",
            rm_robot_arm_model_e.RM_MODEL_RM_63_I_E: "RML_63",
            rm_robot_arm_model_e.RM_MODEL_RM_63_II_E: "RML_63",
            rm_robot_arm_model_e.RM_MODEL_RM_63_III_E: "RML_63",
            rm_robot_arm_model_e.RM_MODEL_ECO_65_E: "ECO_65",
            rm_robot_arm_model_e.RM_MODEL_ECO_62_E: "ECO_62",
            rm_robot_arm_model_e.RM_MODEL_GEN_72_E: "GEN_72"
        }
        force_to_string = {
            rm_force_type_e.RM_MODEL_RM_B_E: "B",
            rm_force_type_e.RM_MODEL_RM_ZF_E: "ZF",
            rm_force_type_e.RM_MODEL_RM_SF_E: "SF",
        }

        # 使用字典来查找对应的字符串表示
        try:
            model_string = model_to_string[self.arm_model]
            force_type = force_to_string[self.force_type]
        except KeyError:
            print(f"Unknown model value: {self.arm_model}, {self.force_type}")
        arm_model = model_string

        output_dict = {
            "arm_dof": arm_dof,
            "arm_model": arm_model if arm_dof != 0 else None,
            "force_type": force_type if arm_dof != 0 else None,
        }

        return output_dict


# rm_robot_info_t = struct_anon_50


class rm_robot_handle(Structure):
    """  
    机械臂句柄结构体  

    **Attributes**:  
        - id (int): 机械臂的唯一标识符，通过rm_create_robot_arm接口可创建机械臂句柄，用于在程序中控制特定的机械臂。 

    """
    _fields_ = [
        ('id', c_int),
    ]


# rm_robot_handle = struct_anon_51
# @cond HIDE_PRIVATE_CLASSES
if _libs[libname].has("rm_api_version", "cdecl"):
    rm_api_version = _libs[libname].get("rm_api_version", "cdecl")
    rm_api_version.argtypes = []
    if sizeof(c_int) == sizeof(c_void_p):
        rm_api_version.restype = ReturnString
    else:
        rm_api_version.restype = String
        rm_api_version.errcheck = ReturnString

if _libs[libname].has("rm_init", "cdecl"):
    rm_init = _libs[libname].get("rm_init", "cdecl")
    rm_init.argtypes = [c_int]
    rm_init.restype = c_int

if _libs[libname].has("rm_destory", "cdecl"):
    rm_destory = _libs[libname].get("rm_destory", "cdecl")
    rm_destory.argtypes = []
    rm_destory.restype = c_int

if _libs[libname].has("rm_set_log_call_back", "cdecl"):
    rm_set_log_call_back = _libs[libname].get("rm_set_log_call_back", "cdecl")
    # rm_set_log_call_back.argtypes = [CFUNCTYPE(UNCHECKED(None), String, c_void_p), c_int]
    rm_set_log_call_back.restype = None

if _libs[libname].has("rm_set_log_save", "cdecl"):
    rm_set_log_save = _libs[libname].get("rm_set_log_save", "cdecl")
    rm_set_log_save.argtypes = [String]
    rm_set_log_save.restype = None

if _libs[libname].has("rm_create_robot_arm", "cdecl"):
    rm_create_robot_arm = _libs[libname].get("rm_create_robot_arm", "cdecl")
    rm_create_robot_arm.argtypes = [String, c_int]
    rm_create_robot_arm.restype = POINTER(rm_robot_handle)

if _libs[libname].has("rm_delete_robot_arm", "cdecl"):
    rm_delete_robot_arm = _libs[libname].get("rm_delete_robot_arm", "cdecl")
    rm_delete_robot_arm.argtypes = [POINTER(rm_robot_handle)]
    rm_delete_robot_arm.restype = c_int

if _libs[libname].has("rm_set_arm_run_mode", "cdecl"):
    rm_set_arm_run_mode = _libs[libname].get("rm_set_arm_run_mode", "cdecl")
    rm_set_arm_run_mode.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_set_arm_run_mode.restype = c_int

if _libs[libname].has("rm_get_arm_run_mode", "cdecl"):
    rm_get_arm_run_mode = _libs[libname].get("rm_get_arm_run_mode", "cdecl")
    rm_get_arm_run_mode.argtypes = [POINTER(rm_robot_handle), POINTER(c_int)]
    rm_get_arm_run_mode.restype = c_int

if _libs[libname].has("rm_get_robot_info", "cdecl"):
    rm_get_robot_info = _libs[libname].get("rm_get_robot_info", "cdecl")
    rm_get_robot_info.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_robot_info_t)]
    rm_get_robot_info.restype = c_int

if _libs[libname].has("rm_get_arm_event_call_back", "cdecl"):
    rm_get_arm_event_call_back = _libs[libname].get(
        "rm_get_arm_event_call_back", "cdecl")
    rm_get_arm_event_call_back.argtypes = [rm_event_callback_ptr]
    rm_get_arm_event_call_back.restype = None

if _libs[libname].has("rm_realtime_arm_state_call_back", "cdecl"):
    rm_realtime_arm_state_call_back = _libs[libname].get(
        "rm_realtime_arm_state_call_back", "cdecl")
    rm_realtime_arm_state_call_back.argtypes = [
        rm_realtime_arm_state_callback_ptr]
    rm_realtime_arm_state_call_back.restype = None

if _libs[libname].has("rm_set_joint_max_speed", "cdecl"):
    rm_set_joint_max_speed = _libs[libname].get(
        "rm_set_joint_max_speed", "cdecl")
    rm_set_joint_max_speed.argtypes = [
        POINTER(rm_robot_handle), c_int, c_float]
    rm_set_joint_max_speed.restype = c_int

if _libs[libname].has("rm_set_joint_max_acc", "cdecl"):
    rm_set_joint_max_acc = _libs[libname].get("rm_set_joint_max_acc", "cdecl")
    rm_set_joint_max_acc.argtypes = [POINTER(rm_robot_handle), c_int, c_float]
    rm_set_joint_max_acc.restype = c_int

if _libs[libname].has("rm_set_joint_min_pos", "cdecl"):
    rm_set_joint_min_pos = _libs[libname].get("rm_set_joint_min_pos", "cdecl")
    rm_set_joint_min_pos.argtypes = [POINTER(rm_robot_handle), c_int, c_float]
    rm_set_joint_min_pos.restype = c_int

if _libs[libname].has("rm_set_joint_max_pos", "cdecl"):
    rm_set_joint_max_pos = _libs[libname].get("rm_set_joint_max_pos", "cdecl")
    rm_set_joint_max_pos.argtypes = [POINTER(rm_robot_handle), c_int, c_float]
    rm_set_joint_max_pos.restype = c_int

if _libs[libname].has("rm_set_joint_drive_max_speed", "cdecl"):
    rm_set_joint_drive_max_speed = _libs[libname].get(
        "rm_set_joint_drive_max_speed", "cdecl")
    rm_set_joint_drive_max_speed.argtypes = [
        POINTER(rm_robot_handle), c_int, c_float]
    rm_set_joint_drive_max_speed.restype = c_int

if _libs[libname].has("rm_set_joint_drive_max_acc", "cdecl"):
    rm_set_joint_drive_max_acc = _libs[libname].get(
        "rm_set_joint_drive_max_acc", "cdecl")
    rm_set_joint_drive_max_acc.argtypes = [
        POINTER(rm_robot_handle), c_int, c_float]
    rm_set_joint_drive_max_acc.restype = c_int

if _libs[libname].has("rm_set_joint_drive_min_pos", "cdecl"):
    rm_set_joint_drive_min_pos = _libs[libname].get(
        "rm_set_joint_drive_min_pos", "cdecl")
    rm_set_joint_drive_min_pos.argtypes = [
        POINTER(rm_robot_handle), c_int, c_float]
    rm_set_joint_drive_min_pos.restype = c_int

if _libs[libname].has("rm_set_joint_drive_max_pos", "cdecl"):
    rm_set_joint_drive_max_pos = _libs[libname].get(
        "rm_set_joint_drive_max_pos", "cdecl")
    rm_set_joint_drive_max_pos.argtypes = [
        POINTER(rm_robot_handle), c_int, c_float]
    rm_set_joint_drive_max_pos.restype = c_int

if _libs[libname].has("rm_set_joint_en_state", "cdecl"):
    rm_set_joint_en_state = _libs[libname].get(
        "rm_set_joint_en_state", "cdecl")
    rm_set_joint_en_state.argtypes = [POINTER(rm_robot_handle), c_int, c_int]
    rm_set_joint_en_state.restype = c_int

if _libs[libname].has("rm_set_joint_zero_pos", "cdecl"):
    rm_set_joint_zero_pos = _libs[libname].get(
        "rm_set_joint_zero_pos", "cdecl")
    rm_set_joint_zero_pos.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_set_joint_zero_pos.restype = c_int

if _libs[libname].has("rm_set_joint_clear_err", "cdecl"):
    rm_set_joint_clear_err = _libs[libname].get(
        "rm_set_joint_clear_err", "cdecl")
    rm_set_joint_clear_err.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_set_joint_clear_err.restype = c_int

if _libs[libname].has("rm_auto_set_joint_limit", "cdecl"):
    rm_auto_set_joint_limit = _libs[libname].get(
        "rm_auto_set_joint_limit", "cdecl")
    rm_auto_set_joint_limit.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_auto_set_joint_limit.restype = c_int

if _libs[libname].has("rm_get_joint_max_speed", "cdecl"):
    rm_get_joint_max_speed = _libs[libname].get(
        "rm_get_joint_max_speed", "cdecl")
    rm_get_joint_max_speed.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_joint_max_speed.restype = c_int

if _libs[libname].has("rm_get_joint_max_acc", "cdecl"):
    rm_get_joint_max_acc = _libs[libname].get("rm_get_joint_max_acc", "cdecl")
    rm_get_joint_max_acc.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_joint_max_acc.restype = c_int

if _libs[libname].has("rm_get_joint_min_pos", "cdecl"):
    rm_get_joint_min_pos = _libs[libname].get("rm_get_joint_min_pos", "cdecl")
    rm_get_joint_min_pos.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_joint_min_pos.restype = c_int

if _libs[libname].has("rm_get_joint_max_pos", "cdecl"):
    rm_get_joint_max_pos = _libs[libname].get("rm_get_joint_max_pos", "cdecl")
    rm_get_joint_max_pos.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_joint_max_pos.restype = c_int

if _libs[libname].has("rm_get_joint_drive_max_speed", "cdecl"):
    rm_get_joint_drive_max_speed = _libs[libname].get(
        "rm_get_joint_drive_max_speed", "cdecl")
    rm_get_joint_drive_max_speed.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_joint_drive_max_speed.restype = c_int

if _libs[libname].has("rm_get_joint_drive_max_acc", "cdecl"):
    rm_get_joint_drive_max_acc = _libs[libname].get(
        "rm_get_joint_drive_max_acc", "cdecl")
    rm_get_joint_drive_max_acc.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_joint_drive_max_acc.restype = c_int

if _libs[libname].has("rm_get_joint_drive_min_pos", "cdecl"):
    rm_get_joint_drive_min_pos = _libs[libname].get(
        "rm_get_joint_drive_min_pos", "cdecl")
    rm_get_joint_drive_min_pos.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_joint_drive_min_pos.restype = c_int

if _libs[libname].has("rm_get_joint_drive_max_pos", "cdecl"):
    rm_get_joint_drive_max_pos = _libs[libname].get(
        "rm_get_joint_drive_max_pos", "cdecl")
    rm_get_joint_drive_max_pos.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_joint_drive_max_pos.restype = c_int

if _libs[libname].has("rm_get_joint_en_state", "cdecl"):
    rm_get_joint_en_state = _libs[libname].get(
        "rm_get_joint_en_state", "cdecl")
    rm_get_joint_en_state.argtypes = [
        POINTER(rm_robot_handle), POINTER(uint8_t)]
    rm_get_joint_en_state.restype = c_int

if _libs[libname].has("rm_get_joint_err_flag", "cdecl"):
    rm_get_joint_err_flag = _libs[libname].get(
        "rm_get_joint_err_flag", "cdecl")
    rm_get_joint_err_flag.argtypes = [
        POINTER(rm_robot_handle), POINTER(uint16_t), POINTER(uint16_t)]
    rm_get_joint_err_flag.restype = c_int

if _libs[libname].has("rm_set_arm_max_line_speed", "cdecl"):
    rm_set_arm_max_line_speed = _libs[libname].get(
        "rm_set_arm_max_line_speed", "cdecl")
    rm_set_arm_max_line_speed.argtypes = [POINTER(rm_robot_handle), c_float]
    rm_set_arm_max_line_speed.restype = c_int

if _libs[libname].has("rm_set_arm_max_line_acc", "cdecl"):
    rm_set_arm_max_line_acc = _libs[libname].get(
        "rm_set_arm_max_line_acc", "cdecl")
    rm_set_arm_max_line_acc.argtypes = [POINTER(rm_robot_handle), c_float]
    rm_set_arm_max_line_acc.restype = c_int

if _libs[libname].has("rm_set_arm_max_angular_speed", "cdecl"):
    rm_set_arm_max_angular_speed = _libs[libname].get(
        "rm_set_arm_max_angular_speed", "cdecl")
    rm_set_arm_max_angular_speed.argtypes = [POINTER(rm_robot_handle), c_float]
    rm_set_arm_max_angular_speed.restype = c_int

if _libs[libname].has("rm_set_arm_max_angular_acc", "cdecl"):
    rm_set_arm_max_angular_acc = _libs[libname].get(
        "rm_set_arm_max_angular_acc", "cdecl")
    rm_set_arm_max_angular_acc.argtypes = [POINTER(rm_robot_handle), c_float]
    rm_set_arm_max_angular_acc.restype = c_int

if _libs[libname].has("rm_set_arm_tcp_init", "cdecl"):
    rm_set_arm_tcp_init = _libs[libname].get("rm_set_arm_tcp_init", "cdecl")
    rm_set_arm_tcp_init.argtypes = [POINTER(rm_robot_handle)]
    rm_set_arm_tcp_init.restype = c_int

if _libs[libname].has("rm_set_collision_state", "cdecl"):
    rm_set_collision_state = _libs[libname].get(
        "rm_set_collision_state", "cdecl")
    rm_set_collision_state.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_set_collision_state.restype = c_int

if _libs[libname].has("rm_get_collision_stage", "cdecl"):
    rm_get_collision_stage = _libs[libname].get(
        "rm_get_collision_stage", "cdecl")
    rm_get_collision_stage.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_int)]
    rm_get_collision_stage.restype = c_int

if _libs[libname].has("rm_get_arm_max_line_speed", "cdecl"):
    rm_get_arm_max_line_speed = _libs[libname].get(
        "rm_get_arm_max_line_speed", "cdecl")
    rm_get_arm_max_line_speed.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_arm_max_line_speed.restype = c_int

if _libs[libname].has("rm_get_arm_max_line_acc", "cdecl"):
    rm_get_arm_max_line_acc = _libs[libname].get(
        "rm_get_arm_max_line_acc", "cdecl")
    rm_get_arm_max_line_acc.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_arm_max_line_acc.restype = c_int

if _libs[libname].has("rm_get_arm_max_angular_speed", "cdecl"):
    rm_get_arm_max_angular_speed = _libs[libname].get(
        "rm_get_arm_max_angular_speed", "cdecl")
    rm_get_arm_max_angular_speed.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_arm_max_angular_speed.restype = c_int

if _libs[libname].has("rm_get_arm_max_angular_acc", "cdecl"):
    rm_get_arm_max_angular_acc = _libs[libname].get(
        "rm_get_arm_max_angular_acc", "cdecl")
    rm_get_arm_max_angular_acc.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_arm_max_angular_acc.restype = c_int

if _libs[libname].has("rm_set_auto_tool_frame", "cdecl"):
    rm_set_auto_tool_frame = _libs[libname].get(
        "rm_set_auto_tool_frame", "cdecl")
    rm_set_auto_tool_frame.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_set_auto_tool_frame.restype = c_int

if _libs[libname].has("rm_generate_auto_tool_frame", "cdecl"):
    rm_generate_auto_tool_frame = _libs[libname].get(
        "rm_generate_auto_tool_frame", "cdecl")
    rm_generate_auto_tool_frame.argtypes = [
        POINTER(rm_robot_handle), String, c_float, c_float, c_float, c_float]
    rm_generate_auto_tool_frame.restype = c_int

if _libs[libname].has("rm_set_manual_tool_frame", "cdecl"):
    rm_set_manual_tool_frame = _libs[libname].get(
        "rm_set_manual_tool_frame", "cdecl")
    rm_set_manual_tool_frame.argtypes = [POINTER(rm_robot_handle), rm_frame_t]
    rm_set_manual_tool_frame.restype = c_int

if _libs[libname].has("rm_change_tool_frame", "cdecl"):
    rm_change_tool_frame = _libs[libname].get("rm_change_tool_frame", "cdecl")
    rm_change_tool_frame.argtypes = [POINTER(rm_robot_handle), String]
    rm_change_tool_frame.restype = c_int

if _libs[libname].has("rm_delete_tool_frame", "cdecl"):
    rm_delete_tool_frame = _libs[libname].get("rm_delete_tool_frame", "cdecl")
    rm_delete_tool_frame.argtypes = [POINTER(rm_robot_handle), String]
    rm_delete_tool_frame.restype = c_int

if _libs[libname].has("rm_update_tool_frame", "cdecl"):
    rm_update_tool_frame = _libs[libname].get("rm_update_tool_frame", "cdecl")
    rm_update_tool_frame.argtypes = [POINTER(rm_robot_handle), rm_frame_t]
    rm_update_tool_frame.restype = c_int

if _libs[libname].has("rm_set_tool_envelope", "cdecl"):
    rm_set_tool_envelope = _libs[libname].get("rm_set_tool_envelope", "cdecl")
    rm_set_tool_envelope.argtypes = [
        POINTER(rm_robot_handle), rm_envelope_balls_list_t]
    rm_set_tool_envelope.restype = c_int

if _libs[libname].has("rm_get_tool_envelope", "cdecl"):
    rm_get_tool_envelope = _libs[libname].get("rm_get_tool_envelope", "cdecl")
    rm_get_tool_envelope.argtypes = [
        POINTER(rm_robot_handle), String, POINTER(rm_envelope_balls_list_t)]
    rm_get_tool_envelope.restype = c_int

if _libs[libname].has("rm_set_auto_work_frame", "cdecl"):
    rm_set_auto_work_frame = _libs[libname].get(
        "rm_set_auto_work_frame", "cdecl")
    rm_set_auto_work_frame.argtypes = [POINTER(rm_robot_handle), String, c_int]
    rm_set_auto_work_frame.restype = c_int

if _libs[libname].has("rm_set_manual_work_frame", "cdecl"):
    rm_set_manual_work_frame = _libs[libname].get(
        "rm_set_manual_work_frame", "cdecl")
    rm_set_manual_work_frame.argtypes = [
        POINTER(rm_robot_handle), String, rm_pose_t]
    rm_set_manual_work_frame.restype = c_int

if _libs[libname].has("rm_change_work_frame", "cdecl"):
    rm_change_work_frame = _libs[libname].get("rm_change_work_frame", "cdecl")
    rm_change_work_frame.argtypes = [POINTER(rm_robot_handle), String]
    rm_change_work_frame.restype = c_int

if _libs[libname].has("rm_delete_work_frame", "cdecl"):
    rm_delete_work_frame = _libs[libname].get("rm_delete_work_frame", "cdecl")
    rm_delete_work_frame.argtypes = [POINTER(rm_robot_handle), String]
    rm_delete_work_frame.restype = c_int

if _libs[libname].has("rm_update_work_frame", "cdecl"):
    rm_update_work_frame = _libs[libname].get("rm_update_work_frame", "cdecl")
    rm_update_work_frame.argtypes = [
        POINTER(rm_robot_handle), String, rm_pose_t]
    rm_update_work_frame.restype = c_int

if _libs[libname].has("rm_get_total_tool_frame", "cdecl"):
    rm_get_total_tool_frame = _libs[libname].get(
        "rm_get_total_tool_frame", "cdecl")
    rm_get_total_tool_frame.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_frame_name_t), POINTER(c_int)]
    rm_get_total_tool_frame.restype = c_int

if _libs[libname].has("rm_get_given_tool_frame", "cdecl"):
    rm_get_given_tool_frame = _libs[libname].get(
        "rm_get_given_tool_frame", "cdecl")
    rm_get_given_tool_frame.argtypes = [
        POINTER(rm_robot_handle), String, POINTER(rm_frame_t)]
    rm_get_given_tool_frame.restype = c_int

if _libs[libname].has("rm_get_current_tool_frame", "cdecl"):
    rm_get_current_tool_frame = _libs[libname].get(
        "rm_get_current_tool_frame", "cdecl")
    rm_get_current_tool_frame.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_frame_t)]
    rm_get_current_tool_frame.restype = c_int

if _libs[libname].has("rm_get_total_work_frame", "cdecl"):
    rm_get_total_work_frame = _libs[libname].get(
        "rm_get_total_work_frame", "cdecl")
    rm_get_total_work_frame.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_frame_name_t), POINTER(c_int)]
    rm_get_total_work_frame.restype = c_int

if _libs[libname].has("rm_get_given_work_frame", "cdecl"):
    rm_get_given_work_frame = _libs[libname].get(
        "rm_get_given_work_frame", "cdecl")
    rm_get_given_work_frame.argtypes = [
        POINTER(rm_robot_handle), String, POINTER(rm_pose_t)]
    rm_get_given_work_frame.restype = c_int

if _libs[libname].has("rm_get_current_work_frame", "cdecl"):
    rm_get_current_work_frame = _libs[libname].get(
        "rm_get_current_work_frame", "cdecl")
    rm_get_current_work_frame.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_frame_t)]
    rm_get_current_work_frame.restype = c_int

if _libs[libname].has("rm_get_current_arm_state", "cdecl"):
    rm_get_current_arm_state = _libs[libname].get(
        "rm_get_current_arm_state", "cdecl")
    rm_get_current_arm_state.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_current_arm_state_t)]
    rm_get_current_arm_state.restype = c_int

if _libs[libname].has("rm_get_current_joint_temperature", "cdecl"):
    rm_get_current_joint_temperature = _libs[libname].get(
        "rm_get_current_joint_temperature", "cdecl")
    rm_get_current_joint_temperature.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_current_joint_temperature.restype = c_int

if _libs[libname].has("rm_get_current_joint_current", "cdecl"):
    rm_get_current_joint_current = _libs[libname].get(
        "rm_get_current_joint_current", "cdecl")
    rm_get_current_joint_current.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_current_joint_current.restype = c_int

if _libs[libname].has("rm_get_current_joint_voltage", "cdecl"):
    rm_get_current_joint_voltage = _libs[libname].get(
        "rm_get_current_joint_voltage", "cdecl")
    rm_get_current_joint_voltage.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_current_joint_voltage.restype = c_int

if _libs[libname].has("rm_set_init_pose", "cdecl"):
    rm_set_init_pose = _libs[libname].get("rm_set_init_pose", "cdecl")
    rm_set_init_pose.argtypes = [POINTER(rm_robot_handle), POINTER(c_float)]
    rm_set_init_pose.restype = c_int

if _libs[libname].has("rm_get_init_pose", "cdecl"):
    rm_get_init_pose = _libs[libname].get("rm_get_init_pose", "cdecl")
    rm_get_init_pose.argtypes = [POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_init_pose.restype = c_int

if _libs[libname].has("rm_movej", "cdecl"):
    rm_movej = _libs[libname].get("rm_movej", "cdecl")
    rm_movej.argtypes = [POINTER(rm_robot_handle), POINTER(
        c_float), c_int, c_int, c_int, c_int]
    rm_movej.restype = c_int

if _libs[libname].has("rm_movel", "cdecl"):
    rm_movel = _libs[libname].get("rm_movel", "cdecl")
    rm_movel.argtypes = [
        POINTER(rm_robot_handle), rm_pose_t, c_int, c_int, c_int, c_int]
    rm_movel.restype = c_int

if _libs[libname].has("rm_moves", "cdecl"):
    rm_moves = _libs[libname].get("rm_moves", "cdecl")
    rm_moves.argtypes = [
        POINTER(rm_robot_handle), rm_pose_t, c_int, c_int, c_int, c_int]
    rm_moves.restype = c_int

if _libs[libname].has("rm_movec", "cdecl"):
    rm_movec = _libs[libname].get("rm_movec", "cdecl")
    rm_movec.argtypes = [POINTER(
        rm_robot_handle), rm_pose_t, rm_pose_t, c_int, c_int, c_int, c_int, c_int]
    rm_movec.restype = c_int

if _libs[libname].has("rm_movej_p", "cdecl"):
    rm_movej_p = _libs[libname].get("rm_movej_p", "cdecl")
    rm_movej_p.argtypes = [
        POINTER(rm_robot_handle), rm_pose_t, c_int, c_int, c_int, c_int]
    rm_movej_p.restype = c_int

if _libs[libname].has("rm_movej_canfd", "cdecl"):
    rm_movej_canfd = _libs[libname].get("rm_movej_canfd", "cdecl")
    rm_movej_canfd.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float), c_bool, c_int]
    rm_movej_canfd.restype = c_int

if _libs[libname].has("rm_movep_canfd", "cdecl"):
    rm_movep_canfd = _libs[libname].get("rm_movep_canfd", "cdecl")
    rm_movep_canfd.argtypes = [POINTER(rm_robot_handle), rm_pose_t, c_bool]
    rm_movep_canfd.restype = c_int

if _libs[libname].has("rm_set_arm_slow_stop", "cdecl"):
    rm_set_arm_slow_stop = _libs[libname].get("rm_set_arm_slow_stop", "cdecl")
    rm_set_arm_slow_stop.argtypes = [POINTER(rm_robot_handle)]
    rm_set_arm_slow_stop.restype = c_int

if _libs[libname].has("rm_set_arm_stop", "cdecl"):
    rm_set_arm_stop = _libs[libname].get("rm_set_arm_stop", "cdecl")
    rm_set_arm_stop.argtypes = [POINTER(rm_robot_handle)]
    rm_set_arm_stop.restype = c_int

if _libs[libname].has("rm_set_arm_pause", "cdecl"):
    rm_set_arm_pause = _libs[libname].get("rm_set_arm_pause", "cdecl")
    rm_set_arm_pause.argtypes = [POINTER(rm_robot_handle)]
    rm_set_arm_pause.restype = c_int

if _libs[libname].has("rm_set_arm_continue", "cdecl"):
    rm_set_arm_continue = _libs[libname].get("rm_set_arm_continue", "cdecl")
    rm_set_arm_continue.argtypes = [POINTER(rm_robot_handle)]
    rm_set_arm_continue.restype = c_int

if _libs[libname].has("rm_set_delete_current_trajectory", "cdecl"):
    rm_set_delete_current_trajectory = _libs[libname].get(
        "rm_set_delete_current_trajectory", "cdecl")
    rm_set_delete_current_trajectory.argtypes = [POINTER(rm_robot_handle)]
    rm_set_delete_current_trajectory.restype = c_int

if _libs[libname].has("rm_set_arm_delete_trajectory", "cdecl"):
    rm_set_arm_delete_trajectory = _libs[libname].get(
        "rm_set_arm_delete_trajectory", "cdecl")
    rm_set_arm_delete_trajectory.argtypes = [POINTER(rm_robot_handle)]
    rm_set_arm_delete_trajectory.restype = c_int

if _libs[libname].has("rm_get_arm_current_trajectory", "cdecl"):
    rm_get_arm_current_trajectory = _libs[libname].get(
        "rm_get_arm_current_trajectory", "cdecl")
    rm_get_arm_current_trajectory.argtypes = [POINTER(rm_robot_handle), POINTER(c_int),
                                              POINTER(c_float)]
    rm_get_arm_current_trajectory.restype = c_int

if _libs[libname].has("rm_set_joint_step", "cdecl"):
    rm_set_joint_step = _libs[libname].get("rm_set_joint_step", "cdecl")
    rm_set_joint_step.argtypes = [
        POINTER(rm_robot_handle), c_int, c_float, c_int, c_int]
    rm_set_joint_step.restype = c_int

if _libs[libname].has("rm_set_pos_step", "cdecl"):
    rm_set_pos_step = _libs[libname].get("rm_set_pos_step", "cdecl")
    rm_set_pos_step.argtypes = [
        POINTER(rm_robot_handle), c_int, c_float, c_int, c_int]
    rm_set_pos_step.restype = c_int

if _libs[libname].has("rm_set_ort_step", "cdecl"):
    rm_set_ort_step = _libs[libname].get("rm_set_ort_step", "cdecl")
    rm_set_ort_step.argtypes = [
        POINTER(rm_robot_handle), c_int, c_float, c_int, c_int]
    rm_set_ort_step.restype = c_int

if _libs[libname].has("rm_set_joint_teach", "cdecl"):
    rm_set_joint_teach = _libs[libname].get("rm_set_joint_teach", "cdecl")
    rm_set_joint_teach.argtypes = [
        POINTER(rm_robot_handle), c_int, c_int, c_int]
    rm_set_joint_teach.restype = c_int

if _libs[libname].has("rm_set_pos_teach", "cdecl"):
    rm_set_pos_teach = _libs[libname].get("rm_set_pos_teach", "cdecl")
    rm_set_pos_teach.argtypes = [POINTER(rm_robot_handle), c_int, c_int, c_int]
    rm_set_pos_teach.restype = c_int

if _libs[libname].has("rm_set_ort_teach", "cdecl"):
    rm_set_ort_teach = _libs[libname].get("rm_set_ort_teach", "cdecl")
    rm_set_ort_teach.argtypes = [POINTER(rm_robot_handle), c_int, c_int, c_int]
    rm_set_ort_teach.restype = c_int

if _libs[libname].has("rm_set_stop_teach", "cdecl"):
    rm_set_stop_teach = _libs[libname].get("rm_set_stop_teach", "cdecl")
    rm_set_stop_teach.argtypes = [POINTER(rm_robot_handle)]
    rm_set_stop_teach.restype = c_int

if _libs[libname].has("rm_set_teach_frame", "cdecl"):
    rm_set_teach_frame = _libs[libname].get("rm_set_teach_frame", "cdecl")
    rm_set_teach_frame.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_set_teach_frame.restype = c_int

if _libs[libname].has("rm_get_teach_frame", "cdecl"):
    rm_get_teach_frame = _libs[libname].get("rm_get_teach_frame", "cdecl")
    rm_get_teach_frame.argtypes = [POINTER(rm_robot_handle), POINTER(c_int)]
    rm_get_teach_frame.restype = c_int

if _libs[libname].has("rm_get_controller_state", "cdecl"):
    rm_get_controller_state = _libs[libname].get(
        "rm_get_controller_state", "cdecl")
    rm_get_controller_state.argtypes = [POINTER(rm_robot_handle), POINTER(c_float), POINTER(c_float), POINTER(c_float),
                                        POINTER(c_int)]
    rm_get_controller_state.restype = c_int

if _libs[libname].has("rm_set_arm_power", "cdecl"):
    rm_set_arm_power = _libs[libname].get("rm_set_arm_power", "cdecl")
    rm_set_arm_power.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_set_arm_power.restype = c_int

if _libs[libname].has("rm_get_arm_power_state", "cdecl"):
    rm_get_arm_power_state = _libs[libname].get(
        "rm_get_arm_power_state", "cdecl")
    rm_get_arm_power_state.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_int)]
    rm_get_arm_power_state.restype = c_int

if _libs[libname].has("rm_get_system_runtime", "cdecl"):
    rm_get_system_runtime = _libs[libname].get(
        "rm_get_system_runtime", "cdecl")
    rm_get_system_runtime.argtypes = [POINTER(rm_robot_handle), POINTER(c_int), POINTER(c_int), POINTER(c_int),
                                      POINTER(c_int)]
    rm_get_system_runtime.restype = c_int

if _libs[libname].has("rm_clear_system_runtime", "cdecl"):
    rm_clear_system_runtime = _libs[libname].get(
        "rm_clear_system_runtime", "cdecl")
    rm_clear_system_runtime.argtypes = [POINTER(rm_robot_handle)]
    rm_clear_system_runtime.restype = c_int

if _libs[libname].has("rm_get_joint_odom", "cdecl"):
    rm_get_joint_odom = _libs[libname].get("rm_get_joint_odom", "cdecl")
    rm_get_joint_odom.argtypes = [POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_joint_odom.restype = c_int

if _libs[libname].has("rm_clear_joint_odom", "cdecl"):
    rm_clear_joint_odom = _libs[libname].get("rm_clear_joint_odom", "cdecl")
    rm_clear_joint_odom.argtypes = [POINTER(rm_robot_handle)]
    rm_clear_joint_odom.restype = c_int

if _libs[libname].has("rm_set_NetIP", "cdecl"):
    rm_set_NetIP = _libs[libname].get("rm_set_NetIP", "cdecl")
    rm_set_NetIP.argtypes = [POINTER(rm_robot_handle), String]
    rm_set_NetIP.restype = c_int

if _libs[libname].has("rm_clear_system_err", "cdecl"):
    rm_clear_system_err = _libs[libname].get("rm_clear_system_err", "cdecl")
    rm_clear_system_err.argtypes = [POINTER(rm_robot_handle)]
    rm_clear_system_err.restype = c_int

if _libs[libname].has("rm_get_arm_software_info", "cdecl"):
    rm_get_arm_software_info = _libs[libname].get(
        "rm_get_arm_software_info", "cdecl")
    rm_get_arm_software_info.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_arm_software_version_t)]
    rm_get_arm_software_info.restype = c_int

if _libs[libname].has("rm_set_wifi_ap", "cdecl"):
    rm_set_wifi_ap = _libs[libname].get("rm_set_wifi_ap", "cdecl")
    rm_set_wifi_ap.argtypes = [POINTER(rm_robot_handle), String, String]
    rm_set_wifi_ap.restype = c_int

if _libs[libname].has("rm_set_wifi_sta", "cdecl"):
    rm_set_wifi_sta = _libs[libname].get("rm_set_wifi_sta", "cdecl")
    rm_set_wifi_sta.argtypes = [POINTER(rm_robot_handle), String, String]
    rm_set_wifi_sta.restype = c_int

if _libs[libname].has("rm_set_RS485", "cdecl"):
    rm_set_RS485 = _libs[libname].get("rm_set_RS485", "cdecl")
    rm_set_RS485.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_set_RS485.restype = c_int

if _libs[libname].has("rm_get_wired_net", "cdecl"):
    rm_get_wired_net = _libs[libname].get("rm_get_wired_net", "cdecl")
    rm_get_wired_net.argtypes = [
        POINTER(rm_robot_handle), String, String, String]
    rm_get_wired_net.restype = c_int

if _libs[libname].has("rm_get_wifi_net", "cdecl"):
    rm_get_wifi_net = _libs[libname].get("rm_get_wifi_net", "cdecl")
    rm_get_wifi_net.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_wifi_net_t)]
    rm_get_wifi_net.restype = c_int

if _libs[libname].has("rm_set_net_default", "cdecl"):
    rm_set_net_default = _libs[libname].get("rm_set_net_default", "cdecl")
    rm_set_net_default.argtypes = [POINTER(rm_robot_handle)]
    rm_set_net_default.restype = c_int

if _libs[libname].has("rm_set_wifi_close", "cdecl"):
    rm_set_wifi_close = _libs[libname].get("rm_set_wifi_close", "cdecl")
    rm_set_wifi_close.argtypes = [POINTER(rm_robot_handle)]
    rm_set_wifi_close.restype = c_int

if _libs[libname].has("rm_get_joint_degree", "cdecl"):
    rm_get_joint_degree = _libs[libname].get("rm_get_joint_degree", "cdecl")
    rm_get_joint_degree.argtypes = [POINTER(rm_robot_handle), POINTER(c_float)]
    rm_get_joint_degree.restype = c_int

if _libs[libname].has("rm_get_arm_all_state", "cdecl"):
    rm_get_arm_all_state = _libs[libname].get("rm_get_arm_all_state", "cdecl")
    rm_get_arm_all_state.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_arm_all_state_t)]
    rm_get_arm_all_state.restype = c_int

if _libs[libname].has("rm_get_controller_RS485_mode", "cdecl"):
    rm_get_controller_RS485_mode = _libs[libname].get(
        "rm_get_controller_RS485_mode", "cdecl")
    rm_get_controller_RS485_mode.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_int), POINTER(c_int), POINTER(c_int)]
    rm_get_controller_RS485_mode.restype = c_int

if _libs[libname].has("rm_get_tool_RS485_mode", "cdecl"):
    rm_get_tool_RS485_mode = _libs[libname].get(
        "rm_get_tool_RS485_mode", "cdecl")
    rm_get_tool_RS485_mode.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_int), POINTER(c_int), POINTER(c_int)]
    rm_get_tool_RS485_mode.restype = c_int

if _libs[libname].has("rm_set_IO_mode", "cdecl"):
    rm_set_IO_mode = _libs[libname].get("rm_set_IO_mode", "cdecl")
    rm_set_IO_mode.argtypes = [POINTER(rm_robot_handle), c_int, c_int]
    rm_set_IO_mode.restype = c_int

if _libs[libname].has("rm_set_DO_state", "cdecl"):
    rm_set_DO_state = _libs[libname].get("rm_set_DO_state", "cdecl")
    rm_set_DO_state.argtypes = [POINTER(rm_robot_handle), c_int, c_int]
    rm_set_DO_state.restype = c_int

if _libs[libname].has("rm_get_IO_state", "cdecl"):
    rm_get_IO_state = _libs[libname].get("rm_get_IO_state", "cdecl")
    rm_get_IO_state.argtypes = [
        POINTER(rm_robot_handle), c_int, POINTER(c_int), POINTER(c_int)]
    rm_get_IO_state.restype = c_int

if _libs[libname].has("rm_get_IO_input", "cdecl"):
    rm_get_IO_input = _libs[libname].get("rm_get_IO_input", "cdecl")
    rm_get_IO_input.argtypes = [POINTER(rm_robot_handle), POINTER(c_int)]
    rm_get_IO_input.restype = c_int

if _libs[libname].has("rm_get_IO_output", "cdecl"):
    rm_get_IO_output = _libs[libname].get("rm_get_IO_output", "cdecl")
    rm_get_IO_output.argtypes = [POINTER(rm_robot_handle), POINTER(c_int)]
    rm_get_IO_output.restype = c_int

if _libs[libname].has("rm_set_voltage", "cdecl"):
    rm_set_voltage = _libs[libname].get("rm_set_voltage", "cdecl")
    rm_set_voltage.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_set_voltage.restype = c_int

if _libs[libname].has("rm_get_voltage", "cdecl"):
    rm_get_voltage = _libs[libname].get("rm_get_voltage", "cdecl")
    rm_get_voltage.argtypes = [POINTER(rm_robot_handle), POINTER(c_int)]
    rm_get_voltage.restype = c_int

if _libs[libname].has("rm_set_tool_DO_state", "cdecl"):
    rm_set_tool_DO_state = _libs[libname].get("rm_set_tool_DO_state", "cdecl")
    rm_set_tool_DO_state.argtypes = [POINTER(rm_robot_handle), c_int, c_int]
    rm_set_tool_DO_state.restype = c_int

if _libs[libname].has("rm_set_tool_IO_mode", "cdecl"):
    rm_set_tool_IO_mode = _libs[libname].get("rm_set_tool_IO_mode", "cdecl")
    rm_set_tool_IO_mode.argtypes = [POINTER(rm_robot_handle), c_int, c_int]
    rm_set_tool_IO_mode.restype = c_int

if _libs[libname].has("rm_get_tool_IO_state", "cdecl"):
    rm_get_tool_IO_state = _libs[libname].get("rm_get_tool_IO_state", "cdecl")
    rm_get_tool_IO_state.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_int), POINTER(c_int)]
    rm_get_tool_IO_state.restype = c_int

if _libs[libname].has("rm_set_tool_voltage", "cdecl"):
    rm_set_tool_voltage = _libs[libname].get("rm_set_tool_voltage", "cdecl")
    rm_set_tool_voltage.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_set_tool_voltage.restype = c_int

if _libs[libname].has("rm_get_tool_voltage", "cdecl"):
    rm_get_tool_voltage = _libs[libname].get("rm_get_tool_voltage", "cdecl")
    rm_get_tool_voltage.argtypes = [POINTER(rm_robot_handle), POINTER(c_int)]
    rm_get_tool_voltage.restype = c_int

if _libs[libname].has("rm_set_gripper_route", "cdecl"):
    rm_set_gripper_route = _libs[libname].get("rm_set_gripper_route", "cdecl")
    rm_set_gripper_route.argtypes = [POINTER(rm_robot_handle), c_int, c_int]
    rm_set_gripper_route.restype = c_int

if _libs[libname].has("rm_set_gripper_release", "cdecl"):
    rm_set_gripper_release = _libs[libname].get(
        "rm_set_gripper_release", "cdecl")
    rm_set_gripper_release.argtypes = [
        POINTER(rm_robot_handle), c_int, c_bool, c_int]
    rm_set_gripper_release.restype = c_int

if _libs[libname].has("rm_set_gripper_pick", "cdecl"):
    rm_set_gripper_pick = _libs[libname].get("rm_set_gripper_pick", "cdecl")
    rm_set_gripper_pick.argtypes = [
        POINTER(rm_robot_handle), c_int, c_int, c_bool, c_int]
    rm_set_gripper_pick.restype = c_int

if _libs[libname].has("rm_set_gripper_pick_on", "cdecl"):
    rm_set_gripper_pick_on = _libs[libname].get(
        "rm_set_gripper_pick_on", "cdecl")
    rm_set_gripper_pick_on.argtypes = [
        POINTER(rm_robot_handle), c_int, c_int, c_bool, c_int]
    rm_set_gripper_pick_on.restype = c_int

if _libs[libname].has("rm_set_gripper_position", "cdecl"):
    rm_set_gripper_position = _libs[libname].get(
        "rm_set_gripper_position", "cdecl")
    rm_set_gripper_position.argtypes = [
        POINTER(rm_robot_handle), c_int, c_bool, c_int]
    rm_set_gripper_position.restype = c_int

if _libs[libname].has("rm_get_gripper_state", "cdecl"):
    rm_get_gripper_state = _libs[libname].get("rm_get_gripper_state", "cdecl")
    rm_get_gripper_state.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_gripper_state_t)]
    rm_get_gripper_state.restype = c_int

if _libs[libname].has("rm_get_force_data", "cdecl"):
    rm_get_force_data = _libs[libname].get("rm_get_force_data", "cdecl")
    rm_get_force_data.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_force_data_t)]
    rm_get_force_data.restype = c_int

if _libs[libname].has("rm_clear_force_data", "cdecl"):
    rm_clear_force_data = _libs[libname].get("rm_clear_force_data", "cdecl")
    rm_clear_force_data.argtypes = [POINTER(rm_robot_handle)]
    rm_clear_force_data.restype = c_int

if _libs[libname].has("rm_set_force_sensor", "cdecl"):
    rm_set_force_sensor = _libs[libname].get("rm_set_force_sensor", "cdecl")
    rm_set_force_sensor.argtypes = [POINTER(rm_robot_handle), c_bool]
    rm_set_force_sensor.restype = c_int

if _libs[libname].has("rm_manual_set_force", "cdecl"):
    rm_manual_set_force = _libs[libname].get("rm_manual_set_force", "cdecl")
    rm_manual_set_force.argtypes = [
        POINTER(rm_robot_handle), c_int, POINTER(c_float), c_bool]
    rm_manual_set_force.restype = c_int

if _libs[libname].has("rm_stop_set_force_sensor", "cdecl"):
    rm_stop_set_force_sensor = _libs[libname].get(
        "rm_stop_set_force_sensor", "cdecl")
    rm_stop_set_force_sensor.argtypes = [POINTER(rm_robot_handle)]
    rm_stop_set_force_sensor.restype = c_int

if _libs[libname].has("rm_get_Fz", "cdecl"):
    rm_get_Fz = _libs[libname].get("rm_get_Fz", "cdecl")
    rm_get_Fz.argtypes = [POINTER(rm_robot_handle), POINTER(rm_fz_data_t)]
    rm_get_Fz.restype = c_int

if _libs[libname].has("rm_clear_Fz", "cdecl"):
    rm_clear_Fz = _libs[libname].get("rm_clear_Fz", "cdecl")
    rm_clear_Fz.argtypes = [POINTER(rm_robot_handle)]
    rm_clear_Fz.restype = c_int

if _libs[libname].has("rm_auto_set_Fz", "cdecl"):
    rm_auto_set_Fz = _libs[libname].get("rm_auto_set_Fz", "cdecl")
    rm_auto_set_Fz.argtypes = [POINTER(rm_robot_handle), c_bool]
    rm_auto_set_Fz.restype = c_int

if _libs[libname].has("rm_manual_set_Fz", "cdecl"):
    rm_manual_set_Fz = _libs[libname].get("rm_manual_set_Fz", "cdecl")
    rm_manual_set_Fz.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float), POINTER(c_float), c_bool]
    rm_manual_set_Fz.restype = c_int

if _libs[libname].has("rm_start_drag_teach", "cdecl"):
    rm_start_drag_teach = _libs[libname].get("rm_start_drag_teach", "cdecl")
    rm_start_drag_teach.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_start_drag_teach.restype = c_int

if _libs[libname].has("rm_stop_drag_teach", "cdecl"):
    rm_stop_drag_teach = _libs[libname].get("rm_stop_drag_teach", "cdecl")
    rm_stop_drag_teach.argtypes = [POINTER(rm_robot_handle)]
    rm_stop_drag_teach.restype = c_int

if _libs[libname].has("rm_start_multi_drag_teach", "cdecl"):
    rm_start_multi_drag_teach = _libs[libname].get(
        "rm_start_multi_drag_teach", "cdecl")
    rm_start_multi_drag_teach.argtypes = [
        POINTER(rm_robot_handle), c_int, c_int]
    rm_start_multi_drag_teach.restype = c_int

if _libs[libname].has("rm_drag_trajectory_origin", "cdecl"):
    rm_drag_trajectory_origin = _libs[libname].get(
        "rm_drag_trajectory_origin", "cdecl")
    rm_drag_trajectory_origin.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_drag_trajectory_origin.restype = c_int

if _libs[libname].has("rm_run_drag_trajectory", "cdecl"):
    rm_run_drag_trajectory = _libs[libname].get(
        "rm_run_drag_trajectory", "cdecl")
    rm_run_drag_trajectory.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_run_drag_trajectory.restype = c_int

if _libs[libname].has("rm_pause_drag_trajectory", "cdecl"):
    rm_pause_drag_trajectory = _libs[libname].get(
        "rm_pause_drag_trajectory", "cdecl")
    rm_pause_drag_trajectory.argtypes = [POINTER(rm_robot_handle)]
    rm_pause_drag_trajectory.restype = c_int

if _libs[libname].has("rm_continue_drag_trajectory", "cdecl"):
    rm_continue_drag_trajectory = _libs[libname].get(
        "rm_continue_drag_trajectory", "cdecl")
    rm_continue_drag_trajectory.argtypes = [POINTER(rm_robot_handle)]
    rm_continue_drag_trajectory.restype = c_int

if _libs[libname].has("rm_stop_drag_trajectory", "cdecl"):
    rm_stop_drag_trajectory = _libs[libname].get(
        "rm_stop_drag_trajectory", "cdecl")
    rm_stop_drag_trajectory.argtypes = [POINTER(rm_robot_handle)]
    rm_stop_drag_trajectory.restype = c_int

if _libs[libname].has("rm_set_force_position", "cdecl"):
    rm_set_force_position = _libs[libname].get(
        "rm_set_force_position", "cdecl")
    rm_set_force_position.argtypes = [
        POINTER(rm_robot_handle), c_int, c_int, c_int, c_float]
    rm_set_force_position.restype = c_int

if _libs[libname].has("rm_stop_force_position", "cdecl"):
    rm_stop_force_position = _libs[libname].get(
        "rm_stop_force_position", "cdecl")
    rm_stop_force_position.argtypes = [POINTER(rm_robot_handle)]
    rm_stop_force_position.restype = c_int

if _libs[libname].has("rm_set_hand_posture", "cdecl"):
    rm_set_hand_posture = _libs[libname].get("rm_set_hand_posture", "cdecl")
    rm_set_hand_posture.argtypes = [
        POINTER(rm_robot_handle), c_int, c_bool, c_int]
    rm_set_hand_posture.restype = c_int

if _libs[libname].has("rm_set_hand_seq", "cdecl"):
    rm_set_hand_seq = _libs[libname].get("rm_set_hand_seq", "cdecl")
    rm_set_hand_seq.argtypes = [POINTER(rm_robot_handle), c_int, c_bool, c_int]
    rm_set_hand_seq.restype = c_int

if _libs[libname].has("rm_set_hand_angle", "cdecl"):
    rm_set_hand_angle = _libs[libname].get("rm_set_hand_angle", "cdecl")
    rm_set_hand_angle.argtypes = [POINTER(rm_robot_handle), POINTER(c_int)]
    rm_set_hand_angle.restype = c_int

if _libs[libname].has("rm_set_hand_speed", "cdecl"):
    rm_set_hand_speed = _libs[libname].get("rm_set_hand_speed", "cdecl")
    rm_set_hand_speed.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_set_hand_speed.restype = c_int

if _libs[libname].has("rm_set_hand_force", "cdecl"):
    rm_set_hand_force = _libs[libname].get("rm_set_hand_force", "cdecl")
    rm_set_hand_force.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_set_hand_force.restype = c_int

if _libs[libname].has("rm_set_modbus_mode", "cdecl"):
    rm_set_modbus_mode = _libs[libname].get("rm_set_modbus_mode", "cdecl")
    rm_set_modbus_mode.argtypes = [
        POINTER(rm_robot_handle), c_int, c_int, c_int]
    rm_set_modbus_mode.restype = c_int

if _libs[libname].has("rm_close_modbus_mode", "cdecl"):
    rm_close_modbus_mode = _libs[libname].get("rm_close_modbus_mode", "cdecl")
    rm_close_modbus_mode.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_close_modbus_mode.restype = c_int

if _libs[libname].has("rm_set_modbustcp_mode", "cdecl"):
    rm_set_modbustcp_mode = _libs[libname].get(
        "rm_set_modbustcp_mode", "cdecl")
    rm_set_modbustcp_mode.argtypes = [
        POINTER(rm_robot_handle), String, c_int, c_int]
    rm_set_modbustcp_mode.restype = c_int

if _libs[libname].has("rm_close_modbustcp_mode", "cdecl"):
    rm_close_modbustcp_mode = _libs[libname].get(
        "rm_close_modbustcp_mode", "cdecl")
    rm_close_modbustcp_mode.argtypes = [POINTER(rm_robot_handle)]
    rm_close_modbustcp_mode.restype = c_int

if _libs[libname].has("rm_read_coils", "cdecl"):
    rm_read_coils = _libs[libname].get("rm_read_coils", "cdecl")
    rm_read_coils.argtypes = [
        POINTER(rm_robot_handle), rm_peripheral_read_write_params_t, POINTER(c_int)]
    rm_read_coils.restype = c_int

if _libs[libname].has("rm_read_input_status", "cdecl"):
    rm_read_input_status = _libs[libname].get("rm_read_input_status", "cdecl")
    rm_read_input_status.argtypes = [
        POINTER(rm_robot_handle), rm_peripheral_read_write_params_t, POINTER(c_int)]
    rm_read_input_status.restype = c_int

if _libs[libname].has("rm_read_holding_registers", "cdecl"):
    rm_read_holding_registers = _libs[libname].get(
        "rm_read_holding_registers", "cdecl")
    rm_read_holding_registers.argtypes = [
        POINTER(rm_robot_handle), rm_peripheral_read_write_params_t, POINTER(c_int)]
    rm_read_holding_registers.restype = c_int

if _libs[libname].has("rm_read_input_registers", "cdecl"):
    rm_read_input_registers = _libs[libname].get(
        "rm_read_input_registers", "cdecl")
    rm_read_input_registers.argtypes = [
        POINTER(rm_robot_handle), rm_peripheral_read_write_params_t, POINTER(c_int)]
    rm_read_input_registers.restype = c_int

if _libs[libname].has("rm_write_single_coil", "cdecl"):
    rm_write_single_coil = _libs[libname].get("rm_write_single_coil", "cdecl")
    rm_write_single_coil.argtypes = [
        POINTER(rm_robot_handle), rm_peripheral_read_write_params_t, c_int]
    rm_write_single_coil.restype = c_int

if _libs[libname].has("rm_write_single_register", "cdecl"):
    rm_write_single_register = _libs[libname].get(
        "rm_write_single_register", "cdecl")
    rm_write_single_register.argtypes = [
        POINTER(rm_robot_handle), rm_peripheral_read_write_params_t, c_int]
    rm_write_single_register.restype = c_int

if _libs[libname].has("rm_write_registers", "cdecl"):
    rm_write_registers = _libs[libname].get("rm_write_registers", "cdecl")
    rm_write_registers.argtypes = [
        POINTER(rm_robot_handle), rm_peripheral_read_write_params_t, POINTER(c_int)]
    rm_write_registers.restype = c_int

if _libs[libname].has("rm_write_coils", "cdecl"):
    rm_write_coils = _libs[libname].get("rm_write_coils", "cdecl")
    rm_write_coils.argtypes = [
        POINTER(rm_robot_handle), rm_peripheral_read_write_params_t, POINTER(c_int)]
    rm_write_coils.restype = c_int

if _libs[libname].has("rm_read_multiple_coils", "cdecl"):
    rm_read_multiple_coils = _libs[libname].get(
        "rm_read_multiple_coils", "cdecl")
    rm_read_multiple_coils.argtypes = [
        POINTER(rm_robot_handle), rm_peripheral_read_write_params_t, POINTER(c_int)]
    rm_read_multiple_coils.restype = c_int

if _libs[libname].has("rm_read_multiple_holding_registers", "cdecl"):
    rm_read_multiple_holding_registers = _libs[libname].get(
        "rm_read_multiple_holding_registers", "cdecl")
    rm_read_multiple_holding_registers.argtypes = [POINTER(rm_robot_handle), rm_peripheral_read_write_params_t,
                                                   POINTER(c_int)]
    rm_read_multiple_holding_registers.restype = c_int

if _libs[libname].has("rm_read_multiple_input_registers", "cdecl"):
    rm_read_multiple_input_registers = _libs[libname].get(
        "rm_read_multiple_input_registers", "cdecl")
    rm_read_multiple_input_registers.argtypes = [POINTER(rm_robot_handle), rm_peripheral_read_write_params_t,
                                                 POINTER(c_int)]
    rm_read_multiple_input_registers.restype = c_int

if _libs[libname].has("rm_set_install_pose", "cdecl"):
    rm_set_install_pose = _libs[libname].get("rm_set_install_pose", "cdecl")
    rm_set_install_pose.argtypes = [
        POINTER(rm_robot_handle), c_float, c_float, c_float]
    rm_set_install_pose.restype = c_int

if _libs[libname].has("rm_get_install_pose", "cdecl"):
    rm_get_install_pose = _libs[libname].get("rm_get_install_pose", "cdecl")
    rm_get_install_pose.argtypes = [POINTER(rm_robot_handle), POINTER(
        c_float), POINTER(c_float), POINTER(c_float)]
    rm_get_install_pose.restype = c_int

if _libs[libname].has("rm_get_joint_software_version", "cdecl"):
    rm_get_joint_software_version = _libs[libname].get(
        "rm_get_joint_software_version", "cdecl")
    rm_get_joint_software_version.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_int)]
    rm_get_joint_software_version.restype = c_int

if _libs[libname].has("rm_get_tool_software_version", "cdecl"):
    rm_get_tool_software_version = _libs[libname].get(
        "rm_get_tool_software_version", "cdecl")
    rm_get_tool_software_version.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_int)]
    rm_get_tool_software_version.restype = c_int

if _libs[libname].has("rm_start_force_position_move", "cdecl"):
    rm_start_force_position_move = _libs[libname].get(
        "rm_start_force_position_move", "cdecl")
    rm_start_force_position_move.argtypes = [POINTER(rm_robot_handle)]
    rm_start_force_position_move.restype = c_int

if _libs[libname].has("rm_stop_force_position_move", "cdecl"):
    rm_stop_force_position_move = _libs[libname].get(
        "rm_stop_force_position_move", "cdecl")
    rm_stop_force_position_move.argtypes = [POINTER(rm_robot_handle)]
    rm_stop_force_position_move.restype = c_int

if _libs[libname].has("rm_force_position_move_joint", "cdecl"):
    rm_force_position_move_joint = _libs[libname].get(
        "rm_force_position_move_joint", "cdecl")
    rm_force_position_move_joint.argtypes = [POINTER(rm_robot_handle), POINTER(c_float), c_int, c_int, c_int, c_float,
                                             c_bool]
    rm_force_position_move_joint.restype = c_int

if _libs[libname].has("rm_force_position_move_pose", "cdecl"):
    rm_force_position_move_pose = _libs[libname].get(
        "rm_force_position_move_pose", "cdecl")
    rm_force_position_move_pose.argtypes = [
        POINTER(rm_robot_handle), rm_pose_t, c_int, c_int, c_int, c_float, c_bool]
    rm_force_position_move_pose.restype = c_int

if _libs[libname].has("rm_set_lift_speed", "cdecl"):
    rm_set_lift_speed = _libs[libname].get("rm_set_lift_speed", "cdecl")
    rm_set_lift_speed.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_set_lift_speed.restype = c_int

if _libs[libname].has("rm_set_lift_height", "cdecl"):
    rm_set_lift_height = _libs[libname].get("rm_set_lift_height", "cdecl")
    rm_set_lift_height.argtypes = [
        POINTER(rm_robot_handle), c_int, c_int, c_int]
    rm_set_lift_height.restype = c_int

if _libs[libname].has("rm_get_lift_state", "cdecl"):
    rm_get_lift_state = _libs[libname].get("rm_get_lift_state", "cdecl")
    rm_get_lift_state.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_expand_state_t)]
    rm_get_lift_state.restype = c_int

if _libs[libname].has("rm_get_expand_state", "cdecl"):
    rm_get_expand_state = _libs[libname].get("rm_get_expand_state", "cdecl")
    rm_get_expand_state.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_expand_state_t)]
    rm_get_expand_state.restype = c_int

if _libs[libname].has("rm_set_expand_speed", "cdecl"):
    rm_set_expand_speed = _libs[libname].get("rm_set_expand_speed", "cdecl")
    rm_set_expand_speed.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_set_expand_speed.restype = c_int

if _libs[libname].has("rm_set_expand_pos", "cdecl"):
    rm_set_expand_pos = _libs[libname].get("rm_set_expand_pos", "cdecl")
    rm_set_expand_pos.argtypes = [
        POINTER(rm_robot_handle), c_int, c_int, c_int]
    rm_set_expand_pos.restype = c_int

if _libs[libname].has("rm_send_project", "cdecl"):
    rm_send_project = _libs[libname].get("rm_send_project", "cdecl")
    rm_send_project.argtypes = [
        POINTER(rm_robot_handle), rm_send_project_t, POINTER(c_int)]
    rm_send_project.restype = c_int

if _libs[libname].has("rm_set_plan_speed", "cdecl"):
    rm_set_plan_speed = _libs[libname].get("rm_set_plan_speed", "cdecl")
    rm_set_plan_speed.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_set_plan_speed.restype = c_int

if _libs[libname].has("rm_save_trajectory", "cdecl"):
    rm_save_trajectory = _libs[libname].get("rm_save_trajectory", "cdecl")
    rm_save_trajectory.argtypes = [
        POINTER(rm_robot_handle), String, POINTER(c_int)]
    rm_save_trajectory.restype = c_int

if _libs[libname].has("rm_get_program_trajectory_list", "cdecl"):
    rm_get_program_trajectory_list = _libs[libname].get(
        "rm_get_program_trajectory_list", "cdecl")
    rm_get_program_trajectory_list.argtypes = [POINTER(rm_robot_handle), c_int, c_int, String,
                                               POINTER(rm_program_trajectorys_t)]
    rm_get_program_trajectory_list.restype = c_int

if _libs[libname].has("rm_set_program_id_run", "cdecl"):
    rm_set_program_id_run = _libs[libname].get(
        "rm_set_program_id_run", "cdecl")
    rm_set_program_id_run.argtypes = [
        POINTER(rm_robot_handle), c_int, c_int, c_int]
    rm_set_program_id_run.restype = c_int

if _libs[libname].has("rm_get_program_run_state", "cdecl"):
    rm_get_program_run_state = _libs[libname].get(
        "rm_get_program_run_state", "cdecl")
    rm_get_program_run_state.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_program_run_state_t)]
    rm_get_program_run_state.restype = c_int

if _libs[libname].has("rm_delete_program_trajectory", "cdecl"):
    rm_delete_program_trajectory = _libs[libname].get(
        "rm_delete_program_trajectory", "cdecl")
    rm_delete_program_trajectory.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_delete_program_trajectory.restype = c_int

if _libs[libname].has("rm_update_program_trajectory", "cdecl"):
    rm_update_program_trajectory = _libs[libname].get(
        "rm_update_program_trajectory", "cdecl")
    rm_update_program_trajectory.argtypes = [
        POINTER(rm_robot_handle), c_int, c_int, String]
    rm_update_program_trajectory.restype = c_int

if _libs[libname].has("rm_set_default_run_program", "cdecl"):
    rm_set_default_run_program = _libs[libname].get(
        "rm_set_default_run_program", "cdecl")
    rm_set_default_run_program.argtypes = [POINTER(rm_robot_handle), c_int]
    rm_set_default_run_program.restype = c_int

if _libs[libname].has("rm_get_default_run_program", "cdecl"):
    rm_get_default_run_program = _libs[libname].get(
        "rm_get_default_run_program", "cdecl")
    rm_get_default_run_program.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_int)]
    rm_get_default_run_program.restype = c_int

if _libs[libname].has("rm_set_realtime_push", "cdecl"):
    rm_set_realtime_push = _libs[libname].get("rm_set_realtime_push", "cdecl")
    rm_set_realtime_push.argtypes = [
        POINTER(rm_robot_handle), rm_realtime_push_config_t]
    rm_set_realtime_push.restype = c_int

if _libs[libname].has("rm_get_realtime_push", "cdecl"):
    rm_get_realtime_push = _libs[libname].get("rm_get_realtime_push", "cdecl")
    rm_get_realtime_push.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_realtime_push_config_t)]
    rm_get_realtime_push.restype = c_int

if _libs[libname].has("rm_add_global_waypoint", "cdecl"):
    rm_add_global_waypoint = _libs[libname].get(
        "rm_add_global_waypoint", "cdecl")
    rm_add_global_waypoint.argtypes = [POINTER(rm_robot_handle), rm_waypoint_t]
    rm_add_global_waypoint.restype = c_int

if _libs[libname].has("rm_update_global_waypoint", "cdecl"):
    rm_update_global_waypoint = _libs[libname].get(
        "rm_update_global_waypoint", "cdecl")
    rm_update_global_waypoint.argtypes = [
        POINTER(rm_robot_handle), rm_waypoint_t]
    rm_update_global_waypoint.restype = c_int

if _libs[libname].has("rm_delete_global_waypoint", "cdecl"):
    rm_delete_global_waypoint = _libs[libname].get(
        "rm_delete_global_waypoint", "cdecl")
    rm_delete_global_waypoint.argtypes = [POINTER(rm_robot_handle), String]
    rm_delete_global_waypoint.restype = c_int

if _libs[libname].has("rm_get_given_global_waypoint", "cdecl"):
    rm_get_given_global_waypoint = _libs[libname].get(
        "rm_get_given_global_waypoint", "cdecl")
    rm_get_given_global_waypoint.argtypes = [
        POINTER(rm_robot_handle), String, POINTER(rm_waypoint_t)]
    rm_get_given_global_waypoint.restype = c_int

if _libs[libname].has("rm_get_global_waypoints_list", "cdecl"):
    rm_get_global_waypoints_list = _libs[libname].get(
        "rm_get_global_waypoints_list", "cdecl")
    rm_get_global_waypoints_list.argtypes = [POINTER(rm_robot_handle), c_int, c_int, String,
                                             POINTER(rm_waypoint_list_t)]
    rm_get_global_waypoints_list.restype = c_int

if _libs[libname].has("rm_add_electronic_fence_config", "cdecl"):
    rm_add_electronic_fence_config = _libs[libname].get(
        "rm_add_electronic_fence_config", "cdecl")
    rm_add_electronic_fence_config.argtypes = [
        POINTER(rm_robot_handle), rm_fence_config_t]
    rm_add_electronic_fence_config.restype = c_int

if _libs[libname].has("rm_update_electronic_fence_config", "cdecl"):
    rm_update_electronic_fence_config = _libs[libname].get(
        "rm_update_electronic_fence_config", "cdecl")
    rm_update_electronic_fence_config.argtypes = [
        POINTER(rm_robot_handle), rm_fence_config_t]
    rm_update_electronic_fence_config.restype = c_int

if _libs[libname].has("rm_delete_electronic_fence_config", "cdecl"):
    rm_delete_electronic_fence_config = _libs[libname].get(
        "rm_delete_electronic_fence_config", "cdecl")
    rm_delete_electronic_fence_config.argtypes = [
        POINTER(rm_robot_handle), String]
    rm_delete_electronic_fence_config.restype = c_int

if _libs[libname].has("rm_get_electronic_fence_list_names", "cdecl"):
    rm_get_electronic_fence_list_names = _libs[libname].get(
        "rm_get_electronic_fence_list_names", "cdecl")
    rm_get_electronic_fence_list_names.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_fence_names_t), POINTER(c_int)]
    rm_get_electronic_fence_list_names.restype = c_int

if _libs[libname].has("rm_get_given_electronic_fence_config", "cdecl"):
    rm_get_given_electronic_fence_config = _libs[libname].get(
        "rm_get_given_electronic_fence_config", "cdecl")
    rm_get_given_electronic_fence_config.argtypes = [
        POINTER(rm_robot_handle), String, POINTER(rm_fence_config_t)]
    rm_get_given_electronic_fence_config.restype = c_int

if _libs[libname].has("rm_get_electronic_fence_list_infos", "cdecl"):
    rm_get_electronic_fence_list_infos = _libs[libname].get(
        "rm_get_electronic_fence_list_infos", "cdecl")
    rm_get_electronic_fence_list_infos.argtypes = [POINTER(rm_robot_handle), POINTER(rm_fence_config_list_t),
                                                   POINTER(c_int)]
    rm_get_electronic_fence_list_infos.restype = c_int

if _libs[libname].has("rm_set_electronic_fence_enable", "cdecl"):
    rm_set_electronic_fence_enable = _libs[libname].get(
        "rm_set_electronic_fence_enable", "cdecl")
    rm_set_electronic_fence_enable.argtypes = [
        POINTER(rm_robot_handle), rm_electronic_fence_enable_t]
    rm_set_electronic_fence_enable.restype = c_int

if _libs[libname].has("rm_get_electronic_fence_enable", "cdecl"):
    rm_get_electronic_fence_enable = _libs[libname].get(
        "rm_get_electronic_fence_enable", "cdecl")
    rm_get_electronic_fence_enable.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_electronic_fence_enable_t)]
    rm_get_electronic_fence_enable.restype = c_int

if _libs[libname].has("rm_set_electronic_fence_config", "cdecl"):
    rm_set_electronic_fence_config = _libs[libname].get(
        "rm_set_electronic_fence_config", "cdecl")
    rm_set_electronic_fence_config.argtypes = [
        POINTER(rm_robot_handle), rm_fence_config_t]
    rm_set_electronic_fence_config.restype = c_int

if _libs[libname].has("rm_get_electronic_fence_config", "cdecl"):
    rm_get_electronic_fence_config = _libs[libname].get(
        "rm_get_electronic_fence_config", "cdecl")
    rm_get_electronic_fence_config.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_fence_config_t)]
    rm_get_electronic_fence_config.restype = c_int

if _libs[libname].has("rm_set_virtual_wall_enable", "cdecl"):
    rm_set_virtual_wall_enable = _libs[libname].get(
        "rm_set_virtual_wall_enable", "cdecl")
    rm_set_virtual_wall_enable.argtypes = [
        POINTER(rm_robot_handle), rm_electronic_fence_enable_t]
    rm_set_virtual_wall_enable.restype = c_int

if _libs[libname].has("rm_get_virtual_wall_enable", "cdecl"):
    rm_get_virtual_wall_enable = _libs[libname].get(
        "rm_get_virtual_wall_enable", "cdecl")
    rm_get_virtual_wall_enable.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_electronic_fence_enable_t)]
    rm_get_virtual_wall_enable.restype = c_int

if _libs[libname].has("rm_set_virtual_wall_config", "cdecl"):
    rm_set_virtual_wall_config = _libs[libname].get(
        "rm_set_virtual_wall_config", "cdecl")
    rm_set_virtual_wall_config.argtypes = [
        POINTER(rm_robot_handle), rm_fence_config_t]
    rm_set_virtual_wall_config.restype = c_int

if _libs[libname].has("rm_get_virtual_wall_config", "cdecl"):
    rm_get_virtual_wall_config = _libs[libname].get(
        "rm_get_virtual_wall_config", "cdecl")
    rm_get_virtual_wall_config.argtypes = [
        POINTER(rm_robot_handle), POINTER(rm_fence_config_t)]
    rm_get_virtual_wall_config.restype = c_int

if _libs[libname].has("rm_set_self_collision_enable", "cdecl"):
    rm_set_self_collision_enable = _libs[libname].get(
        "rm_set_self_collision_enable", "cdecl")
    rm_set_self_collision_enable.argtypes = [POINTER(rm_robot_handle), c_bool]
    rm_set_self_collision_enable.restype = c_int

if _libs[libname].has("rm_get_self_collision_enable", "cdecl"):
    rm_get_self_collision_enable = _libs[libname].get(
        "rm_get_self_collision_enable", "cdecl")
    rm_get_self_collision_enable.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_bool)]
    rm_get_self_collision_enable.restype = c_int

if _libs[libname].has("rm_algo_init_sys_data", "cdecl"):
    rm_algo_init_sys_data = _libs[libname].get(
        "rm_algo_init_sys_data", "cdecl")
    rm_algo_init_sys_data.argtypes = [c_int, c_int]
    rm_algo_init_sys_data.restype = None

if _libs[libname].has("rm_algo_set_angle", "cdecl"):
    rm_algo_set_angle = _libs[libname].get("rm_algo_set_angle", "cdecl")
    rm_algo_set_angle.argtypes = [c_float, c_float, c_float]
    rm_algo_set_angle.restype = None

if _libs[libname].has("rm_algo_get_angle", "cdecl"):
    rm_algo_get_angle = _libs[libname].get("rm_algo_get_angle", "cdecl")
    rm_algo_get_angle.argtypes = [
        POINTER(c_float), POINTER(c_float), POINTER(c_float)]
    rm_algo_get_angle.restype = None

if _libs[libname].has("rm_algo_set_workframe", "cdecl"):
    rm_algo_set_workframe = _libs[libname].get(
        "rm_algo_set_workframe", "cdecl")
    rm_algo_set_workframe.argtypes = [POINTER(rm_frame_t)]
    rm_algo_set_workframe.restype = None

if _libs[libname].has("rm_algo_get_curr_workframe", "cdecl"):
    rm_algo_get_curr_workframe = _libs[libname].get(
        "rm_algo_get_curr_workframe", "cdecl")
    rm_algo_get_curr_workframe.argtypes = [POINTER(rm_frame_t)]
    rm_algo_get_curr_workframe.restype = None

if _libs[libname].has("rm_algo_set_toolframe", "cdecl"):
    rm_algo_set_toolframe = _libs[libname].get(
        "rm_algo_set_toolframe", "cdecl")
    rm_algo_set_toolframe.argtypes = [POINTER(rm_frame_t)]
    rm_algo_set_toolframe.restype = None

if _libs[libname].has("rm_algo_get_curr_toolframe", "cdecl"):
    rm_algo_get_curr_toolframe = _libs[libname].get(
        "rm_algo_get_curr_toolframe", "cdecl")
    rm_algo_get_curr_toolframe.argtypes = [POINTER(rm_frame_t)]
    rm_algo_get_curr_toolframe.restype = None

if _libs[libname].has("rm_algo_set_joint_max_limit", "cdecl"):
    rm_algo_set_joint_max_limit = _libs[libname].get(
        "rm_algo_set_joint_max_limit", "cdecl")
    rm_algo_set_joint_max_limit.argtypes = [POINTER(c_float)]
    rm_algo_set_joint_max_limit.restype = None

if _libs[libname].has("rm_algo_get_joint_max_limit", "cdecl"):
    rm_algo_get_joint_max_limit = _libs[libname].get(
        "rm_algo_get_joint_max_limit", "cdecl")
    rm_algo_get_joint_max_limit.argtypes = [POINTER(c_float)]
    rm_algo_get_joint_max_limit.restype = None

if _libs[libname].has("rm_algo_set_joint_min_limit", "cdecl"):
    rm_algo_set_joint_min_limit = _libs[libname].get(
        "rm_algo_set_joint_min_limit", "cdecl")
    rm_algo_set_joint_min_limit.argtypes = [POINTER(c_float)]
    rm_algo_set_joint_min_limit.restype = None

if _libs[libname].has("rm_algo_get_joint_min_limit", "cdecl"):
    rm_algo_get_joint_min_limit = _libs[libname].get(
        "rm_algo_get_joint_min_limit", "cdecl")
    rm_algo_get_joint_min_limit.argtypes = [POINTER(c_float)]
    rm_algo_get_joint_min_limit.restype = None

if _libs[libname].has("rm_algo_set_joint_max_speed", "cdecl"):
    rm_algo_set_joint_max_speed = _libs[libname].get(
        "rm_algo_set_joint_max_speed", "cdecl")
    rm_algo_set_joint_max_speed.argtypes = [POINTER(c_float)]
    rm_algo_set_joint_max_speed.restype = None

if _libs[libname].has("rm_algo_get_joint_max_speed", "cdecl"):
    rm_algo_get_joint_max_speed = _libs[libname].get(
        "rm_algo_get_joint_max_speed", "cdecl")
    rm_algo_get_joint_max_speed.argtypes = [POINTER(c_float)]
    rm_algo_get_joint_max_speed.restype = None

if _libs[libname].has("rm_algo_set_joint_max_acc", "cdecl"):
    rm_algo_set_joint_max_acc = _libs[libname].get(
        "rm_algo_set_joint_max_acc", "cdecl")
    rm_algo_set_joint_max_acc.argtypes = [POINTER(c_float)]
    rm_algo_set_joint_max_acc.restype = None

if _libs[libname].has("rm_algo_get_joint_max_acc", "cdecl"):
    rm_algo_get_joint_max_acc = _libs[libname].get(
        "rm_algo_get_joint_max_acc", "cdecl")
    rm_algo_get_joint_max_acc.argtypes = [POINTER(c_float)]
    rm_algo_get_joint_max_acc.restype = None

if _libs[libname].has("rm_algo_inverse_kinematics", "cdecl"):
    rm_algo_inverse_kinematics = _libs[libname].get(
        "rm_algo_inverse_kinematics", "cdecl")
    rm_algo_inverse_kinematics.argtypes = [POINTER(rm_robot_handle), rm_inverse_kinematics_params_t,
                                           POINTER(c_float)]
    rm_algo_inverse_kinematics.restype = c_int

if _libs[libname].has("rm_algo_forward_kinematics", "cdecl"):
    rm_algo_forward_kinematics = _libs[libname].get(
        "rm_algo_forward_kinematics", "cdecl")
    rm_algo_forward_kinematics.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float)]
    rm_algo_forward_kinematics.restype = rm_pose_t

if _libs[libname].has("rm_algo_euler2quaternion", "cdecl"):
    rm_algo_euler2quaternion = _libs[libname].get(
        "rm_algo_euler2quaternion", "cdecl")
    rm_algo_euler2quaternion.argtypes = [rm_euler_t]
    rm_algo_euler2quaternion.restype = rm_quat_t

if _libs[libname].has("rm_algo_quaternion2euler", "cdecl"):
    rm_algo_quaternion2euler = _libs[libname].get(
        "rm_algo_quaternion2euler", "cdecl")
    rm_algo_quaternion2euler.argtypes = [rm_quat_t]
    rm_algo_quaternion2euler.restype = rm_euler_t

if _libs[libname].has("rm_algo_euler2matrix", "cdecl"):
    rm_algo_euler2matrix = _libs[libname].get("rm_algo_euler2matrix", "cdecl")
    rm_algo_euler2matrix.argtypes = [rm_euler_t]
    rm_algo_euler2matrix.restype = rm_matrix_t

if _libs[libname].has("rm_algo_pos2matrix", "cdecl"):
    rm_algo_pos2matrix = _libs[libname].get("rm_algo_pos2matrix", "cdecl")
    rm_algo_pos2matrix.argtypes = [rm_pose_t]
    rm_algo_pos2matrix.restype = rm_matrix_t

if _libs[libname].has("rm_algo_matrix2pos", "cdecl"):
    rm_algo_matrix2pos = _libs[libname].get("rm_algo_matrix2pos", "cdecl")
    rm_algo_matrix2pos.argtypes = [rm_matrix_t]
    rm_algo_matrix2pos.restype = rm_pose_t

if _libs[libname].has("rm_algo_base2workframe", "cdecl"):
    rm_algo_base2workframe = _libs[libname].get(
        "rm_algo_base2workframe", "cdecl")
    rm_algo_base2workframe.argtypes = [rm_matrix_t, rm_pose_t]
    rm_algo_base2workframe.restype = rm_pose_t

if _libs[libname].has("rm_algo_workframe2base", "cdecl"):
    rm_algo_workframe2base = _libs[libname].get(
        "rm_algo_workframe2base", "cdecl")
    rm_algo_workframe2base.argtypes = [rm_matrix_t, rm_pose_t]
    rm_algo_workframe2base.restype = rm_pose_t

if _libs[libname].has("rm_algo_rotate_move", "cdecl"):
    rm_algo_rotate_move = _libs[libname].get("rm_algo_rotate_move", "cdecl")
    rm_algo_rotate_move.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float), c_int, c_float, rm_pose_t]
    rm_algo_rotate_move.restype = rm_pose_t

if _libs[libname].has("rm_algo_cartesian_tool", "cdecl"):
    rm_algo_cartesian_tool = _libs[libname].get(
        "rm_algo_cartesian_tool", "cdecl")
    rm_algo_cartesian_tool.argtypes = [
        POINTER(rm_robot_handle), POINTER(c_float), c_float, c_float, c_float]
    rm_algo_cartesian_tool.restype = rm_pose_t

if _libs[libname].has("rm_algo_pose_move", "cdecl"):
    rm_algo_pose_move = _libs[libname].get("rm_algo_pose_move", "cdecl")
    rm_algo_pose_move.argtypes = [POINTER(rm_robot_handle), rm_pose_t, POINTER(c_float), c_int]
    rm_algo_pose_move.restype = rm_pose_t

if _libs[libname].has("rm_algo_end2tool", "cdecl"):
    rm_algo_end2tool = _libs[libname].get("rm_algo_end2tool", "cdecl")
    rm_algo_end2tool.argtypes = [POINTER(rm_robot_handle), rm_pose_t]
    rm_algo_end2tool.restype = rm_pose_t

if _libs[libname].has("rm_algo_tool2end", "cdecl"):
    rm_algo_tool2end = _libs[libname].get("rm_algo_tool2end", "cdecl")
    rm_algo_tool2end.argtypes = [POINTER(rm_robot_handle), rm_pose_t]
    rm_algo_tool2end.restype = rm_pose_t

try:
    ARM_DOF = 7
except:
    pass

try:
    M_PI = 3.14159265358979323846
except:
    pass
# @endcond
# No inserted files

# No prefix-stripping
