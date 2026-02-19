FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD streamlit run App.py --server.port=8501 --server.address=0.0.0.0