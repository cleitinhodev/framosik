# Componentes de terceiros

A distribuição portátil inclui os pacotes oficiais abaixo, sem alteração dos binários. A interface usa ligação dinâmica com Qt/PySide6; seus módulos e DLLs permanecem separados e substituíveis. Textos de licença, créditos e metadados completos acompanham os pacotes em `runtime/Lib/site-packages`, incluindo diretórios `.dist-info` e arquivos de licença internos. Cópias da LGPLv3 e GPLv3 também estão na pasta `licenses`. O Python embutido inclui seu `LICENSE.txt` em `runtime`.

| Componente | Versão | Projeto / fontes |
|---|---|---|
| CPython | 3.12.10 | https://www.python.org/downloads/release/python-31210/ |
| PySide6 Essentials / Shiboken6 | 6.8.3 | https://code.qt.io/cgit/pyside/pyside-setup.git/ |
| Qt | 6.8.3 (incluído no PySide6) | https://download.qt.io/archive/qt/6.8/6.8.3/submodules/ |
| OpenCV Python headless | 4.11.0.86 | https://github.com/opencv/opencv-python |
| OpenCV | 4.11.0 | https://github.com/opencv/opencv/tree/4.11.0 |
| NumPy | 2.2.6 | https://github.com/numpy/numpy/tree/v2.2.6 |
| Pillow | 11.2.1 | https://github.com/python-pillow/Pillow/tree/11.2.1 |

As licenças upstream aplicam-se aos componentes (por exemplo, PSF para Python, LGPL/GPL/opção comercial para Qt/PySide6, Apache 2.0 para OpenCV e BSD para NumPy). Pacotes também podem incluir bibliotecas auxiliares com licenças próprias; consulte seus textos completos. A distribuição preserva esses arquivos. O OpenCV inclui o backend FFmpeg fornecido no wheel, com os avisos de terceiros correspondentes.

O launcher é compilado com Zig 0.13.0, usado somente na construção, e importa apenas KERNEL32.dll e USER32.dll do Windows. `build_tools/launcher.c` contém seu código completo. A aplicação Python está acessível em `app/` na distribuição portátil e também no pacote fonte separado.

Documentação técnica usada na implementação:
- https://docs.opencv.org/4.x/d7/df3/group__imgproc__motion.html
- https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html
- https://doc.qt.io/qtforpython-6/PySide6/QtCore/QThread.html
