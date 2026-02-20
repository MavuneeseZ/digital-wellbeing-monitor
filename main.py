from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

timetable = []

class ClassItem(BaseModel):
    subject: str
    day: str
    start: str
    end: str
    room: str

def to_minutes(time_str):
    hour, minute = map(int, time_str.split(":"))
    return hour * 60 + minute

def detect_conflicts():
    for item in timetable:
        item["conflict"] = False

    for i in range(len(timetable)):
        for j in range(i + 1, len(timetable)):
            a = timetable[i]
            b = timetable[j]

            if (
                a["day"] == b["day"]
                and a["room"] == b["room"]
                and to_minutes(a["start"]) < to_minutes(b["end"])
                and to_minutes(b["start"]) < to_minutes(a["end"])
            ):
                a["conflict"] = True
                b["conflict"] = True

@app.get("/timetable")
def get_timetable():
    return timetable
@app.post("/timetable")
def add_class(item: ClassItem):
    new_item = item.dict()
    new_item["id"] = str(uuid4())
    new_item["conflict"] = False
    timetable.append(new_item)
    detect_conflicts()
    return timetable

@app.delete("/timetable/{id}")
def delete_class(id: str):
    global timetable
    timetable = [c for c in timetable if c["id"] != id]
    detect_conflicts()
    return timetable

@app.put("/timetable/{id}")
def update_class(id: str, item: ClassItem):
    for index, c in enumerate(timetable):
        if c["id"] == id:
            updated_item = item.dict()
            updated_item["id"] = id
            updated_item["conflict"] = False
            timetable[index] = updated_item
    detect_conflicts()
    return timetable

@app.get("/conflicts")
def get_conflicts():
    return [item for item in timetable if item["conflict"]]