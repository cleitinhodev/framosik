"""Catálogos locais; nenhuma tradução ou dado de mídia é enviado à internet."""
LANGUAGES = {'pt':'Português (Brasil)', 'en':'English', 'es':'Español', 'fr':'Français',
             'de':'Deutsch', 'it':'Italiano', 'ja':'日本語', 'ko':'한국어', 'zh':'简体中文', 'ru':'Русский'}
# Ordem: português, inglês, espanhol, francês, alemão, italiano, japonês, coreano, chinês, russo.
ROWS = '''
finish|Acabamento|Finishing|Acabado|Finition|Nachbearbeitung|Finitura|仕上げ|마무리|后期调整|Обработка
seam_soft|Suavização|Smoothing|Suavizado|Lissage|Glättung|Levigatura|平滑化|부드럽게|平滑|Сглаживание
seam_color|Correção de cor local|Local color repair|Corrección de color local|Correction de couleur locale|Lokale Farbkorrektur|Correzione colore locale|局所色補正|국소 색상 보정|局部颜色修复|Коррекция цвета стыков
apply_finish|Aplicar à prévia|Apply to preview|Aplicar a la vista|Appliquer à l’aperçu|Vorschau anwenden|Applica all’anteprima|プレビューに適用|미리보기에 적용|应用到预览|Применить к просмотру
zoom_motion|Zoom + X/Y (experimental)|Zoom + X/Y (experimental)|Zoom + X/Y (experimental)|Zoom + X/Y (expérimental)|Zoom + X/Y (experimentell)|Zoom + X/Y (sperimentale)|ズーム + X/Y（実験的）|줌 + X/Y (실험적)|缩放 + X/Y（实验性）|Масштаб + X/Y (экспериментально)
open|Abrir GIF / vídeo|Open GIF / video|Abrir GIF / vídeo|Ouvrir GIF / vidéo|GIF / Video öffnen|Apri GIF / video|GIF / 動画を開く|GIF / 동영상 열기|打开 GIF / 视频|Открыть GIF / видео
subtitle|Reconstrua a cena, quadro a quadro.|Rebuild the scene, frame by frame.|Reconstruye la escena, cuadro a cuadro.|Reconstruisez la scène, image par image.|Die Szene Bild für Bild zusammensetzen.|Ricostruisci la scena, fotogramma per fotogramma.|フレームをつなぎ、シーンを再構成。|프레임을 이어 장면을 재구성하세요.|逐帧拼接，还原完整场景。|Соберите сцену кадр за кадром.
workspace|Montagem|Stitching|Montaje|Assemblage|Zusammensetzen|Unione|結合|합성|拼接|Сборка
view|Visualização|Appearance|Visualización|Affichage|Darstellung|Visualizzazione|表示|화면 설정|外观|Оформление
about|Sobre|About|Acerca de|À propos|Über|Informazioni|このアプリについて|정보|关于|О программе
interval|1 · Intervalo da cena|1 · Scene range|1 · Intervalo de escena|1 · Plage de la scène|1 · Szenenbereich|1 · Intervallo scena|1 · シーンの範囲|1 · 장면 범위|1 · 场景范围|1 · Диапазон сцены
first|Primeiro frame|First frame|Primer fotograma|Première image|Erstes Bild|Primo fotogramma|開始フレーム|첫 프레임|起始帧|Первый кадр
last|Último frame|Last frame|Último fotograma|Dernière image|Letztes Bild|Ultimo fotogramma|終了フレーム|마지막 프레임|结束帧|Последний кадр
step|Usar a cada N frames|Use every N frames|Usar cada N fotogramas|Utiliser toutes les N images|Jedes N-te Bild verwenden|Usa ogni N fotogrammi|N フレームごとに使用|N 프레임마다 사용|每 N 帧采样|Брать каждый N-й кадр
mark_start|Marcar início|Set start|Marcar inicio|Définir le début|Start markieren|Segna inizio|開始位置を設定|시작 지정|设为起点|Отметить начало
mark_end|Marcar fim|Set end|Marcar final|Définir la fin|Ende markieren|Segna fine|終了位置を設定|끝 지정|设为终点|Отметить конец
alignment|2 · Alinhamento|2 · Alignment|2 · Alineación|2 · Alignement|2 · Ausrichtung|2 · Allineamento|2 · 位置合わせ|2 · 정렬|2 · 对齐|2 · Выравнивание
movement|Movimento|Movement|Movimiento|Mouvement|Bewegung|Movimento|移動方向|이동 방향|移动方向|Движение
free|Livre (X e Y)|Free (X and Y)|Libre (X e Y)|Libre (X et Y)|Frei (X und Y)|Libero (X e Y)|自由 (X・Y)|자유 (X, Y)|自由（X 和 Y）|Свободное (X и Y)
vertical|Somente vertical|Vertical only|Solo vertical|Vertical uniquement|Nur vertikal|Solo verticale|縦方向のみ|세로만|仅垂直|Только по вертикали
horizontal|Somente horizontal|Horizontal only|Solo horizontal|Horizontal uniquement|Nur horizontal|Solo orizzontale|横方向のみ|가로만|仅水平|Только по горизонтали
resolution|Resolução de trabalho|Working resolution|Resolución de trabajo|Résolution de travail|Arbeitsauflösung|Risoluzione di lavoro|処理解像度|작업 해상도|工作分辨率|Рабочее разрешение
similarity|Similaridade mínima|Minimum similarity|Similitud mínima|Similarité minimale|Mindestähnlichkeit|Somiglianza minima|最小類似度|최소 유사도|最低相似度|Минимальное сходство
overlap|Sobreposição mínima|Minimum overlap|Solapamiento mínimo|Chevauchement minimal|Mindestüberlappung|Sovrapposizione minima|最小重複率|최소 겹침|最小重叠率|Минимальное перекрытие
limit|Limite da imagem|Image limit|Límite de imagen|Limite de l’image|Bildbegrenzung|Limite immagine|画像サイズ上限|이미지 크기 제한|图像大小上限|Лимит изображения
skip|Pular frames não alinhados|Skip unaligned frames|Omitir fotogramas no alineados|Ignorer les images non alignées|Nicht ausgerichtete Bilder überspringen|Salta fotogrammi non allineati|未整列フレームをスキップ|정렬 실패 프레임 건너뛰기|跳过未对齐的帧|Пропускать несопоставленные кадры
mixing|3 · Mesclagem|3 · Blending|3 · Mezcla|3 · Fusion|3 · Überblendung|3 · Fusione|3 · ブレンド|3 · 혼합|3 · 混合|3 · Смешивание
mode|Modo|Mode|Modo|Mode|Modus|Modalità|モード|모드|模式|Режим
preserve|Preservar existente|Preserve existing|Conservar existente|Conserver l’existant|Vorhandenes erhalten|Mantieni esistente|既存部分を保持|기존 영역 유지|保留已有区域|Сохранять существующее
feather|Suavizar emendas|Soften seams|Suavizar uniones|Adoucir les raccords|Übergänge glätten|Sfuma giunzioni|継ぎ目をぼかす|이음새 부드럽게|柔化接缝|Сглаживать стыки
average|Média na sobreposição|Average overlap|Promediar solapamiento|Moyenne du chevauchement|Überlappung mitteln|Media sovrapposizione|重複部分を平均化|겹친 영역 평균|重叠区域取平均|Усреднять перекрытие
feather_width|Faixa de suavização|Feather width|Ancho de suavizado|Largeur du fondu|Übergangsbreite|Larghezza sfumatura|ぼかし幅|혼합 너비|柔化宽度|Ширина сглаживания
crop|4 · Recortar bordas / legendas|4 · Crop borders / subtitles|4 · Recortar bordes / subtítulos|4 · Rogner bords / sous-titres|4 · Ränder / Untertitel beschneiden|4 · Ritaglia bordi / sottotitoli|4 · 枠・字幕を切り抜く|4 · 테두리 / 자막 자르기|4 · 裁剪边框 / 字幕|4 · Обрезка краёв / субтитров
left|Esquerda|Left|Izquierda|Gauche|Links|Sinistra|左|왼쪽|左|Слева
top|Topo|Top|Arriba|Haut|Oben|Alto|上|위|上|Сверху
right|Direita|Right|Derecha|Droite|Rechts|Destra|右|오른쪽|右|Справа
bottom|Base|Bottom|Abajo|Bas|Unten|Basso|下|아래|下|Снизу
crop_tip|Pixels na resolução original. A prévia permanece sem recorte.|Pixels at original resolution. Preview stays uncropped.|Píxeles a resolución original. La vista previa no se recorta.|Pixels à la résolution d’origine. Aperçu non rogné.|Pixel in Originalauflösung. Vorschau bleibt unbeschnitten.|Pixel alla risoluzione originale. Anteprima non ritagliata.|元の解像度のピクセル数。プレビューは切り抜かれません。|원본 해상도의 픽셀 수입니다. 미리보기는 잘리지 않습니다.|使用原始分辨率的像素值。预览不裁剪。|Пиксели исходного разрешения. Предпросмотр без обрезки.
original|Frame original|Original frame|Fotograma original|Image originale|Originalbild|Fotogramma originale|元のフレーム|원본 프레임|原始帧|Исходный кадр
result|Imagem montada|Stitched image|Imagen unida|Image assemblée|Zusammengesetztes Bild|Immagine unita|結合画像|합성 이미지|拼接图像|Собранное изображение
empty_source|Abra um GIF ou vídeo para começar|Open a GIF or video to start|Abre un GIF o vídeo para empezar|Ouvrez un GIF ou une vidéo|Zum Start GIF oder Video öffnen|Apri un GIF o video per iniziare|GIF または動画を開いてください|GIF 또는 동영상을 열어 시작하세요|打开 GIF 或视频以开始|Откройте GIF или видео
empty_result|A montagem aparecerá aqui|Your stitched image appears here|La imagen aparecerá aquí|L’assemblage apparaîtra ici|Hier erscheint das Ergebnis|Il risultato apparirà qui|結合結果がここに表示されます|합성 결과가 여기에 표시됩니다|拼接结果将在此显示|Результат появится здесь
fit|Ajustar à janela|Fit to window|Ajustar a ventana|Adapter à la fenêtre|An Fenster anpassen|Adatta alla finestra|ウィンドウに合わせる|창에 맞추기|适应窗口|По размеру окна
zoom|Zoom 100%|Zoom 100%|Zoom 100%|Zoom 100 %|Zoom 100 %|Zoom 100%|100% 表示|100% 확대|缩放 100%|Масштаб 100%
navigate|Roda: zoom · arraste: navegar|Wheel: zoom · drag: pan|Rueda: zoom · arrastrar: mover|Molette : zoom · glisser : déplacer|Mausrad: Zoom · ziehen: verschieben|Rotella: zoom · trascina: sposta|ホイール: 拡大 · ドラッグ: 移動|휠: 확대 · 드래그: 이동|滚轮缩放 · 拖动平移|Колесо: масштаб · перетаскивание: сдвиг
play|Reproduzir|Play|Reproducir|Lire|Abspielen|Riproduci|再生|재생|播放|Воспроизвести
pause|Pausar|Pause|Pausar|Pause|Pause|Pausa|一時停止|일시 정지|暂停|Пауза
frame|Frame|Frame|Fotograma|Image|Bild|Fotogramma|フレーム|프레임|帧|Кадр
stitch|Montar imagem|Stitch image|Unir imágenes|Assembler l’image|Bild zusammensetzen|Unisci immagini|画像を結合|이미지 합성|拼接图像|Собрать изображение
cancel|Cancelar|Cancel|Cancelar|Annuler|Abbrechen|Annulla|キャンセル|취소|取消|Отмена
export|Exportar PNG|Export PNG|Exportar PNG|Exporter PNG|PNG exportieren|Esporta PNG|PNG を保存|PNG 내보내기|导出 PNG|Экспорт PNG
report|Salvar relatório|Save report|Guardar informe|Enregistrer le rapport|Bericht speichern|Salva rapporto|レポートを保存|보고서 저장|保存报告|Сохранить отчёт
log|Progresso e avisos da montagem|Progress and stitching notices|Progreso y avisos|Progression et avertissements|Fortschritt und Hinweise|Avanzamento e avvisi|処理状況と通知|진행 상황 및 알림|进度和拼接提示|Ход работы и уведомления
theme|Tema|Theme|Tema|Thème|Design|Tema|テーマ|테마|主题|Тема
dark|Escuro|Dark|Oscuro|Sombre|Dunkel|Scuro|ダーク|어둡게|深色|Тёмная
light|Claro|Light|Claro|Clair|Hell|Chiaro|ライト|밝게|浅色|Светлая
language|Idioma|Language|Idioma|Langue|Sprache|Lingua|言語|언어|语言|Язык
gradients|Gradientes e brilho|Gradients and glow|Degradados y brillo|Dégradés et lueurs|Farbverläufe und Leuchten|Sfumature e bagliori|グラデーションと光彩|그라데이션 및 발광|渐变与辉光|Градиенты и свечение
animations|Animar nome e controles|Animate title and controls|Animar nombre y controles|Animer le titre et les commandes|Titel und Bedienelemente animieren|Anima titolo e controlli|タイトルと操作部のアニメーション|제목 및 컨트롤 애니메이션|为标题和控件启用动画|Анимация названия и элементов управления
appearance_note|As preferências são salvas automaticamente. Desative as animações para reduzir o movimento e o uso de CPU.|Preferences are saved automatically. Turn off animations to reduce motion and CPU use.|Las preferencias se guardan automáticamente. Desactiva las animaciones para reducir movimiento y uso de CPU.|Les préférences sont enregistrées automatiquement. Désactivez les animations pour réduire les mouvements et l’utilisation du processeur.|Einstellungen werden automatisch gespeichert. Animationen deaktivieren, um Bewegung und CPU-Last zu reduzieren.|Le preferenze vengono salvate automaticamente. Disattiva le animazioni per ridurre movimento e uso della CPU.|設定は自動保存されます。動きや CPU 使用量を減らすにはアニメーションを無効にしてください。|설정은 자동 저장됩니다. 애니메이션을 끄면 움직임과 CPU 사용량이 줄어듭니다.|偏好设置自动保存。关闭动画可减少动态效果和 CPU 使用量。|Настройки сохраняются автоматически. Отключите анимацию, чтобы уменьшить движение и нагрузку на процессор.
version|Versão|Version|Versión|Version|Version|Versione|バージョン|버전|版本|Версия
repository|Repositório|Repository|Repositorio|Dépôt|Repository|Repository|リポジトリ|저장소|代码仓库|Репозиторий
website|Site|Website|Sitio web|Site web|Website|Sito web|ウェブサイト|웹사이트|网站|Сайт
donate|Apoiar o projeto|Support the project|Apoyar el proyecto|Soutenir le projet|Projekt unterstützen|Sostieni il progetto|プロジェクトを支援|프로젝트 후원|支持项目|Поддержать проект
about_text|Transforme movimentos de câmera em uma imagem completa. Processamento local com Python, PySide6 e OpenCV, sem IA generativa.|Turn camera pans into a complete image. Local processing with Python, PySide6 and OpenCV, without generative AI.|Convierte movimientos de cámara en una imagen completa. Procesamiento local con Python, PySide6 y OpenCV, sin IA generativa.|Transformez les panoramiques en une image complète. Traitement local avec Python, PySide6 et OpenCV, sans IA générative.|Kameraschwenks zu einem vollständigen Bild verbinden. Lokale Verarbeitung mit Python, PySide6 und OpenCV, ohne generative KI.|Trasforma i movimenti di camera in un’immagine completa. Elaborazione locale con Python, PySide6 e OpenCV, senza IA generativa.|カメラの移動を一枚の画像に。Python、PySide6、OpenCV でローカル処理し、生成 AI は使用しません。|카메라 이동 장면을 하나의 이미지로 만드세요. 생성형 AI 없이 Python, PySide6, OpenCV로 로컬 처리합니다.|将镜头平移画面拼成完整图像。使用 Python、PySide6 和 OpenCV 本地处理，不使用生成式 AI。|Объединяйте панорамы в полное изображение. Локальная обработка на Python, PySide6 и OpenCV, без генеративного ИИ.
ready|Pronto · processamento local|Ready · local processing|Listo · procesamiento local|Prêt · traitement local|Bereit · lokale Verarbeitung|Pronto · elaborazione locale|準備完了 · ローカル処理|준비 완료 · 로컬 처리|就绪 · 本地处理|Готово · локальная обработка
mark_hint|Marque o início e o fim da mesma cena.|Mark the start and end of the same scene.|Marca el inicio y final de la misma escena.|Marquez le début et la fin de la même scène.|Anfang und Ende derselben Szene markieren.|Segna inizio e fine della stessa scena.|同じシーンの開始と終了を指定してください。|같은 장면의 시작과 끝을 지정하세요.|标记同一场景的起点和终点。|Отметьте начало и конец одной сцены.
failed|Não foi possível concluir. Consulte os detalhes.|Could not complete. See details.|No se pudo completar. Consulta los detalles.|Impossible de terminer. Consultez les détails.|Vorgang fehlgeschlagen. Details beachten.|Impossibile completare. Consulta i dettagli.|完了できませんでした。詳細を確認してください。|완료하지 못했습니다. 자세한 내용을 확인하세요.|无法完成。请查看详细信息。|Не удалось завершить. См. подробности.
details|Detalhes técnicos|Technical details|Detalles técnicos|Détails techniques|Technische Details|Dettagli tecnici|技術情報|기술 세부 정보|技术详情|Технические сведения
invalid|Revise o intervalo e os parâmetros.|Check the range and parameters.|Revisa el intervalo y los parámetros.|Vérifiez la plage et les paramètres.|Bereich und Parameter überprüfen.|Controlla intervallo e parametri.|範囲とパラメーターを確認してください。|범위와 매개변수를 확인하세요.|请检查范围和参数。|Проверьте диапазон и параметры.
processing|Processando|Processing|Procesando|Traitement|Verarbeitung|Elaborazione|処理中|처리 중|处理中|Обработка
accepted|aceitos|accepted|aceptados|acceptées|angenommen|accettati|採用|승인|已接受|принято
rejected|rejeitados|rejected|rechazados|rejetées|abgelehnt|rifiutati|不採用|거부|已拒绝|отклонено
completed|Concluído|Completed|Completado|Terminé|Abgeschlossen|Completato|完了|완료|已完成|Завершено
stopped|Interrompido|Stopped|Detenido|Interrompu|Angehalten|Interrotto|停止|중단됨|已停止|Остановлено
cancelled|Cancelado|Cancelled|Cancelado|Annulé|Abgebrochen|Annullato|キャンセル済み|취소됨|已取消|Отменено
partial|Resultado parcial preservado. Revise o trecho, o recorte e o passo entre frames.|Partial result preserved. Review the range, crop and frame step.|Resultado parcial conservado. Revisa el intervalo, recorte y paso.|Résultat partiel conservé. Vérifiez la plage, le recadrage et le pas.|Teilergebnis erhalten. Bereich, Zuschnitt und Bildschritt prüfen.|Risultato parziale conservato. Controlla intervallo, ritaglio e passo.|途中結果を保持しました。範囲、切り抜き、フレーム間隔を確認してください。|부분 결과가 유지되었습니다. 범위, 자르기, 프레임 간격을 확인하세요.|已保留部分结果。请检查范围、裁剪和帧间隔。|Частичный результат сохранён. Проверьте диапазон, обрезку и шаг кадров.
cancelling|Cancelando após o frame atual…|Cancelling after the current frame…|Cancelando tras el fotograma actual…|Annulation après l’image actuelle…|Abbruch nach dem aktuellen Bild…|Annullamento dopo il fotogramma attuale…|現在のフレーム処理後にキャンセル…|현재 프레임 처리 후 취소 중…|处理完当前帧后取消…|Отмена после текущего кадра…
saved|Arquivo salvo|File saved|Archivo guardado|Fichier enregistré|Datei gespeichert|File salvato|保存しました|파일 저장 완료|文件已保存|Файл сохранён
wait|Aguarde a tarefa terminar antes de fechar.|Wait for the task to finish before closing.|Espera a que termine la tarea antes de cerrar.|Attendez la fin de la tâche avant de fermer.|Vor dem Schließen auf das Ende der Aufgabe warten.|Attendi la fine dell’attività prima di chiudere.|処理が完了してから閉じてください。|작업이 끝난 후 닫아 주세요.|请等待任务结束后再关闭。|Перед закрытием дождитесь завершения задачи.
'''
CATALOGS = {code:{} for code in LANGUAGES}
for row in ROWS.strip().splitlines():
    key, *values = row.split('|')
    if len(values) != len(LANGUAGES):
        raise RuntimeError(f'Invalid translation row: {key}')
    for code, value in zip(LANGUAGES, values):
        CATALOGS[code][key] = value

def translate(key, language='pt'):
    return CATALOGS.get(language, CATALOGS['en']).get(key, key)
