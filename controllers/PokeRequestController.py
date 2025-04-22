import json
import logging

from fastapi import HTTPException
from models.PokeRequest import PokeRequest
from utils.database import execute_query_json
from utils.AQueue import AQueue
from utils.ABlob import ABlob

#configurar el logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def select_pokemon_request(id: int) -> dict:
    try:
        query = "select * from pokequeue.requests where id = ?"
        params = (id,)
        result = await execute_query_json(query, params)
        result_dict = json.loads(result)

        return result_dict
    
    except Exception as e:
        logger.error(f"Error updating report request: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def update_pokemon_request(pokemon_request: PokeRequest) -> dict:
    try:
        query = "exec pokequeue.update_poke_request ?, ?, ? "
        if not pokemon_request.url:
            pokemon_request.url = "";
        params = (pokemon_request.id, pokemon_request.status, pokemon_request.url,)
        result = await execute_query_json(query, params, True)
        result_dict = json.loads(result)

        return result_dict
    
    except Exception as e:
        logger.error(f"Error updating report request: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


async def insert_pokemon_request(pokemon_request: PokeRequest) -> dict:
    try:
        query = "exec pokequeue.create_poke_request ?"
        params = (pokemon_request.pokemon_type,)
        result = await execute_query_json(query, params, True)
        result_dict = json.loads(result)

        await AQueue().insert_message_on_queue(result)

        return result_dict
    

    except Exception as e:
        logger.error(f"Error inserting report request: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

async def get_all_request() -> dict:
    query = """
                SELECT 
                    r.id as ReportId
                    , s.description as Status
                    , r.type as PokemonType
                    , r.url
                    , r.created
                    , r.updated
                FROM pokequeue.requests r
                INNER JOIN pokequeue.status s
                ON r.id_status = s.id
            """
    result = await execute_query_json( query )
    result_dict = json.loads(result)
    blob = ABlob()
    for record in result_dict:
        id = record['ReportId']
        record['url'] = f"{record['url']}?{blob.generate_sas(id)}"
    return result_dict


async def delete_request_registry(id: int) -> dict:
    try:
        # se verifica que el reporte exista en Azure SQL DB
        pokemon_request = await select_pokemon_request(id)
        if not pokemon_request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # se verifica que el archivo CSV correspondiente
        blob_url = pokemon_request[0].get("url")
        if not blob_url:
            logger.warning(f"No blob URL found for request id {id}")
        else:
            try:
                blob = ABlob()
                blob.delete_blob_csv(id)
                logger.info(f"Blob deleted successfully for request id {id}")
            except Exception as blob_error:
                logger.warning(f"Failed to delete blob for request id {id}: {blob_error}")

        query = "exec pokequeue.delete_poke_request ? "
        params = (id,)
        result = await execute_query_json(query, params, True)
        result_dict = json.loads(result)

        return result_dict
    
    except HTTPException:
        raise  # Re-raise known HTTPExceptions
    except Exception as e:
        logger.error(f"Error al intentar eliminar el registro: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")