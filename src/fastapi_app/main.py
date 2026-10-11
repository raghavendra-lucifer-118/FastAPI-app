from fastapi import FastAPI , Request , HTTPException , status , Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from .schemas import PostResponse , PostCreate , UserCreate , UserResponse

from typing import Annotated

from . import models
from .database import Base , engine , get_db

models.Base.metadata.create_all(bind=engine)


from sqlalchemy import select
from sqlalchemy.orm import Session

app = FastAPI()
templates = Jinja2Templates(directory = "templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")


# Endpoints for users
@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.username == user.username),
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    result = db.execute(
        select(models.User).where(models.User.email == user.email),
    )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    new_user = models.User(
        username=user.username,
        email=user.email,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/api/users/{user_id}" , response_model = UserResponse)
def api_get_user(user_id : int , db : Annotated[Session , Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
        
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = "User Not Found")
    
    return user


@app.get("/api/users/{user_id}/posts" , response_model = UserResponse)
def api_get_user_posts(user_id : int , db : Annotated[Session , Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
        
    if user:
        result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
        posts = result.scalars().all()
        
        if posts:
            return posts
        else:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = "Posts Not Found")
        
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = "User Not Found")

    
@app.get("/users/{user_id}/posts" , response_model = UserResponse)
def user_posts(request : Request, user_id : int , db : Annotated[Session , Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
        
    if user:
        result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
        posts = result.scalars().all()
        
        if posts:
            return templates.TemplateResponse(
                    request,
                    "users_posts.html",
                    {"posts": posts, "title": "Home","user" : user},
                )
            
        else:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = "Posts Not Found")
        
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = "User Not Found")
    

# Home and About HTML Response
@app.get("/" , include_in_schema = False)
def home(request : Request):
    return templates.TemplateResponse(request, "home.html")

@app.get("/about" , include_in_schema = False)
def about_app(request : Request):
    return templates.TemplateResponse(request , "about.html")


# All posts api and HTML response
@app.get("/api/posts" , response_model= list[PostResponse])
def get_all_posts_api(db : Annotated[Session , Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    
    if posts:
        return posts
    
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = "Posts Not Found")

@app.get("/posts" , include_in_schema = False)
def get_all_posts(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "posts.html",
        {"posts": posts, "title": "Home"},
    )



# Single posts api and HTML response
# JSON Response
@app.get("/api/posts/{req_id}" , response_model = PostResponse)
def get_single_post_api(req_id : int , db : Annotated[Session , Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == req_id))
    post = result.scalars().first()
    
    if post:
        return post
    
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = "Post Not Found")

# HTML Response
@app.get("/posts/{req_id}" ,include_in_schema = False)
def post_page(request : Request , req_id :int , db : Annotated[Session ,Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == req_id))
    post = result.scalars().first()
        
    if post:
        return templates.TemplateResponse(request , "single_post.html" , {"post" : post})
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = "Post Not Found")  
     
     
# Create Endpoint for a post
@app.post("/api/posts")
def create_post_api(new_req_post : PostCreate , db : Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == new_req_post.user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
        
    
    new_post = models.Post(
        title = new_req_post.title,
        content = new_req_post.content,
        user_id = new_req_post.user_id)    
    
    db.add(new_post)     
    db.commit()
    db.refresh(new_post)
    
    return new_post 
        
            
## StarletteHTTPException Handler
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


### RequestValidationError Handler
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )