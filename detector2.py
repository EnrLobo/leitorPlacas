import cv2
import easyocr
import os
import numpy as np
import database  # Importa o módulo do banco de dados

# --- 1. CONFIGURAÇÃO INICIAL ---
cascade_path = 'haarcascade_russian_plate_number.xml'
image_path = 'oficial.png' 

print("Carregando modelo EasyOCR...")
reader = easyocr.Reader(['en'], gpu=False)
print("Modelo carregado.")

# --- FUNÇÃO DE CORREÇÃO
def corrigir_placa(texto):
    # Limpa caracteres indesejados
    texto = texto.replace("-", "").replace(" ", "").replace(".", "").upper()
    
    # Se não tiver 7 caracteres, retorna o original
    if len(texto) != 7:
        return texto

    chars = list(texto)

    # Dicionários de conversão visual
    letra_para_numero = {
        'O': '0', 'Q': '0', 'D': '0',
        'Z': '2',
        'I': '1', 'L': '1', 'T': '1',
        'B': '8',
        'S': '5',
        'G': '6',
        'Y': '9'
    }
    
    numero_para_letra = {
        '0': 'O',
        '2': 'Z',
        '1': 'I',
        '8': 'B',
        '5': 'S',
        '6': 'G',
        '4': 'A'
    }

    # --- REGRA MERCOSUL: L L L N L N N ---
    # Posições que DEVEM ser LETRAS: 0, 1, 2, 4
    for i in [0, 1, 2, 4]:
        char_atual = chars[i]
        if char_atual in numero_para_letra:
            chars[i] = numero_para_letra[char_atual]
        elif char_atual == 'K':
            chars[i] = 'R'

    # Posições que DEVEM ser NÚMEROS: 3, 5, 6
    for i in [3, 5, 6]:
        char_atual = chars[i]
        if char_atual in letra_para_numero:
            chars[i] = letra_para_numero[char_atual]

    return "".join(chars)

# --- 2. CARREGAR OS ARQUIVOS ---
if not os.path.exists(cascade_path):
    print(f"[ERRO] Arquivo do classificador não encontrado em: {cascade_path}")
    exit()
if not os.path.exists(image_path):
    print(f"[ERRO] Imagem de teste não encontrada em: {image_path}")
    exit()

plate_cascade = cv2.CascadeClassifier(cascade_path)
img = cv2.imread(image_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

# --- 3. DETECTAR PLACAS ---
plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
print(f"Placas detectadas: {len(plates)}")

# --- 4. PROCESSAR PLACAS ---
for (x, y, w, h) in plates:
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    plate_roi_full = gray[y:y+h, x:x+w]
    full_height, full_width = plate_roi_full.shape
    
    # Cortes (Crop)
    crop_y_start = int(full_height * 0.40) 
    plate_roi_v_cropped = plate_roi_full[crop_y_start:full_height, :]
    current_height, current_width = plate_roi_v_cropped.shape
    crop_x_start = int(current_width * 0.15) 
    plate_roi = plate_roi_v_cropped[:, crop_x_start:current_width]
    
    # Processamento de imagem
    width = int(plate_roi.shape[1] * 2)
    height = int(plate_roi.shape[0] * 2)
    plate_roi_resized = cv2.resize(plate_roi, (width, height), interpolation=cv2.INTER_CUBIC)
    plate_roi_blurred = cv2.GaussianBlur(plate_roi_resized, (3, 3), 0)
    (thresh_val, plate_roi_processed) = cv2.threshold(plate_roi_blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # --- 5. LER COM EASYOCR ---
    try:
        final_ocr_image = plate_roi_processed
        
        allow_list = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        results = reader.readtext(final_ocr_image, allowlist=allow_list, detail=0, paragraph=False)
        
        if results:
            text_raw = "".join(results).upper().replace(" ", "")
            print(f"Leitura Original: {text_raw}")
            
            # --- APLICA A CORREÇÃO ---
            text_fixed = corrigir_placa(text_raw)
            print(f"Leitura Corrigida: {text_fixed}")
            
            # --- INTEGRAÇÃO COM BANCO DE DADOS (NOVO) ---
            # 1. Busca no banco para saber quem é
            info_veiculo = database.buscar_veiculo(text_fixed)
            
            cor_texto = (0, 255, 0) # Verde (Padrão)
            mensagem_status = "DESCONHECIDO"

            if info_veiculo:
                # Se achou no banco, verifica o status
                tipo = info_veiculo['tipo']
                status = info_veiculo['status']
                proprietario = info_veiculo['proprietario']
                
                mensagem_status = f"{tipo} | {status}"
                print(f"Veículo Identificado: {proprietario} - {status}")
                
                # Req. 7: Gerar alertas para não autorizados
                if status == 'PROIBIDO':
                    cor_texto = (0, 0, 255) # Texto Vermelho na tela!
                    print("ALERTA: VEÍCULO PROIBIDO TENTANDO ACESSAR!")
                
                # Req. 4: Registrar no banco
                database.registrar_acesso(text_fixed)
            else:
                print("Veículo não cadastrado no sistema.")
            
            # Escreve na imagem
            texto_tela = f"{text_fixed} ({mensagem_status})"
            cv2.putText(img, texto_tela, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor_texto, 2)
        else:
            print("EasyOCR não encontrou texto.")
    
    except Exception as e:
        print(f"Erro ao ler a placa: {e}")

# --- 6. EXIBIR ---
print("Pressione qualquer tecla para fechar...")
cv2.imshow('Imagem com Placas Detectadas', img)
cv2.waitKey(0)
cv2.destroyAllWindows()