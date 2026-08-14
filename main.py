from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os 
from routers import classes, technologies, students, general

app = FastAPI()
load_dotenv()

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