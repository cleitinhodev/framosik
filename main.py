"""Ponto de entrada; registra erros de inicialização também na versão sem console."""
import os
from pathlib import Path
import sys
import traceback

if __name__ == '__main__':
    try:
        from gui import run
        sys.exit(run(smoke_test='--smoke-test' in sys.argv))
    except Exception:
        message = traceback.format_exc()
        folder = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'Framosik'
        folder.mkdir(parents=True, exist_ok=True)
        log = folder / 'erro.log'
        log.write_text(message, encoding='utf-8')
        if sys.stderr:
            sys.stderr.write(message)
        if sys.platform == 'win32':
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, f'Não foi possível iniciar. Detalhes em:\n{log}\n\n{message[-1400:]}', 'Framosik', 0x10)
        raise SystemExit(1)
