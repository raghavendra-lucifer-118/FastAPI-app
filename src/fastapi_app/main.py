from fastapi import FastAPI , Request , HTTPException , status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException



app = FastAPI()
templates = Jinja2Templates(directory = "templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    },
    {
        "id": 3,
        "author": "John Smith",
        "title": "Building APIs with FastAPI",
        "content": "FastAPI makes it simple to build modern and reliable APIs with Python.",
        "date_posted": "April 22, 2025",
    },
    {
        "id": 4,
        "author": "Alice Johnson",
        "title": "Learning Python",
        "content": "Python is beginner-friendly and has many powerful tools for building applications.",
        "date_posted": "April 23, 2025",
    },
    {
        "id": 5,
        "author": "Michael Brown",
        "title": "Why I Like FastAPI",
        "content": "FastAPI provides great performance while keeping API development simple and clean.",
        "date_posted": "April 24, 2025",
    },
    {
        "id": 6,
        "author": "Sarah Wilson",
        "title": "Modern Web APIs with Python",
        "content": "With Python and FastAPI, creating modern web APIs can be quick, straightforward, and enjoyable.",
        "date_posted": "April 25, 2025",
    },
]



# Home and About HTML Response
@app.get("/" , include_in_schema = False)
def home(request : Request):
    return templates.TemplateResponse(request, "home.html")

@app.get("/about" , include_in_schema = False)
def about_app(request : Request):
    return templates.TemplateResponse(request , "about.html")


# All posts api and HTML response
@app.get("/api/posts")
def get_all_posts_api():
    return posts

@app.get("/posts" , include_in_schema = False)
def get_all_posts(request : Request):
    return templates.TemplateResponse(request , "posts.html" , {"posts" : posts})



# Single posts api and HTML response
# JSON Response
@app.get("/api/posts/{req_id}")
def get_single_post_api(req_id : int):
    for post in posts:
        if req_id == post.get("id"):
            return post
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = "Post Not Found")  

# HTML Response
@app.get("/posts/{req_id}" ,include_in_schema = False)
def get_single_post(request : Request , req_id :int):
    for post in posts:
            if req_id == post.get("id"):
                return templates.TemplateResponse(request , "single_post.html" , {"post" : post})
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = "Post Not Found")  
            
        
            
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