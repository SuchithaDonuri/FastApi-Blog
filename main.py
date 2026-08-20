from fastapi import FastAPI, Request,HTTPException,status,Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from schemas import PostCreate, PostResponse
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import session
from database import Base,engine,get_db
from schemas import PostCreate,PostResponse
import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount('/media',StaticFiles(directory='media'),name='media')

templates = Jinja2Templates(directory="templates")
posts: list[dict] = [
    {
        "id": 1,
        "author": "Rahul Verma",
        "title": "Learning FastAPI Step by Step",
        "content": "FastAPI makes building REST APIs simple, fast, and beginner-friendly.",
        "date_posted": "August 10, 2026",
    },
    {
        "id": 2,
        "author": "Ananya Sharma",
        "title": "Why Python is So Popular",
        "content": "Python is widely used because of its readability, huge community, and versatile libraries.",
        "date_posted": "August 12, 2026",
    },
    {
        "id": 3,
        "author": "Vikram Reddy",
        "title": "Getting Started with Web Development",
        "content": "Understanding APIs, databases, and frontend frameworks is the first step toward becoming a full-stack developer.",
        "date_posted": "August 15, 2026",
    },
]


@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"},
    )
    
@app.get("/posts/{post_id}/")
def post_page(request:Request,post_id:int):
    for post in posts:
        if post.get("id") == post_id:
            title=post["title"][:50]
            return templates.TemplateResponse(request,'post.html', {"post":post, "title":title},status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="post not found")


@app.get("/api/posts",response_model=list[PostResponse])
def get_posts():
    return posts

@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreate):
    new_id = max(p["id"] for p in posts) + 1 if posts else 1
    new_post = {
        "id": new_id,
        "author": post.author,
        "title": post.title,
        "content": post.content,
        "date_posted": "April 23, 2025",
    }
    posts.append(new_post)
    return new_post


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



    