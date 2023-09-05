from datetime import datetime, timedelta
from typing import Optional
import databases
import enum
import jwt
import sqlalchemy
from pydantic import BaseModel, validator, EmailStr
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from decouple import config
from email_validator import validate_email as validate_e, EmailNotValidError
from passlib.context import CryptContext
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from uvicorn import Config, Server

from services.apify_instagram import scrape_instagram_data
from services.caption_fixer import fix_my_cap
from services.Imagedownloader import download_image

import pathlib
HOME_DIR = pathlib.Path(__file__).parent.resolve()
STATIC_IMAGES_DIR = HOME_DIR / "imgs"

# -----------------------------------------DATABASES------------------------------------------#

DATABASE_URL = f"{config('DATABASE_URL')}"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# ---------------------------------------------------------------------------------------------#
# -----------------------------------------MODELS----------------------------------------------#

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
    sqlalchemy.Column("first_name", sqlalchemy.String(20), nullable=False),
    sqlalchemy.Column("Last_name", sqlalchemy.String(20), nullable=False),
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
    sqlalchemy.Column("sm_category", sqlalchemy.Enum(social_media_categories), nullable=False),
    sqlalchemy.Column("sm_handle", sqlalchemy.String(50), nullable=False),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False, index=True),
)

# Define the table for saved Instagram posts
tb_saved_ig_posts = sqlalchemy.Table(
    "ig_posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("post_id", sqlalchemy.String(255), nullable=False),  # made primary-key false
    sqlalchemy.Column("ownerUsername", sqlalchemy.String(100), nullable=False),
    sqlalchemy.Column("extensionId", sqlalchemy.String(100), nullable=False),  # extension id
    sqlalchemy.Column("caption", sqlalchemy.String(1000), nullable=False),
    sqlalchemy.Column("displayUrl_hosted", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("url", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("correction_results", sqlalchemy.String(1000), nullable=False),
    sqlalchemy.Column("helpful", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("dismiss", sqlalchemy.Boolean, nullable=False, server_default=sqlalchemy.sql.expression.false()),
    sqlalchemy.Column(
        "updated_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
)

# ---------------------------------------------------------------------------------------------#
# ------------------------------------------VALIDATORS------------------------------------------#

class BaseUser(BaseModel):
    email: EmailStr
    first_name: str
    Last_name: str

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
    post_id: str
    ownerUsername: str
    extensionId: str
    caption: str
    displayUrl_hosted: str
    url: str
    correction_results: str
    helpful: bool
    dismiss: bool

# ---------------------------------------------------------------------------------------------#
# ------------------------------------------FASTAPI---------------------------------------------#

server_address = "http://192.168.2.172"
# server_address = "http://192.168.1.143"

origins = [
    "http://127.0.0.1:8000",  # This is the default FastAPI server origin
    "chrome-extension://cdpjgindfjcedmeikjnahnkbpgfkbmpe",  # Replace with your Chrome extension's origin
    "chrome-extension://anpppboobkdbncaffjiopmjplenamine"
]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI()

# -----------------------------------------TOKEN SETTINGS----------------------------------------#

SECRET_KEY = config('JWT_SECRET')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# -----------------------------------DEPENDENCIES AND MIDDLEWARES---------------------------------#

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token validation error")

app.mount("/imgs", StaticFiles(directory="imgs"), name='images')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------STARTUP AND SHUTDOWN EVENTS---------------------------------#

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# --------------------------------------------ROUTES---------------------------------------------#

@app.post("/register", status_code=201, response_model=UserRegOut)
async def create_user(user: UserRegIn):
    user.password = pwd_context.hash(user.password)
    q = tb_users.insert().values(**user.dict())
    id_ = await database.execute(q)
    user = await database.fetch_one(tb_users.select().where(tb_users.c.id == id_))
    return user

@app.post("/login", response_model=dict)
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    query = tb_users.select().where(tb_users.c.email == form_data.username)
    db_user = await database.fetch_one(query)

    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not pwd_context.verify(form_data.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"sub": db_user["id"]}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/instagram_posts")
async def fetch_instagram_posts(
    ig_id: InstagramPostRequest,
    token: dict = Depends(verify_token)
):
    # Access the user information from the token
    user_id = token.get("sub")

    result = []
    ig_posts = scrape_instagram_data(instagram_id=ig_id.instagram_id.strip(), all_posts=False)

    for post in ig_posts:
        print(f"DEBUG: processing {post['id']}")
        try:
            gingered_op = fix_my_cap(post['caption'])
            post['any_corrections'] = len(gingered_op["corrections"]) > 0
            post['total_errors'] = len(gingered_op["corrections"])
            post['correction_results'] = gingered_op["result"]
            post['corrections_list'] = gingered_op["corrections"]

            file_name = f"{post['id']}.jpg"
            img_save_path = str(STATIC_IMAGES_DIR / file_name)
            download_image(url=post['displayUrl'], save_path=img_save_path)
            post["displayUrl_hosted"] = f"{server_address}/imgs/{file_name}"

            result.append(post)
        except:
            print("ERROR: fields like caption not found in post: {post}")
            continue

    # Print the user ID
    query = tb_users.select().where(tb_users.c.id == user_id)
    db_user = await database.fetch_one(query)
    print(f"User ID: {user_id},{db_user['email']}")

    return result

@app.post("/save_ig_posts")
async def save_ig_posts(saved_post: SavedIgPost, token: dict = Depends(verify_token)):
    # Access the user information from the token
    user_id = token.get("sub")
    # Print the user ID
    query = tb_users.select().where(tb_users.c.id == user_id)
    db_user = await database.fetch_one(query)
    print(f"User ID: {user_id},{db_user['email']}")

    try:
        values = {
            "post_id": saved_post.post_id,
            "ownerUsername": saved_post.ownerUsername,
            "extensionId": saved_post.extensionId,
            "caption": saved_post.caption,
            "displayUrl_hosted": saved_post.displayUrl_hosted,
            "url": saved_post.url,
            "correction_results": saved_post.correction_results,
            "helpful": saved_post.helpful,
            "dismiss": saved_post.dismiss,
        }

        query = tb_saved_ig_posts.insert().values(**values)
        await database.execute(query)

        print("\nDEBUG: Instagram post saved successfully:", values)
        return {"message": "Instagram post saved successfully"}
    except Exception as e:
        return {"error": str(e)}
