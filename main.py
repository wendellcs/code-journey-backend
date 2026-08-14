from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os 
import sys
from routers import classes, technologies, students, general

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

app = FastAPI()
load_dotenv()

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

DEV_ORIGIN = os.getenv('DEV_ORIGIN')
PROD_ORIGIN = os.getenv('PROD_ORIGIN')

origins_list = [DEV_ORIGIN, PROD_ORIGIN]

ALLOWED_ORIGINS = [url for url in origins_list if url]



app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(general.router)
app.include_router(classes.router)
app.include_router(technologies.router)
app.include_router(students.router)