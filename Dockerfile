FROM python:3.10-slim

# Instala as dependências gráficas essenciais do Linux
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# Atualiza o PIP e força a instalação pesada PRIMEIRO para evitar conflito de versão
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# O pulo do gato Sênior: Desinstala qualquer lixo de OpenCV padrão que o DeepFace tenha tentado socar junto
RUN pip uninstall -y opencv-python opencv-python-headless
# E garante que apenas a versão 'contrib' (com o módulo DNN) fique ativa
RUN pip install --no-cache-dir opencv-contrib-python-headless

# Puxa os pesos da IA ignorando o OpenCV na compilação inicial
RUN python -c "import numpy as np, cv2; cv2.imwrite('dummy.jpg', np.zeros((224, 224, 3), dtype=np.uint8)); from deepface import DeepFace; DeepFace.analyze('dummy.jpg', actions=['emotion'], enforce_detection=False, detector_backend='skip')"

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]