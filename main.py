import uvicorn
import json
from fastapi import FastAPI
from utils.database import execute_query_json
from controllers.PokeRequestController import insert_pokemon_request, update_pokemon_request, select_pokemon_request
from models.PokeRequest import PokeRequest


app = FastAPI()

@app.get("/")
async def root():
    query = "SELECT * FROM pokequeue.MESSAGES"
    result = await execute_query_json(query)
    result_dict = json.loads(result)
    return result_dict
    

@app.get("/api/version")
async def version():
    return {"version": "0.2.0"}

@app.get("/api/request/{id}")
async def select_request(id: int):
    return await select_pokemon_request( id )

@app.post("/api/request")
async def create_request(pokemon_request: PokeRequest):
    return await insert_pokemon_request(pokemon_request)

@app.put("/api/request")
async def update_request(pokemon_request: PokeRequest):
    return await update_pokemon_request(pokemon_request)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)