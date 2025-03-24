from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os

app = FastAPI()

JSON_FILE = os.getenv("COMMANDS_JSON_PATH", "./befehle.json")

class Command(BaseModel):
    name: str
    command: str
    category: str
    description: Optional[str] = None
    info: Optional[str] = None

def load_commands() -> List[Command]:
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Command(**cmd) for cmd in data]

def save_commands(commands: List[Command]):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump([cmd.dict() for cmd in commands], f, indent=2, ensure_ascii=False)

@app.get("/commands", response_model=List[Command])
def get_commands():
    return load_commands()

@app.post("/commands", response_model=Command)
def create_command(new_cmd: Command):
    commands = load_commands()
    # Optional: check duplicates
    commands.append(new_cmd)
    save_commands(commands)
    return new_cmd

@app.put("/commands/{cmd_name}", response_model=Command)
def update_command(cmd_name: str, updated_cmd: Command):
    commands = load_commands()
    for i, c in enumerate(commands):
        if c.name == cmd_name:
            commands[i] = updated_cmd
            save_commands(commands)
            return updated_cmd
    raise HTTPException(status_code=404, detail="Command not found")

@app.delete("/commands/{cmd_name}")
def delete_command(cmd_name: str):
    commands = load_commands()
    filtered = [c for c in commands if c.name != cmd_name]
    if len(filtered) == len(commands):
        raise HTTPException(status_code=404, detail="Command not found")
    save_commands(filtered)
    return {"message": f"Befehl '{cmd_name}' gelöscht"}