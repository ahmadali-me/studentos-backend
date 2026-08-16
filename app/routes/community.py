from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/community", tags=["Community Module"])

class PostCreate(BaseModel):
    title: str
    content: str
    author: str
    tags: Optional[List[str]] = []

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

class CommentCreate(BaseModel):
    post_id: str
    commenter: str
    text: str

class LikeCreate(BaseModel):
    post_id: str
    username: str

posts_db = []
comments_db = []
likes_db = []

@router.get("/posts")
async def get_posts():
    return {"posts": posts_db}

@router.post("/posts")
async def create_post(post: PostCreate):
    new_post = {
        "id": str(len(posts_db) + 1),
        "title": post.title,
        "content": post.content,
        "author": post.author,
        "tags": post.tags,
        "likes_count": 0,
        "created_at": datetime.utcnow()
    }
    posts_db.append(new_post)
    return {"message": "Discussion post created successfully!", "post": new_post}

@router.put("/posts/{post_id}")
async def edit_post(post_id: str, post_update: PostUpdate):
    for post in posts_db:
        if post["id"] == post_id:
            if post_update.title is not None:
                post["title"] = post_update.title
            if post_update.content is not None:
                post["content"] = post_update.content
            if post_update.tags is not None:
                post["tags"] = post_update.tags
            return {"message": "Post updated successfully!", "post": post}
    raise HTTPException(status_code=404, detail="Post not found")

@router.delete("/posts/{post_id}")
async def delete_post(post_id: str):
    for index, post in enumerate(posts_db):
        if post["id"] == post_id:
            posts_db.pop(index)
            return {"message": "Post deleted successfully!", "deleted_id": post_id}
    raise HTTPException(status_code=404, detail="Post not found")

@router.post("/comments")
async def add_comment(comment: CommentCreate):
    new_comment = {
        "id": str(len(comments_db) + 1),
        "post_id": comment.post_id,
        "commenter": comment.commenter,
        "text": comment.text,
        "created_at": datetime.utcnow()
    }
    comments_db.append(new_comment)
    return {"message": "Comment added successfully!", "comment": new_comment}

@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str):
    for index, comment in enumerate(comments_db):
        if comment["id"] == comment_id:
            comments_db.pop(index)
            return {"message": "Comment deleted successfully!", "deleted_id": comment_id}
    raise HTTPException(status_code=404, detail="Comment not found")

@router.post("/likes")
async def like_post(like: LikeCreate):
    existing_like = next((l for l in likes_db if l['post_id'] == like.post_id and l['username'] == like.username), None)
    if existing_like:
        likes_db.remove(existing_like)
        return {"message": "Post unliked successfully!"}
    else:
        likes_db.append({"post_id": like.post_id, "username": like.username})
        return {"message": "Post liked successfully!"}