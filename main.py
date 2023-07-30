from datetime import datetime, timedelta
from typing import Optional
import databases
import enum
import jwt
import sqlalchemy
from h11._abnf import status_code
from pydantic import BaseModel, validator,EmailStr
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

tb_users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String(120), unique=True),
    sqlalchemy.Column("password", sqlalchemy.String(255)),
    sqlalchemy.Column("first_name", sqlalchemy.String(20),nullable=False),
    sqlalchemy.Column("Last_name", sqlalchemy.String(20),nullable=False),
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


tb_user_subscriptions = sqlalchemy.Table(
    "user_subscriptions",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("sm_category",sqlalchemy.Enum(social_media_categories),nullable=False),
    sqlalchemy.Column("sm_handle",sqlalchemy.String(50),nullable=False),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"),nullable=False, index=True),
)

#----------------------------------------------------------------------------------------------#
#------------------------------------------VALIDATORS------------------------------------------#
class BaseUser(BaseModel):
    email: EmailStr
    first_name: str
    Last_name:str
        
    @validator('first_name')
    def validate_name(cls, v):
        if len(v) < 3:
            raise ValueError("The name should be at least 3 characters long.")
        return v
    
    @validator('Last_name')
    def validate_name(cls, v):
        if len(v) < 3:
            raise ValueError("The name should be at least 3 characters long.")
        return v
    

class UserRegIn(BaseUser):
    password: str

class UserRegOut(BaseUser):
    created_at: datetime
    last_modified_at: datetime

class UserSignIn(BaseModel):
    email: EmailStr
    password: str

class InstagramPostRequest(BaseModel):
    instagram_id: str

#----------------------------------------------------------------------------------------------#
#------------------------------------------FASTAPI---------------------------------------------#
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI() 

@app.on_event("startup")
async def startup():
    # [print(x) for x in scrape_instagram_data("nike")] #testing 
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

def create_access_token(user):
    try:
        payload = {"sub": user["id"], "exp": datetime.utcnow() + 
        timedelta(minutes=120)}
        return jwt.encode(payload, config('JWT_SECRET'),algorithm='HS256')
    except Exception as e:
        raise e

#-----------------------------------------------------------------------------------------------#
#--------------------------------------------ROUTES---------------------------------------------#
@app.post("/register", status_code=201, response_model=UserRegOut)
async def create_user(user: UserRegIn):
    user.password = pwd_context.hash(user.password)
    q = tb_users.insert().values(**user.dict())
    id_ = await database.execute(q)
    user = await database.fetch_one(tb_users.select().where(tb_users.c.id == id_))
    return user

@app.post("/login")
async def user_login(user: UserSignIn):
    # Retrieve user from the database based on the provided email
    query = tb_users.select().where(tb_users.c.email == user.email)
    db_user = await database.fetch_one(query)

    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Compare the provided password with the hashed password in the database
    if not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(db_user)
    
    return { "message": "Login successful",
             "token": token }


@app.post("/instagram_posts")
def fetch_instagram_posts(ig_id: InstagramPostRequest):
    ig_posts= scrape_instagram_data(instagram_id=ig_id.instagram_id,all_posts=False)
    return ig_posts



#-----------------------------------------------------------------------------------------------#