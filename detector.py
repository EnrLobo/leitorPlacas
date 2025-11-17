import cv2
import pytesseract
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Tesseract-OCR\tesseract.exe'

cascade_path = 'haarcascade_russian_plate_number.xml'

image_path = 'teste.jpg'


if not os.path.exists(cascade_path):
    print(f"[ERRO] Arquivo do classificador não encontrado em: {cascade_path}")
    exit()
if not os.path.exists(image_path):
    print(f"[ERRO] Imagem de teste não encontrada em: {image_path}")
    exit()

plate_cascade = cv2.CascadeClassifier(cascade_path)
image = cv2.imread(image_path)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

print(f"Placas detectadas: {len(plates)}")


for (x, y, w, h) in plates:
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    plate_roi = gray[y:y+h, x:x+w]
    
    _, plate_roi_processed = cv2.threshold(plate_roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

config = "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
try:
        text = pytesseract.image_to_string(plate_roi_processed, config=config, lang='eng') # Usamos 'eng' pois 'por' pode confundir com acentos
        
        # Limpar o texto (remover quebras de linha, espaços)
        text = "".join(filter(str.isalnum, text)).upper()
        
        print(f"Texto da placa: {text}")
        
        # Colocar o texto lido na imagem
        cv2.putText(img, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
except Exception as e:
        print(f"Erro ao ler a placa: {e}")

print("Pressione qualquer tecla para fechar...")
cv2.imshow('Imagem com Placas Detectadas', img)
#cv2.imshow('Placa Processada', plate_roi_processed) # Descomente para ver o pré-processamento
cv2.waitKey(0)
cv2.destroyAllWindows()