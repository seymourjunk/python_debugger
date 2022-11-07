from debugger import Debugger

debugger = Debugger()
pid = input("Enter the PID of the process to attach to: ")
debugger.attach(int(pid))

threads = debugger.enumerate_threads()

# For each thread in the list we want to grab the value of each of the registers
for thread in threads:
    thread_context = debugger.get_thread_context(thread)

    if thread_context:
    # Let output the contents of some of the registers
        print(f"[*] Dumping registers for thread ID: {thread}")
        print("[**] General-Purpose Registers")
        print('-' * 10)
        print(f"[***] EAX: {thread_context.Eax}")
        print(f"[***] EBX: {thread_context.Ebx}")
        print(f"[***] ECX: {thread_context.Ecx}")
        print(f"[***] EDX: {thread_context.Edx}")
        print(f"[***] ESI: {thread_context.Esi}")
        print(f"[***] EDI: {thread_context.Edi}")
        print(f"[***] ESP: {thread_context.Esp}")
        print(f"[***] EBP: {thread_context.Ebp}")
        print("[**] Segment Registers")
        print('-' * 10)
        print(f"[***] CS: {thread_context.SegCs}")
        print(f"[***] DS: {thread_context.SegDs}")
        print(f"[***] SS: {thread_context.SegSs}")
        print("[*] END DUMP")
    else:
        print("[*] Unable to get a thread context")


debugger.detach()