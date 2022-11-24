from debugger import Debugger

debugger = Debugger()
pid = input("Enter the PID of the process to attach to: ")
debugger.attach(int(pid))
# threads = debugger.enumerate_threads()

# # For each thread in the list we want to grab the value of each of the registers
# for thread in threads:
    # thread_context = debugger.get_thread_context(thread)

    # if thread_context:
    # # Let output the contents of some of the registers
        # print(f"[*] Dumping registers for thread ID: {thread}")
        # print("[**] General-Purpose Registers")
        # print('-' * 10)
        # print(f"[***] EAX: {hex(thread_context.Eax)}")
        # print(f"[***] EBX: {hex(thread_context.Ebx)}")
        # print(f"[***] ECX: {hex(thread_context.Ecx)}")
        # print(f"[***] EDX: {hex(thread_context.Edx)}")
        # print(f"[***] ESI: {hex(thread_context.Esi)}")
        # print(f"[***] EDI: {hex(thread_context.Edi)}")
        # print(f"[***] ESP: {hex(thread_context.Esp)}")
        # print(f"[***] EBP: {hex(thread_context.Ebp)}")
        # print("[**] Segment Registers")
        # print('-' * 10)
        # print(f"[***] CS: {hex(thread_context.SegCs)}")
        # print(f"[***] DS: {hex(thread_context.SegDs)}")
        # print(f"[***] SS: {hex(thread_context.SegSs)}")
        # print("[*] END DUMP")
    # else:
        # print("[*] Unable to get a thread context")

printf_address = debugger.get_function_address(b"msvcrt.dll", b"printf")

print(f"[*] Address of printf function from msvcrt.dll: {hex(printf_address)}")
debugger.set_breakpoint(printf_address)
debugger.run()
debugger.detach()