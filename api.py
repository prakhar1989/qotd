from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from transformers import AutoTokenizer, AutoModelWithLMHead, pipeline

## create the pipeline
tokenizer = AutoTokenizer.from_pretrained("nandinib1999/quote-generator")
model = AutoModelWithLMHead.from_pretrained("nandinib1999/quote-generator")
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

app = FastAPI()

class QuoteRequest(BaseModel):
    text: str

class QuoteResponse(BaseModel):
    text: str

### Serves the Model API to generate quote
@app.post("/generate", response_model=QuoteResponse)
async def generate(request: QuoteRequest):
    resp = generator(request.text)
    if not resp[0] and not resp[0]["generated_text"]:
        raise HTTPException(status_code=500, detail='Error in generation')
    return QuoteResponse(text=resp[0]["generated_text"])
