from debugger import Debugger

debugger = Debugger()
pid = input("Enter the PID of the process to attach to: ")
debugger.attach(int(pid))
debugger.detach()
#debugger.load(b"C:\\Windows\\system32\\calc.exe")