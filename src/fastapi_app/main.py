from fastapi import FastAPI , Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles



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
]


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
@app.get("/api/posts/{req_id}")
def get_single_post_api(req_id : int):
    for post in posts:
        if req_id == post.get("id"):
            return post
    return "Post Not Found"    

@app.get("/posts/{req_id}" ,include_in_schema = False)
def get_single_post(request : Request , req_id :int):
    for post in posts:
            if req_id == post.get("id"):
                req_post = post
    return templates.TemplateResponse(request , "single_post.html" , {"post" : req_post})