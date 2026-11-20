# Framosik — beta visual 0.5.0-beta.2

Projeto em Python com interface PySide6 para reconstruir uma cena estática a partir de um GIF ou vídeo com movimento da câmera. O código da aplicação foi escrito para este projeto; o processamento usa OpenCV, NumPy, Pillow e Qt. Não é um fork do Overmix e não usa IA generativa.

## Abrir a versão Windows portátil

1. Baixe `Framosik-0.5.0-beta.2-Windows-x64.zip` na release beta.
2. Extraia o ZIP em uma pasta e abra `Framosik.exe`. Mantenha a pasta `_internal` ao lado do executável.

O pacote inclui Python e as dependências para Windows x64. A versão estável para comparação está na [release v0.4.1](https://github.com/cleitinhodev/framosik/releases/tag/v0.4.1).

## Linux portátil

Extraia `Framosik-0.5.0-beta.2-Linux-x86_64.tar.gz` e execute `./Framosik` dentro da pasta extraída. A base de compatibilidade é Ubuntu 22.04 x86_64 com glibc 2.35. Consulte [LINUX.md](LINUX.md) para as bibliotecas gráficas e a verificação do download.

## Identidade e visualização

O ícone fornecido pelo autor aparece no cabeçalho, na janela e na aba Sobre. `assets/icons` contém PNGs de 16, 20, 24, 32, 40, 48, 64, 96, 128, 192, 256, 512 e 1024 pixels, além de ICO multirresolução e ICNS. O ICO revisado pelo autor foi preservado em `assets/icon_source.ico` e é usado diretamente no executável. Suas camadas nativas são usadas quando disponíveis. Os PNGs maiores são redimensionamentos da camada de 256 px, sem criação de detalhes; o enquadramento original é mantido.

Na aba **Visualização**, escolha tema claro/escuro, idioma e efeitos. **Gradientes e brilho** controla o acabamento neon. **Animar nome e controles** controla a formação periódica do título em pixels e as transições de brilho dos botões e barras de rolagem. A animação também pausa quando a janela está inativa/minimizada ou durante uma tarefa. As preferências ficam no registro do Windows (QSettings: Bugzinho/Framosik) ou na configuração do usuário em outros sistemas.

Idiomas da interface: português, inglês, espanhol, francês, alemão, italiano, japonês, coreano, chinês simplificado e russo. Traduções são locais e podem precisar de revisão por falantes nativos. Detalhes técnicos de exceções/relatórios podem permanecer em português ou inglês. Diálogos nativos de arquivo seguem o idioma do sistema operacional.

A aba **Sobre** contém os links:
- Repositório: https://github.com/cleitinhodev/framosik
- Site: https://www.bugzinho.com/
- Apoio: https://www.bugzinho.com/donate

## Primeiro teste

- Abra `examples/demo_vertical.gif`.
- Mantenha frames **1 a 37**, passo **1**, resolução **100%**, movimento **Livre**, mesclagem **Preservar existente**.
- Clique em **Montar imagem** e depois em **Exportar PNG**.
- A imagem deverá ter **480 × 1080 px**, correspondente a `examples/resultado_esperado.png`.

O exemplo é uma ilustração sintética própria, estática, com deslocamento vertical conhecido. Não substitui testes em vídeos reais de anime.

## Como usar em uma cena real

1. Abra um GIF, MP4, MKV, AVI, MOV ou WebM. A disponibilidade de codecs depende do backend OpenCV; H.264/MP4 costuma ser uma boa entrada. WebP animado e imagens estáticas também são aceitos.
2. Navegue pela barra ou pelos botões quadro a quadro. Os números da interface começam em **1**.
3. No ponto inicial, use **Marcar início**. No final do movimento, use **Marcar fim**. Não inclua cortes para outra cena.
4. Comece com passo 1, modo Livre e Preservar existente. Para uma subida reta, experimente Somente vertical.
5. Monte a imagem. A aba de resultado permite zoom com a roda e navegação arrastando.
6. Exporte o PNG. Áreas sem pixels ficam transparentes; não há preenchimento inventado. O relatório JSON é opcional e registra ajustes, deslocamentos e frames aceitos/rejeitados.

## Parâmetros

| Controle | Efeito |
|---|---|
| Primeiro/último frame | Intervalo inclusivo. Um único frame também pode ser exportado. |
| Usar a cada N frames | 1 analisa todos. 2, 3… aceleram, mas podem perder a sobreposição. O último frame sempre é incluído. |
| Movimento | Translação livre X/Y ou restrita ao eixo vertical/horizontal. Novo modo **Zoom + X/Y (experimental)** para aproximação/afastamento gradual. Não corrige rotação ou perspectiva. |
| Resolução de trabalho | Reduz os frames antes da montagem. 50% reduz largura e altura pela metade, inclusive na imagem exportada. |
| Similaridade mínima | Correlação dos pixels compartilhados; não é probabilidade. Aumente para rejeitar montagens duvidosas. Reduzir demais pode juntar cenas erradas. |
| Sobreposição mínima | Parcela mínima do frame que precisa estar em comum. Se falhar, tente passo menor. |
| Limite da imagem | Proteção pelo número de pixels da tela final, não um limite absoluto de RAM. Padrão: 24 megapixels. |
| Preservar existente | Mantém o que já está montado e acrescenta apenas pixels em regiões ainda vazias. Mais fiel à sua proposta. |
| Suavizar emendas | Mescla uma faixa próxima à borda da área nova. O restante da imagem anterior é conservado. |
| Média na sobreposição | Média de 50% com o frame anterior na região compartilhada. É uma média incremental, não a média uniforme de todos os frames. Pode criar fantasmas em partes animadas. |
| Faixa de suavização | Largura aproximada em pixels de trabalho. Só se aplica a Suavizar emendas. |
| Recortar bordas | Remove margens fixas antes do alinhamento: útil para legendas, logos e barras pretas. Medidas na imagem original. A prévia da origem continua sem recorte. |
| Pular frames não alinhados | Tenta o próximo frame contra o último aceito. Desmarcado, interrompe e permite exportar a montagem parcial. |

Cancelamento é cooperativo: termina o processamento do frame atual e conserva o resultado parcial. Carregamento/exportação não são canceláveis. Enquanto há uma tarefa ativa, a janela aguarda seu término para fechar. A reprodução usa duração por frame no GIF; vídeo usa FPS nominal e não reproduz áudio.

## Como funciona

1. Lê um frame por vez, aplica recorte e escala.
2. Localiza detalhes semelhantes por SIFT e filtra correspondências inconsistentes com RANSAC.
3. Estima a **translação** entre o frame atual e o último aceito. No modo Zoom + X/Y, estima também uma escala uniforme usando detalhes SIFT; nos modos de translação, correlação de fase oferece uma segunda estimativa.
4. Valida a semelhança na área sobreposta e escolhe a melhor estimativa.
5. Compõe a transformação com a do último frame aceito e expande a tela apenas quando necessário, inclusive para coordenadas negativas.
6. Insere a área nova e aplica o modo de mesclagem escolhido.

Nos modos sem zoom, os deslocamentos são arredondados para pixels inteiros para preservar o traço sem reamostragem em cada passo. Os detalhes para alinhamento são analisados em uma resolução limitada; a exportação usa a resolução de trabalho escolhida. A máscara alpha distingue preto legítimo de área vazia.

## Limitações conhecidas

- Melhor resultado: ilustração parada e câmera apenas deslizando. Movimentos do corpo, cabelo e fundo podem causar emendas.
- O modo Zoom + X/Y corrige escala uniforme gradual (0,5–2× por par, 0,05–20× acumulada), com detalhes suficientes e sobreposição. Cada frame original é reamostrado uma vez para a escala do primeiro frame; não recupera detalhes perdidos no vídeo. Rotação, perspectiva e parallax não são corrigidos. O algoritmo pode interromper nesses casos ou, se o limiar estiver baixo, produzir alinhamento imperfeito.
- Áreas lisas/repetitivas podem impedir o alinhamento. A similaridade não garante uma correspondência correta.
- Pode acumular erro em sequências longas. Não há otimização global nem editor manual de emendas nesta primeira versão.
- GIF perde cores por sua própria paleta; vídeo comprimido pode trazer ruído. Não há super-resolução.
- Vídeos com taxa variável usam índices de decodificação e FPS nominal; não há edição por timecode preciso.
- O arquivo inteiro não fica na RAM, mas a imagem final, máscaras e cópias temporárias ocupam memória. Use 50% e limite menor para cenas grandes.
- Transparência do arquivo de origem é mantida no modo preservar; a mesclagem foi pensada principalmente para frames opacos de anime.

## Executar o código-fonte

Recomendado: Python **3.12 x64**. No Windows, `INICIAR_WINDOWS.bat` cria um ambiente local e instala as dependências na primeira execução (precisa de internet). Ou use:

```sh
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

No Linux, Qt exige as bibliotecas gráficas da distribuição. Em ambiente sem tela, os testes podem usar `QT_QPA_PLATFORM=offscreen`.

## Gerar uma distribuição no Windows

Execute `BUILD_WINDOWS.bat` com Python 3.12 x64 instalado. O script `build_tools/build_windows.py` inclui os assets, aplica o ICO e verifica o EXE com `--smoke-test`. Ele usa PyInstaller e produz `dist/Framosik/Framosik.exe`. Distribua **a pasta inteira**. Esse é um caminho alternativo à distribuição portátil com Python embutido entregue junto do projeto.

O iniciador da distribuição portátil está em `build_tools/launcher.c`. É um programa mínimo que encontra sua própria pasta e chama `runtime/pythonw.exe app/main.py`; não depende do diretório de trabalho e aceita caminhos com espaços/acentos. As instruções para reproduzir esse pacote estão em `build_tools/build_portable.py`.

## Estrutura

- `main.py`: inicialização e registro de falhas.
- `gui.py`: interface e tarefas em segundo plano.
- `appearance.py`: temas e borda animada.
- `i18n.py`: dez catálogos de idioma.
- `app_info.py`: versão, caminhos e links.
- `media.py`: leitura incremental de GIF/imagem/vídeo.
- `engine.py`: alinhamento, validação, tela e mesclagem.
- `tests/`: testes de algoritmo, entrada/saída e fluxo da interface.
- `examples/`: GIF sintético e resultado esperado.
- `build_tools/`: código do iniciador e empacotamento portátil.

## Testes

```sh
python -m pip install pytest
python -m pytest -q tests
```

Os testes cobrem deslocamento vertical, horizontal/diagonal, corte de cena, frames idênticos, modos de mesclagem, pixels pretos/transparência, seleção de intervalo, cancelamento, GIF, vídeo, limites e fluxo de carregar/montar/exportar pela interface.

## Dependências e autoria

A aplicação é um código novo entregue para você desenvolver e renomear. Nenhuma licença de publicação foi escolhida para o código da aplicação; o repositório inicial é privado. Dependências mantêm suas próprias licenças; consulte `THIRD_PARTY.md` e os arquivos de licença distribuídos junto dos pacotes.

## Zoom / afastamento (0.3.0)

Em **Alinhamento → Movimento**, selecione **Zoom + X/Y (experimental)**. Comece com passo 1 e mesclagem **Preservar existente**; escolha o intervalo de uma mesma cena estática. O modo funciona nos dois sentidos e aceita deslocamento simultâneo. A resolução do primeiro frame é a referência; começar pelo enquadramento mais próximo pode preservar mais detalhe, mas aumenta o tamanho da montagem. O limite em megapixels é verificado antes da transformação. O relatório JSON registra escala relativa, acumulada e matriz por frame aceito. Frames rejeitados não alteram a referência.

A versão v0.2.0 permanece disponível com seu código e executável originais como ponto de retorno.
