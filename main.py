from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
import models  # Import your SQLAlchemy models
from database import SessionLocal, engine  # Correct the import for the database setup
#db: Session = Depends(get_db)==> dependency injection
app = FastAPI()

# Create the database tables
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    value: int = Field(..., ge=0, le=100)

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    items = db.query(models.Item).all()
    return items

@app.post("/items/", response_model=Item)
async def create_item(item: Item, db: Session = Depends(get_db)):
    temp_item = models.Item(name=item.name, value=item.value)
    db.add(temp_item)
    db.commit()
    db.refresh(temp_item)
    return temp_item

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return item

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.name = item.name
    db_item.value = item.value
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}", response_model=Item)
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return item
