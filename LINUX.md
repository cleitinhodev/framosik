# Framosik para Linux (x86_64)

Pacote portátil com Python e bibliotecas incluídos. Não precisa instalar Python nem usar Wine.

## Abrir

1. Baixe `Framosik-0.3.0-Linux-x86_64.tar.gz` na release v0.3.0.
2. Extraia o arquivo inteiro pelo gerenciador de arquivos.
3. Abra o executável `Framosik` dentro da pasta `Framosik`.

Se o gerenciador não abrir o executável, abra um terminal na pasta extraída e execute:

```sh
./Framosik
```

Mantenha `_internal` junto ao executável. A extração do tar preserva a permissão de execução; se o seu gerenciador a remover, use `chmod +x Framosik`. Não execute com sudo.

## Compatibilidade

Compilado e testado em Ubuntu 22.04 x86_64 (glibc 2.35). Destinado a Ubuntu 22.04/24.04 e distribuições compatíveis mais recentes; outras distribuições ainda precisam de teste. Não é um pacote ARM/Raspberry Pi nem Alpine/musl. As bibliotecas gráficas do sistema precisam estar disponíveis. Wayland pode usar XWayland; o teste automatizado usa X11 virtual.

Se aparecer erro de plugin Qt xcb ou biblioteca gráfica ausente, no Ubuntu/Debian instale:

```sh
sudo apt install libegl1 libopengl0 libgl1 libxkbcommon-x11-0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-xinerama0 libxcb-xkb1 libxcb-shape0
```

Abra pelo terminal para ver o erro completo. Erros Python de inicialização também são registrados em `~/Framosik/erro.log`. Preferências ficam normalmente em `~/.config/Bugzinho/Framosik.conf`.

## Verificação e compilação

O arquivo `.sha256` acompanha o pacote. Na pasta dos downloads:

```sh
sha256sum -c Framosik-0.3.0-Linux-x86_64.tar.gz.sha256
```

O GitHub Actions executa os testes do algoritmo/interface, abre o executável empacotado e repete a abertura após extrair o tar para outra pasta (com espaços), usando X11 virtual. Isso não substitui testes com vídeos reais e drivers da sua máquina.

Para compilar, use Python 3.12 em ambiente virtual, instale `requirements.txt` e `pyinstaller==6.22.3`; instale também `xvfb` e `xauth` além das bibliotecas gráficas acima. Execute `python build_tools/build_linux.py`.

O workflow pode adicionar o port a uma release existente: ele obtém o código da tag indicada e usa o script de empacotamento da revisão que disparou o workflow. A tag e o pacote Windows não são alterados. Não sobrescreve assets existentes. A v0.2.0 permanece como ponto de retorno.
