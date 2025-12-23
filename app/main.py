from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
import data_interactor as db


# ============ Pydantic Models ============

class ContactCreate(BaseModel):
    """Request model for creating a contact"""
    first_name: str
    last_name: str
    phone_number: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "050-1234567"
            }
        }


class ContactUpdate(BaseModel):
    """Request model for updating a contact"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "052-9999999"
            }
        }


class ContactResponse(BaseModel):
    """Response model for a contact"""
    id: int
    first_name: str
    last_name: str
    phone_number: str


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    id: Optional[int] = None


# ============ FastAPI App ============

app = FastAPI(
    title="Contact Manager API",
    description="A REST API for managing contacts",
    version="1.0.0"
)


@app.get("/")
def read_root():
    """Root endpoint - API info"""
    return {
        "message": "Welcome to Contact Manager API",
        "endpoints": {
            "GET /contacts": "Get all contacts",
            "POST /contacts": "Create a new contact",
            "PUT /contacts/{id}": "Update a contact",
            "DELETE /contacts/{id}": "Delete a contact"
        }
    }


@app.get("/contacts", response_model=List[ContactResponse])
def get_contacts():
    """
    Retrieve all contacts from the database
    """
    try:
        contacts = db.get_all_contacts()
        
        # Convert Contact objects to dictionaries
        return [contact.to_dict() for contact in contacts]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving contacts: {str(e)}"
        )


@app.post("/contacts", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact: ContactCreate):
    """
    Create a new contact in the database
    """
    try:
        new_id = db.create_contact(
            first_name=contact.first_name,
            last_name=contact.last_name,
            phone_number=contact.phone_number
        )
        
        if new_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create contact. Phone number might already exist."
            )
        
        return {
            "message": "Contact created successfully",
            "id": new_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating contact: {str(e)}"
        )


@app.put("/contacts/{contact_id}", response_model=MessageResponse)
def update_contact(contact_id: int, contact: ContactUpdate):
    """
    Update an existing contact
    """
    try:
        success = db.update_contact(
            contact_id=contact_id,
            first_name=contact.first_name,
            last_name=contact.last_name,
            phone_number=contact.phone_number
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contact with id {contact_id} not found"
            )
        
        return {
            "message": "Contact updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating contact: {str(e)}"
        )


@app.delete("/contacts/{contact_id}", response_model=MessageResponse)
def delete_contact(contact_id: int):
    """
    Delete a contact from the database
    """
    try:
        success = db.delete_contact(contact_id=contact_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contact with id {contact_id} not found"
            )
        
        return {
            "message": "Contact deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting contact: {str(e)}"
        )
