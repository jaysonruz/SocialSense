from datetime import datetime, timedelta
from typing import Optional
import databases
import enum
import jwt
import sqlalchemy
from h11._abnf import status_code
from pydantic import BaseModel, validator
from fastapi import FastAPI, HTTPException, dependencies, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from decouple import config
from email_validator import validate_email as validate_e, EmailNotValidError
from passlib.context import CryptContext
from starlette.requests import Request

from services.apify_instagram import scrape_instagram_data
from services.caption_fixer import fix_my_cap

#-----------------------------------------DATABASES------------------------------------------#

DATABASE_URL = f"{config('DATABASE_URL')}"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

#---------------------------------------------------------------------------------------------#
#-----------------------------------------MODELS----------------------------------------------#

class UserRole(enum.Enum):
    super_admin = "super admin"
    admin = "admin"
    user = "user"

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String(120), unique=True),
    sqlalchemy.Column("password", sqlalchemy.String(255)),
    sqlalchemy.Column("full_name", sqlalchemy.String(200)),
    sqlalchemy.Column("phone", sqlalchemy.String(13)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False, 
                      server_default=sqlalchemy.func.now()),
    sqlalchemy.Column(
        "last_modified_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
    sqlalchemy.Column("role", sqlalchemy.Enum(UserRole), nullable=False, 
                      server_default=UserRole.user.name),
)

class social_media_categories(enum.Enum):
    Instagram = "Instagram"
    Twitter = "Twitter"
    Facebook = "Facebook"


user_subscriptions = sqlalchemy.Table(
    "user_subscriptions",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("sm_category",sqlalchemy.Enum(social_media_categories),nullable=False),
    sqlalchemy.Column("sm_handle",sqlalchemy.String(50),nullable=False),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"),nullable=False, index=True),
)

#----------------------------------------------------------------------------------------------#
#------------------------------------------FASTAPI---------------------------------------------#

app = FastAPI() 

@app.on_event("startup")
async def startup():
    # [print(x) for x in scrape_instagram_data("nike")] #testing 
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    
#-----------------------------------------------------------------------------------------------#
#--------------------------------------------ROUTES---------------------------------------------#

#-----------------------------------------------------------------------------------------------#