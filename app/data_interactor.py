import mysql.connector
from mysql.connector import Error
import os
from typing import List, Optional


class Contact:
    """
    Represents a contact with basic information
    """

    def __init__(self, id: int, first_name: str, last_name: str, phone_number: str):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number

    def to_dict(self) -> dict:
        """
        Convert contact object to dictionary
        """
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number
        }

    def __repr__(self) -> str:
        return f"Contact(id={self.id}, name={self.first_name} {self.last_name}, phone={self.phone_number})"


def get_db_connection():
    """
    Create and return a database connection
    Reads configuration from environment variables
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'db'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'rootpassword'),
            database=os.getenv('DB_NAME', 'contacts_db')
        )

        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise

    return None


# ============ CRUD Operations ============

def create_contact(first_name: str, last_name: str, phone_number: str) -> Optional[int]:
    """
    Create a new contact in the database
    Returns: The ID of the newly created contact, or None if failed
    """
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Manual SQL query
        query = """
        INSERT INTO contacts (first_name, last_name, phone_number) 
        VALUES (%s, %s, %s)
        """

        cursor.execute(query, (first_name, last_name, phone_number))
        connection.commit()

        # Get the ID of the newly created contact
        new_id = cursor.lastrowid

        return new_id

    except Error as e:
        print(f"Error creating contact: {e}")
        if connection:
            connection.rollback()
        return None

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def get_all_contacts() -> List[Contact]:
    """
    Retrieve all contacts from the database
    Returns: List of Contact objects
    """
    connection = None
    cursor = None
    contacts = []

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Manual SQL query
        query = "SELECT id, first_name, last_name, phone_number FROM contacts"

        cursor.execute(query)
        results = cursor.fetchall()

        # Convert results to Contact objects
        for row in results:
            contact = Contact(
                id=row[0],
                first_name=row[1],
                last_name=row[2],
                phone_number=row[3]
            )
            contacts.append(contact)

        return contacts

    except Error as e:
        print(f"Error retrieving contacts: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def update_contact(contact_id: int, first_name: Optional[str] = None,
                   last_name: Optional[str] = None,
                   phone_number: Optional[str] = None) -> bool:
    """
    Update an existing contact
    Only updates fields that are provided (not None)
    Returns: True if successful, False otherwise
    """
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Build dynamic UPDATE query based on provided fields
        update_fields = []
        values = []

        if first_name is not None:
            update_fields.append("first_name = %s")
            values.append(first_name)

        if last_name is not None:
            update_fields.append("last_name = %s")
            values.append(last_name)

        if phone_number is not None:
            update_fields.append("phone_number = %s")
            values.append(phone_number)

        # If no fields to update, return False
        if not update_fields:
            return False

        # Add the contact_id at the end
        values.append(contact_id)

        # Build the query
        query = f"UPDATE contacts SET {', '.join(update_fields)} WHERE id = %s"

        cursor.execute(query, tuple(values))
        connection.commit()

        # Check if any row was affected
        return cursor.rowcount > 0

    except Error as e:
        print(f"Error updating contact: {e}")
        if connection:
            connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def delete_contact(contact_id: int) -> bool:
    """
    Delete a contact from the database
    Returns: True if successful, False otherwise
    """
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Manual SQL query
        query = "DELETE FROM contacts WHERE id = %s"

        cursor.execute(query, (contact_id,))
        connection.commit()

        # Check if any row was affected
        return cursor.rowcount > 0

    except Error as e:
        print(f"Error deleting contact: {e}")
        if connection:
            connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()