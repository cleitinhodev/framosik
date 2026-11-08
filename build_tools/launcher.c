/* Launcher Windows x64 sem CRT: usa apenas APIs do sistema. */
#define UNICODE
#define _UNICODE
#include <windows.h>
static wchar_t root[16384], python[16384], script[16384], command[32768];
DWORD _tls_index = 0; /* Símbolo exigido pelo linker Zig/MinGW sem CRT. */
static STARTUPINFOW si;
static PROCESS_INFORMATION pi;
void entry(void) {
    DWORD n = GetModuleFileNameW(NULL, root, 16384);
    if (!n || n >= 14000) ExitProcess(1);
    while (n && root[n] != L'\\') --n;
    if (!n) ExitProcess(1);
    root[n] = 0;
    lstrcpyW(python, root); lstrcatW(python, L"\\runtime\\pythonw.exe");
    lstrcpyW(script, root); lstrcatW(script, L"\\app\\main.py");
    lstrcpyW(command, L"\""); lstrcatW(command, python);
    lstrcatW(command, L"\" \""); lstrcatW(command, script); lstrcatW(command, L"\"");
    si.cb = sizeof(si);
    if (!CreateProcessW(python, command, NULL, NULL, FALSE, 0, NULL, root, &si, &pi)) {
        MessageBoxW(NULL, L"Não foi possível abrir o programa. Extraia o ZIP inteiro e mantenha as pastas app e runtime junto do executável.", L"Framosik", MB_OK|MB_ICONERROR);
        ExitProcess(1);
    }
    CloseHandle(pi.hThread); CloseHandle(pi.hProcess);
    ExitProcess(0);
}
