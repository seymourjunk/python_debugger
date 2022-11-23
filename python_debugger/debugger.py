import ctypes
import constants

kernel32 = ctypes.WinDLL("kernel32")

class Debugger():
    def __init__(self):
        self.handle_process     = None
        self.pid                = None
        self.debugger_active    = False
        self.handle_thread      = None
        self.context            = None
        self.exception          = None
        self.exception_address  = 0x0
        self.breakpoints        = {}


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
        return kernel32.OpenProcess(constants.PROCESS_ALL_ACCESS, False, pid)
    
    def open_thread(self, thread_id):
        # https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openthread
        h_thread = kernel32.OpenThread(constants.THREAD_ALL_ACCESS, None, thread_id)

        if h_thread:
            return h_thread
        else:
            print("[*] Could not obtain a valid thread handle.")
            return False

    def read_process_memory(self, address, length):
        data = ""
        read_buf = ctypes.create_string_buffer(length)
        count = ctypes.c_ulong(0)

        if kernel32.ReadProcessMemory(self.handle_process, address, read_buf, length, ctypes.byref(count)):
            data += read_buf.raw
            return data
        return False

    def write_process_memory(self, address, data):
        count = ctypes.c_ulong(0)
        length = len(data)

        c_data = ctypes.c_char_p(data[count.value:])

        if kernel32.WriteProcessMemory(self.handle_process, address, c_data, length, ctypes.byref(count)):
            return True
        
        return False

    def set_breakpoint(self, address):
        if not self.breakpoints.has_key(address):
            try:
                # store the original byte
                original_byte = self.read_process_memory(address, 1)

                # write the INT3 opcode
                self.write_process_memory(address, "\xCC")

                #register the breakpoint in our internal list
                self.breakpoints[address] = (address, original_byte)
            except:
                return False
            
        return True

    def enumerate_threads(self):
        # https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot
        thread_entry = constants.THREADENTRY32()
        threads = []
        snapshot = kernel32.CreateToolhelp32Snapshot(constants.TH32CS_SNAPTHREAD, self.pid)

        if snapshot:
            #You have to set the size of the struct or the call will fail
            thread_entry.dwSize = ctypes.sizeof(thread_entry)
            success = kernel32.Thread32First(snapshot, ctypes.byref(thread_entry))

            while success:
                if thread_entry.th32OwnerProcessID == self.pid:
                    threads.append(thread_entry.th32ThreadID)

                success = kernel32.Thread32Next(snapshot, ctypes.byref(thread_entry))

            kernel32.CloseHandle(snapshot)
            return threads
        else:
            return []

    def get_thread_context(self, thread_id=None, h_thread=None):
        context = constants.CONTEXT()
        context.ContextFlags = constants.CONTEXT_FULL | constants.CONTEXT_DEBUG_REGISTERS

        # Obtain a handle to the thread
        #h_thread = self.open_thread(thread_id)
        # Obtain a handle to the thread
        if not h_thread:
            self.handle_thread = self.open_thread(thread_id)
        if kernel32.GetThreadContext(self.handle_thread, ctypes.byref(context)):
            #kernel32.CloseHandle(h_thread)
            return context
        else:
            return None

    def attach(self, pid):
        self.handle_process = self.open_process(pid)

        # https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-debugactiveprocess
        if kernel32.DebugActiveProcess(pid):
            self.debugger_active = True
            self.pid = pid
            #self.run()
        else:
            print(f"[*] Unable to attach to the process with PID: {pid}")

    def run(self):
        while self.debugger_active:
            self.get_debug_event()

    def get_debug_event(self):
        debug_event = constants.DEBUG_EVENT()
        continue_status = constants.DBG_CONTINUE

        if kernel32.WaitForDebugEvent(ctypes.byref(debug_event), constants.INFINITE):
            self.handle_thread = self.open_thread(debug_event.dwThreadId)
            self.context = self.get_thread_context(self.handle_thread)

            print(f"Event Code: {debug_event.dwDebugEventCode}, Thread ID: {debug_event.dwThreadId}")

            # input("Press a key to continue...")
            # self.debugger_active = False

            # check if the event code ia an exception
            if debug_event.dwDebugEventCode == constants.EXCEPTION_DEBUG_EVENT:
                self.exception = debug_event.u.Exception.ExceptionRecord.ExceptionCode
                self.exception_address = debug_event.u.Exception.ExceptionRecord.ExceptionAddress

                if self.exception == constants.EXCEPTION_ACCESS_VIOLATION:
                    print("[E]: Access Violation Detected")
                elif self.exception == constants.EXCEPTION_BREAKPOINT:
                    continue_status = self.exception_handler_breakpoint()
                elif self.exception == constants.EXCEPTION_GUARD_PAGE:
                    print("[E]: Guard Page Access Detected")
                elif self.exception == constants.EXCEPTION_SINGLE_STEP:
                    self.exception_handler_single_step()

            # https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-continuedebugevent      
            kernel32.ContinueDebugEvent(debug_event.dwProcessId, debug_event.dwThreadId, continue_status)

    def exception_handler_breakpoint(self):
        print("[*] Inside the breakpoint handler")
        print(f"Exception Address: {hex(self.exception_address)}")
        return constants.DBG_CONTINUE

    def exception_handler_single_step(self):
        pass

    def detach(self):
        if kernel32.DebugActiveProcessStop(self.pid):
            print("[*] Finished debugging. Exiting...")
            return True
        else:
            print("There was an error")
            return False