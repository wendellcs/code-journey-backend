from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os 
from routers import classes, technologies, students, general

app = FastAPI()
load_dotenv()

ORIGIN = os.getenv('ORIGIN')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ORIGIN],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(general.router)
app.include_router(classes.router)
app.include_router(technologies.router)
app.include_router(students.router)