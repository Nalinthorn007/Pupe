from pydantic import BaseModel, Field

class RouterSchema(BaseModel):
    """
    Schema ຫຼັກສຳລັບ Router Output
    """
    sql_script: str = Field(
        description=(
            "SQL Query (MariaDB SELECT statement). "
            "DO NOT escape single quotes (') inside the SQL string. "
            "Only double quotes (\") need to be escaped for JSON structure. "
            "Example: \"SELECT * FROM users WHERE name = 'Somdy'\""
        )
    )