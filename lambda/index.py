# 必要なライブラリのインストール
!pip install fastapi nest_asyncio pyngrok uvicorn

import nest_asyncio
from pyngrok import ngrok
from fastapi import FastAPI, Request
import uvicorn

# Jupyter 対応パッチ
nest_asyncio.apply()

# アプリ作成
app = FastAPI()

@app.post("/predict")
async def predict(request: Request):
    data = await request.json()
    message = data.get("message", "")
    history = data.get("conversationHistory", [])

    # シンプルな応答（ここをモデル推論に差し替え可）
    response_text = f"Echo: {message}"

    # 会話履歴にアシスタントの応答を追加
    history.append({
        "role": "assistant",
        "content": response_text
    })

    return {
        "response": response_text,
        "conversationHistory": history
    }

# ngrok トンネル作成（公開URLが生成される）
public_url = ngrok.connect(8000)
print(f"Your ngrok URL is: {public_url}")

# UvicornでAPIサーバ起動
uvicorn.run(app, host="0.0.0.0", port=8000)
