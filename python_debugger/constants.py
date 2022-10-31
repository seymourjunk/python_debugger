import ctypes

# Mapping of the Microsoft types to ctypes
WORD        = ctypes.c_ushort
DWORD       = ctypes.c_ulong
LPBYTE      = ctypes.POINTER(ctypes.c_ubyte)
LPTSTR      = ctypes.POINTER(ctypes.c_char) 
HANDLE      = ctypes.c_void_p
PVOID       = ctypes.c_void_p
ULONG_PTR   = ctypes.POINTER(ctypes.c_ulong) # ctypes.c_ulong
LPVOID      = ctypes.c_void_p


# Define constants
DEBUG_PROCESS       = 0x00000001
CREATE_NEW_CONSOLE  = 0x00000010
DBG_CONTINUE        = 0x00010002
INFINITE            = 0xFFFFFFFF

# Structures for CreateProcessA()
# https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/ns-processthreadsapi-startupinfoa
class STARTUP_INFO(ctypes.Structure):
    _fields_ = [
        ("cb",              DWORD),     # the size of the structure, in bytes
        ("lpReserved",      LPTSTR),     # reserved; must be NULL
        ("lpDesktop",       LPTSTR),     # the name of the desktop
        ("lpTitle",         LPTSTR),     # the title displayed in the title bar if a new console window is created
        ("dwX",             DWORD),     # the x offset of the upper left corner, in pixels
        ("dwY",             DWORD),     # the y offset of the upper left corner, in pixels
        ("dwXSize",         DWORD),     # the width of the window, in pixels
        ("dwYSize",         DWORD),     # the height of the window, in pixels
        ("dwXCountChars",   DWORD),     # the screen buffer width, in character columns
        ("dwYCountChars",   DWORD),     # the screen buffer height, in character rows
        ("dwFillAttribute", DWORD),     # the initial text and background colors if a new console window is created in a console app
        ("dwFlags",         DWORD),     # a bitfield that determines whether certain STARTUPINFO members are used when the process creates a window
        ("wShowWindow",     WORD),
        ("cbReserved2",     WORD),      # reserved for use by the C Run-time; must be zero
        ("lpReserved2",     LPBYTE),    # reserved for use by the C Run-time; must be NULL
        ("hStdInput",       HANDLE),    # defines standart input handle
        ("hStdOutput",      HANDLE),    # defines standart output handle
        ("hStdError",       HANDLE),    # defines standart error handle
    ]


# https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/ns-processthreadsapi-process_information
class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("nProcess",    HANDLE),        # a handle to the newly created process
        ("hThread",     HANDLE),        # a handle to the primary thread of the newly created process
        ("dwProcessId", DWORD),         # a value that can be used to identify a process
        ("dwThreadId",  DWORD),         # a value that can be used to identify a thread
    ]

class EXCEPTION_RECORD(ctypes.Structure):
    pass

EXCEPTION_RECORD._fields_ = [
        ("ExceptionCode",           DWORD),
        ("ExceptionFlags",          DWORD),
        ("ExceptionRecord",         ctypes.POINTER(EXCEPTION_RECORD)),
        ("ExceptionAddress",        PVOID),
        ("NumberParameters",        DWORD),
        ("ExceptionInformation",    ULONG_PTR) # UINT_PTR * 15
    ]

class _EXCEPTION_RECORD(ctypes.Structure):
    _fields_ = [
        ("ExceptionCode",           DWORD),
        ("ExceptionFlags",          DWORD),
        ("ExceptionRecord",         ctypes.POINTER(EXCEPTION_RECORD)),
        ("ExceptionAddress",        PVOID),
        ("NumberParameters",        DWORD),
        ("ExceptionInformation",    ULONG_PTR) # UINT_PTR * 15
    ]

# defines structures of exception information
class EXCEPTION_DEBUG_INFO(ctypes.Structure):
    _fields_ = [
        ("ExceptionRecord", EXCEPTION_RECORD),
        ("dwFirstChance",   DWORD),
    ]

class CREATE_THREAD_DEBUG_INFO(ctypes.Structure):
    _fields_ = [
        ("hThread",             HANDLE),
        ("lpThreadLocalBase",   LPVOID),
        ("lpStartAddress",      LPVOID), # LPTHREAD_START_ROUTINE 
    ]

class CREATE_PROCESS_DEBUG_INFO(ctypes.Structure):
    _fields_ = [
        ("hFile",                   HANDLE),
        ("hProcess",                HANDLE),
        ("hThread",                 HANDLE),
        ("lpBaseOfImage",           LPVOID),
        ("dwDebugInfoFileOffset",   DWORD),
        ("nDebugInfoSize",          DWORD),
        ("lpThreadLocalBase",       LPVOID),
        ("lpStartAddress",          LPVOID), # LPTHREAD_START_ROUTINE 
        ("lpImageName",             LPVOID),
        ("fUnicode",                WORD),
    ]

class EXIT_THREAD_DEBUG_INFO(ctypes.Structure):
    _fields_ = [
        ("dwExitCode", DWORD),
    ]

class EXIT_PROCESS_DEBUG_INFO(ctypes.Structure):
    _fields_ = [
        ("dwExitCode", DWORD),
    ]

class LOAD_DLL_DEBUG_INFO(ctypes.Structure):
    _fields_ = [
        ("hFile",                   HANDLE),
        ("lpBaseOfDll",             LPVOID),
        ("dwDebugInfoFileOffset",   DWORD),
        ("nDebugInfoSize",          DWORD),
        ("lpImageName",             LPVOID),
        ("fUnicode",                WORD),
    ]

class UNLOAD_DLL_DEBUG_INFO(ctypes.Structure):
    _fields_ = [
        ("lpBaseOfDll", LPVOID),
    ]

class OUTPUT_DEBUG_STRING_INFO(ctypes.Structure):
    _fields_ = [
        #("lpDebugStringData",    LPSTR),
        ("fUnicode",             WORD),
        ("nDebugStringLength",   WORD),
    ]

class RIP_INFO(ctypes.Structure):
    _fields_ = [
        ("dwError", DWORD),
        ("dwType",  DWORD),
    ]

class DEBUG_EVENT_INFO(ctypes.Union):
    _fields_ = [
        ("Exception",           EXCEPTION_DEBUG_INFO),
        ("CreateThread",        CREATE_THREAD_DEBUG_INFO),
        ("CreateProcessInfo",   CREATE_PROCESS_DEBUG_INFO),
        ("ExitThread",          EXIT_THREAD_DEBUG_INFO ),
        ("ExitProcess",         EXIT_PROCESS_DEBUG_INFO),
        ("LoadDll",             LOAD_DLL_DEBUG_INFO),
        ("UnloadDll",           UNLOAD_DLL_DEBUG_INFO),
        ("DebugString",         OUTPUT_DEBUG_STRING_INFO),
        ("RipInfo",             RIP_INFO),
    ]


# https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-debug_event
class DEBUG_EVENT(ctypes.Structure):
    _fields_ = [
        ("dwDebugEventCode",    DWORD), # The code that identifies the type of debugging event
        ("dwProcessId",         DWORD), # The identifier of the process in which the debugging event occurred
        ("dwThreadId",          DWORD), # The identifier of the thread in which the debugging event occurred
        ('u',                   DEBUG_EVENT_INFO)
    ]


