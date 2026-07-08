import os
import shutil
import uuid
import cv2
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from deepface import DeepFace

app = FastAPI(title="Detector de Estresse API - By Bruno")

@app.get("/")
def home():
    return {"status": "Córtex pré-frontal online. Manda a foto."}

@app.post("/analisar")
async def analisar_rosto(file: UploadFile = File(...)):
    extensao = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    temp_file_path = f"temp_{uuid.uuid4()}.{extensao}"
    
    # Salva o arquivo que o Postman mandou
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # BLINDAGEM SÊNIOR: Verifica se o arquivo é uma imagem de verdade antes de chamar a IA
    img_teste = cv2.imread(temp_file_path)
    if img_teste is None:
        os.remove(temp_file_path)
        return JSONResponse(status_code=400, content={
            "erro": "O Postman te trollou! A imagem chegou vazia ou corrompida.",
            "diagnostico_gerais": "Mude o tipo da Key 'file' de 'Text' para 'File' no Postman e anexe a foto novamente."
        })

    try:
        # Chama a IA usando o motor SSD (agora blindado)
        analise = DeepFace.analyze(
            img_path=temp_file_path, 
            actions=['emotion'], 
            enforce_detection=True,
            detector_backend='mtcnn'
        )
        emocoes = analise[0]['emotion']
        
        # Nossa matemática agora faz o cast para o float nativo
        nivel_estresse = float(emocoes['angry']) + float(emocoes['fear']) + float(emocoes['sad']) + float(emocoes['disgust'])
        
        diagnostico = "Chassi blindado. Estresse baixo."
        if nivel_estresse > 40.0:
            diagnostico = "DIAGNÓSTICO: Você tá com cara de pinto murcho! Risco de crash no sistema."

        resultado = {
            "Tristeza": round(float(emocoes['sad']), 2),
            "Raiva": round(float(emocoes['angry']), 2),
            "Medo": round(float(emocoes['fear']), 2),
            "Nivel_Estresse_Total": round(nivel_estresse, 2),
            "Laudo": diagnostico
        }
        
        os.remove(temp_file_path)
        return JSONResponse(content=resultado)

    except ValueError as e:
        print(f"--> CRASH DO DEEPFACE (ValueError): {str(e)}")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return JSONResponse(status_code=400, content={"erro": "Rosto não detectado na imagem.", "detalhe_tecnico": str(e)})
    
    except Exception as e:
        print(f"--> CRASH GERAL FATAL: {str(e)}")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return JSONResponse(status_code=500, content={"erro": "O chassi fundiu o motor.", "detalhe_tecnico": str(e)})