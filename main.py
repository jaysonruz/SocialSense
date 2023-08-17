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
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from uvicorn import Config, Server

from services.apify_instagram import scrape_instagram_data
from services.caption_fixer import fix_my_cap
# from services.convert_image_to_blob import convert_image_to_blob
from services.Imagedownloader import download_image

import pathlib
HOME_DIR = pathlib.Path(__file__).parent.resolve()
STATIC_IMAGES_DIR = HOME_DIR/"imgs"
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

# Define the table for saved Instagram posts
tb_saved_ig_posts = sqlalchemy.Table(
    "ig_posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String(255), primary_key=True),
    sqlalchemy.Column("caption", sqlalchemy.String(1000), nullable=False),
    sqlalchemy.Column("displayUrl_hosted", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("url", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("correction_results", sqlalchemy.String(1000), nullable=False),
    sqlalchemy.Column("helpful", sqlalchemy.Boolean, nullable=False),
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

class SavedIgPost(BaseModel):
    id: str
    caption: str
    displayUrl_hosted: str
    url:str
    correction_results: str
    helpful: bool
#----------------------------------------------------------------------------------------------#
#------------------------------------------FASTAPI---------------------------------------------#
server_address="http://192.168.2.172"
# server_address="http://192.168.1.143"

origins = [
    "http://127.0.0.1:8000",  # This is the default FastAPI server origin
    "chrome-extension://cdpjgindfjcedmeikjnahnkbpgfkbmpe",  # Replace with your Chrome extension's origin
    "chrome-extension://anpppboobkdbncaffjiopmjplenamine"
]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI() 

app.mount("/imgs", StaticFiles(directory="imgs"), name='images')

# Add the CORS middleware with allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # [print(x) for x in scrape_instagram_data("nike")] #testing 
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

def create_access_token(user):
    try:
        payload = {"sub": user["id"], "exp": datetime.utcnow() + timedelta(minutes=15)}
        return jwt.encode(payload, config('JWT_SECRET'), algorithm='HS256')
    except Exception as e:
        raise e

def create_refresh_token(user):
    try:
        payload = {"sub": user["id"], "exp": datetime.utcnow() + timedelta(days=30)}
        return jwt.encode(payload, config('JWT_REFRESH_SECRET'), algorithm='HS256')
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
    
    access_token = create_access_token(db_user)
    refresh_token = create_refresh_token(db_user)
    
    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@app.post("/instagram_posts")
def fetch_instagram_posts(ig_id: InstagramPostRequest):
    result = []
    ig_posts= scrape_instagram_data(instagram_id=ig_id.instagram_id,all_posts=False)
    # returns array of dict
    for post in ig_posts:
        print(f"DEBUG: processing {post['id']}")
        try:
            gingered_op = fix_my_cap(post['caption'])
            post['any_corrections']= len(gingered_op["corrections"]) > 0
            post['total_errors']=len(gingered_op["corrections"])
            post['correction_results']=gingered_op["result"]
            post['corrections_list']=gingered_op["corrections"]
            
            # dowload img and serve it from local
            file_name = f"{post['id']}.jpg" 
            img_save_path = str(STATIC_IMAGES_DIR/file_name)
            download_image(url=post['displayUrl'],save_path=img_save_path)
            post["displayUrl_hosted"]=f"{server_address}/imgs/{file_name}"

            result.append(post)
        except:
            print("ERROR: fields like caption not found in post: {post}")
            continue
    return result

@app.post("/save_ig_posts")
async def save_ig_posts(saved_post: SavedIgPost):
    try:
        # Prepare the values to be inserted into the database
        values = {
            "id": saved_post.id,
            "caption": saved_post.caption,
            "displayUrl_hosted": saved_post.displayUrl_hosted,
            "url":saved_post.url,
            "correction_results": saved_post.correction_results,
            "helpful": saved_post.helpful,
        }
        
        print("DEBUG: ",values)
        # Insert the values into the database
        query = tb_saved_ig_posts.insert().values(**values)
        await database.execute(query)

        print("\nDEBUG: Instagram post saved successfully:", values)  # Print success message

        return {"message": "Instagram post saved successfully"}
    except Exception as e:
        return {"error": str(e)}

#-----------------------------------------------------------------------------------------------#