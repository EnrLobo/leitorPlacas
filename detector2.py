import cv2
import easyocr # Importa o novo leitor
import os
import numpy as np

# --- 1. CONFIGURAÇÃO INICIAL ---
# (Sem mudanças aqui)
cascade_path = 'haarcascade_russian_plate_number.xml'
image_path = 'teste3.png' # Mantenha a imagem do fusca

print("Carregando modelo EasyOCR...")
reader = easyocr.Reader(['en', 'pt'], gpu=False) 
print("Modelo carregado.")

# --- 2. CARREGAR OS ARQUIVOS ---
# (Sem mudanças aqui)
if not os.path.exists(cascade_path):
    print(f"[ERRO] Arquivo do classificador não encontrado em: {cascade_path}")
    exit()
if not os.path.exists(image_path):
    print(f"[ERRO] Imagem de teste não encontrada em: {image_path}")
    exit()

plate_cascade = cv2.CascadeClassifier(cascade_path)
img = cv2.imread(image_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

# --- 3. DETECTAR PLACAS (REQ. 1 - PARTE 1) ---
# (Sem mudanças aqui)
plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
print(f"Placas detectadas: {len(plates)}")

# --- 4. PROCESSAR CADA PLACA ENCONTRADA ---
# (Ajuste de CROP aqui)
for (x, y, w, h) in plates:
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    # Recorta a região da placa (com a barra "BRASIL" inclusa)
    plate_roi_full = gray[y:y+h, x:x+w]
    
    # --- NOVO PASSO: CORTAR A PARTE DE CIMA (O "BRASIL") ---
    full_height = plate_roi_full.shape[0]
    # Define o ponto de corte (ignora os 40% de cima)
    crop_y_start = int(full_height * 0.40) 
    
    # Nosso novo ROI é só a parte de baixo da placa
    plate_roi = plate_roi_full[crop_y_start:full_height, :]
    # ----------------------------------------------------
    
    # Pré-processamento (agora feito na imagem CORTADA)
    width = int(plate_roi.shape[1] * 2)
    height = int(plate_roi.shape[0] * 2)
    plate_roi_resized = cv2.resize(plate_roi, (width, height), interpolation=cv2.INTER_CUBIC)
    plate_roi_blurred = cv2.GaussianBlur(plate_roi_resized, (3, 3), 0)
    
    # Binarização Otsu
    (thresh_val, plate_roi_processed) = cv2.threshold(
        plate_roi_blurred, 
        0, 
        255, 
        cv2.THRESH_BINARY + cv2.THRESH_OTSU 
    )

    # --- 5. LER O TEXTO DA PLACA (COM EASYOCR) ---
    
    try:
        # A imagem que o EasyOCR vai ler (agora só tem o número)
        final_ocr_image = plate_roi_processed
        
        # A nova janela vai mostrar uma imagem "cortada"
        cv2.imshow('Imagem Limpa CORTADA (Otsu)', final_ocr_image)
        
        allow_list = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        
        # --- MUDANÇA AQUI ---
        # paragraph=False: Retorna cada pedaço de texto em uma lista
        results = reader.readtext(final_ocr_image, 
                                  allowlist=allow_list, 
                                  detail=0,
                                  paragraph=False) # Mudado para False
        
        # -------------------

        if results:
            # Junta todos os pedaços de texto que ele encontrar
            text = "".join(results).upper().replace(" ", "")
            
            print(f"Texto da placa (Processado): {text}")
            
            # Colocar o texto lido na imagem original
            cv2.putText(img, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            print("EasyOCR não encontrou texto.")
    
    except Exception as e:
        print(f"Erro ao ler a placa com EasyOCR: {e}")

# --- 6. EXIBIR O RESULTADO ---
# (Sem mudanças aqui)
print("Pressione qualquer tecla para fechar...")
cv2.imshow('Imagem com Placas Detectadas', img)
cv2.waitKey(0)
cv2.destroyAllWindows()