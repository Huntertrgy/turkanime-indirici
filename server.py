import os
from fastapi import FastAPI
import uvicorn

app = FastAPI()

# Eğer 'PORT' ortam değişkeni varsa, onu al. Yoksa 8080'i kullan.
port = int(os.getenv("PORT", 8080))  # Default port 8080

# Uygulama başlatma işlemi
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)
