from pydantic import BaseModel, Field
from typing import Optional

class PokeRequest(BaseModel):
    """Request model for Poke API"""
    
    id: Optional[int] = Field(
        default = None, 
        ge = 1, 
        description="ID de la Petición"
        )
    pokemon_type: Optional[str] = Field(
        default = None, 
        description="Tipo de Pokemon",
        pattern = "^[a-zA-Z0-9_]+$"
        )
    
    url: Optional[str] = Field(
        default = None, 
        description="URL de la Petición",
        pattern = "^https?://[^\s]+$"
        )
    
    status: Optional[str] = Field(
        default = None, 
        description="Estado de la Petición",
        pattern = "^(sent|completed|failed|inprogress)$"
        )
    
    sample_size: Optional[int] = Field(
        default = None, 
        gt = 0, 
        description="Tamaño de la Muestra"
        )
    
    