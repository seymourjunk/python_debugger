import ctypes
import constants

kernel32 = ctypes.WinDLL("kernel32")

class Debugger():
    def __init__(self):
        self.handle_process     = None
        self.pid                = None
        self.debugger_active    = False

    def load(self, exe_path):
        """
        dwCreation flag determines how to create the process
        set creation_flags = CREATE_NEW_CONSOLE if you want
        to see the calculator GUI
        """
        creation_flags = constants.DEBUG_PROCESS

        # instatiate the structs
        startup_info    = constants.STARTUP_INFO()
        process_info    = constants.PROCESS_INFORMATION()

        """
        The following two options allow the started process
        to be shawn as a separate window. This also illustrates
        how different settings in the STARTUP_INFO struct
        can affect the debuggee
        """
        startup_info.dwFlags        = 0x1
        startup_info.wShowWindow    = 0x0

        # Initialize the cb variable
        startup_info.cb = ctypes.sizeof(startup_info)

        if kernel32.CreateProcessA(exe_path,
                                    None,
                                    None,
                                    None,
                                    None,
                                    creation_flags,
                                    None,
                                    None,
                                    ctypes.byref(startup_info),
                                    ctypes.byref(process_info)):
            print("[*] We have successfully launched the process!")
            print(f"[*] PID: {process_info.dwProcessId}")

            self.handle_process = self.open_process(process_info.dwProcessId)

        else:
            print(f"[*] Error: {hex(kernel32.GetLastError())}")

    def open_process(self, pid):
        # https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess
        return kernel32.OpenProcess(ctypes.PROCESS_ALL_ACCESS, pid, False)
    
    def attach(self, pid):
        # https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-debugactiveprocess
        if kernel32.DebugActiveProcess(pid):
            self.debugger_active = True
            self.pid = pid
            self.run()
        else:
            print(f"[*] Unable to attach to the process with PID: {pid}")


    def run(self):
        while self.debugger_active:
            self.get_debug_event()


    def get_debug_event(self):
        debug_event = constants.DEBUG_EVENT()
        continue_status = constants.DBG_CONTINUE

        if kernel32.WaitForDebugEvent(ctypes.byref(debug_event), constants.INFINITE):
            input("Press a key to continue...")
            self.debugger_active = False
            # https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-continuedebugevent
            kernel32.ContinueDebugEvent(debug_event.dwProcessId, debug_event.dwThreadId, continue_status)


    def detach(self):
        if kernel32.DebugActiveProcessStop(self.pid):
            print("[*] Finished debugging. Exiting...")
            return True
        else:
            print("There was an error")
            return False