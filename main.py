#pip install fastapi, uvicorn, python-multipart
#pip install aiofiles jinja2
#pip install websockets
#pip install python-dotenv (this is for adding a feature where you can store,retrieve environment vars)
#pip3 freeze > requirements.txt (create a requirement.txt file containing the libraries used in this project. You need this for production deployment)
#before running this script, make sure uvicorn is running
#to run uvicorn, on terminal, run uvicorn mainv2:app --reload

from openai import OpenAI
from fastapi import FastAPI, Form, Request, WebSocket
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv

app = FastAPI()
templates = Jinja2Templates(directory='templates')

chat_responses = []

@app.get("/",response_class=HTMLResponse)
async def chat_page(request:Request):
    return templates.TemplateResponse('home.html',{"request":request,"chat_responses":chat_responses})

load_dotenv()
openai = OpenAI(
    api_key = os.getenv("OPEN_AI_API_SECRET_KEY")
)

chat_log = [{'role':'system','content':'You are a university virtual assistant'}]

@app.websocket("/ws")
async def chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        user_input = await websocket.receive_text()
        chat_log.append({'role': 'user', 'content': user_input})
        chat_responses.append(user_input)

        try:
            response = openai.chat.completions.create(
                model='gpt-4o-mini',
                messages=chat_log,
                temperature=0.6,
                stream=True
            )
            ai_response = ''
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    ai_response += chunk.choices[0].delta.content
                    await websocket.send_text(chunk.choices[0].delta.content)

            chat_responses.append(ai_response)
        except Exception as e:
            await websocket.send_text(f'Error: {str(e)}')
            break


@app.post('/', response_class=HTMLResponse)
async def chat(request: Request, user_input: Annotated[str, Form()]):

    chat_log.append({'role':'user','content':user_input})
    chat_responses.append(user_input)
    response = openai.chat.completions.create(
        model='gpt-4o-mini',
        messages=chat_log,
        temperature=0.6
    )

    bot_response = response.choices[0].message.content
    chat_log.append({'role':'assistant','content':bot_response})
    chat_responses.append(bot_response)
    #return  bot_response
    return templates.TemplateResponse("home.html", {"request": request, "chat_responses":chat_responses})

#for Dalle
@app.get('/image',response_class=HTMLResponse)
async def image_page(request:Request):
    return templates.TemplateResponse("image.html",{"request":request})


@app.post('/image',response_class=HTMLResponse)
async def create_image(request: Request, user_input: Annotated[str, Form()]):
    response = openai.images.generate(
        prompt=user_input,
        n=1,
        size='512x512'
    )

    image_url = response.data[0].url
    return templates.TemplateResponse("image.html",{"request":request, "image_url":image_url})
