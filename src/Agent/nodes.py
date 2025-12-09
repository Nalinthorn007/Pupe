from loguru import logger
from langchain_core.prompts import ChatPromptTemplate
from src.Agent.state import AgentState
from src.Agent.router_schema import RouterSchema
from src.DB.db_config import get_db_connection
from src.Model_Provider.llm_config import get_router_llm
from src.Agent.tools import FileGenerationSchema, write_chart_file


def get_schema_node(state: AgentState) -> dict:
    """
    Node ສຳລັບດຶງຂໍ້ມູນ tables ທັງໝົດຈາກ schema test_visualization
    (ບໍ່ລວມ records - ຈະໃຫ້ AI execute SQL ເອງ)
    """
    logger.info("📊 Executing Get Schema Node: Fetching all tables from test_visualization...")
    
    connection = None
    result_text = ""
    
    try:
        # 1. ເຊື່ອມຕໍ່ Database
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 2. ດຶງລາຍຊື່ tables ທັງໝົດຈາກ schema test_visualization
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'test_visualization'
        """)
        tables = cursor.fetchall()
        
        if not tables:
            result_text = "ບໍ່ພົບ tables ໃນ schema test_visualization"
            logger.warning(result_text)
            return {"result_schema": result_text}
        
        # 3. ວົນລູບດຶງ structure ຂອງແຕ່ລະ table (ບໍ່ດຶງ records)
        result_text = f"=== Schema: test_visualization ===\n"
        result_text += f"ຈຳນວນ Tables: {len(tables)}\n\n"
        
        for (table_name,) in tables:
            result_text += f"--- Table: {table_name} ---\n"
            
            # ດຶງ columns ຂອງ table
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'test_visualization' 
                AND TABLE_NAME = '{table_name}'
            """)
            columns = cursor.fetchall()
            
            result_text += "Columns:\n"
            for col_name, data_type, is_nullable, col_key in columns:
                key_info = f" [{col_key}]" if col_key else ""
                null_info = "NULL" if is_nullable == "YES" else "NOT NULL"
                result_text += f"  - {col_name}: {data_type} ({null_info}){key_info}\n"
            
            result_text += "\n"

            print("result_text: ", result_text)
        
        cursor.close()
        connection.close()
        
        logger.success(f"✅ Schema fetched successfully: {len(tables)} tables")
        return {"result_schema": result_text}
        
    except Exception as e:
        logger.error(f"❌ Error fetching schema: {e}")
        if connection:
            connection.close()
        return {"result_schema": f"Error: {str(e)}"}


# ===========================
# SQL AGENT PROMPT
# ===========================

from langchain_core.output_parsers import JsonOutputParser

SQL_AGENT_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """ທ່ານເປັນ **Expert SQL Developer ລະດັບສູງ** ທີ່ຖືກອອກແບບມາສຳລັບການສ້າງ SQL Query (MariaDB) ທີ່ສັບຊ້ອນ ແລະ ມີປະສິດທິພາບ.

Database Schema:
{schema}

---

### 📚 ກົດລະບຽບ ແລະ ຄຳແນະນຳເພີ່ມເຕີມ:

1.  **ຄຳສັ່ງທີ່ອະນຸຍາດ:** ທ່ານຕ້ອງໃຊ້ສະເພາະຄຳສັ່ງ **SELECT** ເທົ່ານັ້ນ!
2.  **ຄວາມຖືກຕ້ອງ ແລະ ຄວາມສັບສົນ:** ຕ້ອງສ້າງ Query ທີ່ຖືກຕ້ອງທາງໄວຍາກອນ (Syntax). ສໍາລັບຄໍາຖາມທີ່ຕ້ອງການລາຍລະອຽດ ຫຼື ການລວມຂໍ້ມູນ, ໃຫ້ໃຊ້ **JOINs** (ເຊັ່ນ: `INNER JOIN`, `LEFT JOIN`), **GROUP BY**, **SUM()**, **COUNT()**, **AVG()**, **MAX()**, **MIN()**, **LIKE()**, **IN()**, **BETWEEN()**, **LIMIT()**, **OFFSET()**, **HAVING()**, **WHERE()**, **ORDER BY** ແລະ **UNION()** ຢ່າງເໝາະສົມ.
3.  **Schema Naming:** ຕ້ອງໃຊ້ **Schema name** `test_visualization` ນໍາໜ້າຊື່ຕາຕະລາງສະເໝີ (ເຊັ່ນ: `SELECT * FROM test_visualization.users`).
4.  **Ambiguity Handling:** ຖ້າຄໍາຖາມຂອງຜູ້ໃຊ້ບໍ່ຊັດເຈນ, ໃຫ້ສ້າງ Query ທີ່ດີທີ່ສຸດຕາມຫຼັກການການວິເຄາະຂໍ້ມູນທີ່ຖືກຖາມເລື້ອຍໆ.
5.  **ຫ້າມມີ SQL Injection:** ຮັບປະກັນວ່າ Query ປອດໄພ.
6.  **ບັງຄັບ: ຖ້າຜູ້ໃຊ້ ຖາມຫາປະເພດຄົນ ໃຫ້ໃຊ້ແບບນີ້ ຕົວຢ່າງ Like '%ສົມດີ%' ແທນ name = 'ສົມດີ'

### ⚠️ FORMAT INSTRUCTIONS (ສຳຄັນ):
1. ຕອບກັບມາເປັນ **JSON Object** ເທົ່ານັ້ນ.
2. ຫ້າມມີຄຳອະທິບາຍອື່ນນອກເໜືອຈາກ JSON.
3. **ຫ້າມ Escape Single Quote** ພາຍໃນ SQL String.
   - ✅ ຖືກ: {{"sql_script": "SELECT * FROM t WHERE name = 'ສົມດີ'"}}
   - ❌ ຜິດ: {{"sql_script": "SELECT * FROM t WHERE name = \\'ສົມດີ\\'"}}

Format Output:
{{
    "sql_script": "SQL Query ຢູ່ນີ້..."
}}
"""
    ),
    ("user", "ຄຳຖາມ: {question}")
])



def sql_agent_node(state: AgentState) -> dict:
    logger.info("🤖 Generating SQL (JSON Mode)...")
    
    question = state.get("question", "")
    schema = state.get("result_schema", "")
    
    if not question or not schema:
        return {"sql_script": ""}

    try:
        llm = get_router_llm(model_name="moonshotai/kimi-k2-instruct-0905", temperature=0.0)
        
        chain = SQL_AGENT_PROMPT | llm
        
        response = chain.invoke({
            "schema": schema,
            "question": question
        })
        
        raw_content = response.content
        logger.debug(f"Raw LLM Output: {raw_content}")
    
        # ຖ້າ Model ຫຼົງສົ່ງ \' ມາ, ເຮົາຈະແທນທີ່ມັນດ້ວຍ ' ທຳມະດາ
        if "\\'" in raw_content:
            logger.warning("⚠️ Detected escaped single quotes. Fixing...")
            raw_content = raw_content.replace("\\'", "'")
        
        # ລຶບ markdown ```json ... ``` ຖ້າມີຕິດມາ
        raw_content = raw_content.strip().strip('`').replace('json', '', 1).strip()

        parser = JsonOutputParser()
        parsed_data = parser.parse(raw_content)
        
        sql_script = parsed_data.get("sql_script", "")
        return {"sql_script": sql_script}

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        # ກໍລະນີ Parse ບໍ່ໄດ້ແທ້ໆ ໃຫ້ລອງສົ່ງ raw content ກັບໄປເບິ່ງ (ຫຼື return error)
        return {"sql_script": f"-- Error parsing SQL: {str(e)}"}


# ===========================
# EXECUTE SQL NODE
# ===========================

def execute_sql_node(state: AgentState) -> dict:
    """
    Node ສຳລັບ execute SQL script ແລະດຶງຂໍ້ມູນ
    """
    logger.info("🚀 Executing SQL Query...")
    
    sql_script = state.get("sql_script", "")

    print("sql_script: ", sql_script)
    
    if not sql_script or sql_script.startswith("--"):
        logger.warning("⚠️ No valid SQL script to execute")
        return {"sql_result": {"error": "No valid SQL script", "columns": [], "rows": []}}
    
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute(sql_script)
        
        # ດຶງຊື່ columns
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # ດຶງ rows ທັງໝົດ
        rows = cursor.fetchall()
        
        # ແປງ rows ເປັນ list of dicts ເພື່ອງ່າຍຕໍ່ການໃຊ້ງານ
        result_data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                # ແປງ types ທີ່ບໍ່ serializable ໃຫ້ເປັນ string
                if hasattr(value, 'isoformat'):  # datetime, date
                    value = value.isoformat()
                elif isinstance(value, bytes):
                    value = value.decode('utf-8', errors='replace')
                row_dict[col] = value
            result_data.append(row_dict)
        
        cursor.close()
        connection.close()
        
        logger.success(f"✅ SQL executed successfully: {len(result_data)} rows returned")
        return {
            "sql_result": {
                "columns": columns,
                "rows": result_data,
                "row_count": len(result_data)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error executing SQL: {e}")
        if connection:
            connection.close()
        return {
            "sql_result": {
                "error": str(e),
                "columns": [],
                "rows": []
            }
        }

CHART_AGENT_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """ທ່ານແມ່ນ **Expert Visualization Agent ລະດັບສູງ** ທີ່ມີຄວາມຊຳນານໃນການສ້າງ Code HTML, CSS, ແລະ JavaScript (ໃຊ້ Chart.js) ທີ່ສວຍງາມ ແລະ ມີການວິເຄາະ.

### ພາລະກິດຫຼັກ:
1.  **ວິເຄາະ ແລະ ເລືອກ Chart:** ຕັດສິນໃຈວ່າຄວນສ້າງ Chart ປະເພດໃດທີ່ເໝາະສົມກັບໂຄງສ້າງ ແລະ ເນື້ອໃນຂອງ `ຜົນລັບຈາກ Database`.

2.  **⚠️ ການຈັດການການສະແດງຜົນຂໍ້ມູນຂະໜາດໃຫຍ່ (ສຳຄັນ):**
    * **ຫ້າມ** ຕັດ ຫຼື ຈຳກັດຈຳນວນຂໍ້ມູນ (ເຊັ່ນ: Top 10). ຕ້ອງສະແດງທຸກແຖວຂອງຂໍ້ມູນທີ່ໄດ້ຮັບມາ.
    * **ສຳລັບ Bar Chart ເທົ່ານັ້ນ:** ຖ້າຂໍ້ມູນມີແຖວ (Rows) **ເກີນ 15 ແຖວ** ແລະ ເປັນ Bar Chart, ທ່ານຕ້ອງສ້າງ **Horizontal Bar Chart** ເທົ່ານັ້ນ.
    * **CSS Scroll Control:** ໃຫ້ກຳນົດຂະໜາດຂອງ Canvas ໃຫ້ມີຄວາມສູງທີ່ເໝາະສົມ (ເຊັ່ນ: 600px) ແລະ ໃຫ້ໃຊ້ **CSS Overflow/Scroll** ຂອງ Container (<div>) ຫຸ້ມ Chart ນັ້ນ ເພື່ອໃຫ້ຜູ້ໃຊ້ສາມາດເລື່ອນເບິ່ງ Chart ໄດ້ໂດຍບໍ່ເຮັດໃຫ້ໜ້າເວັບຢາວເກີນໄປ.

3.  **ສ້າງ HTML Code ທີ່ສວຍງາມ:** ຕ້ອງສ້າງ Code ທີ່ສົມບູນ ແລະ ເນັ້ນການອອກແບບດັ່ງຕໍ່ໄປນີ້:
    * **Font:** ຕ້ອງໃຊ້ Font **Phetsarath OT** ໂດຍການ Import ເຂົ້າໃນ CSS ໃຫ້ຖືກຕ້ອງ.
    * **Design:** ໃຊ້ສີສັນທີ່ທັນສະໄໝ (Modern Color Palette) ແລະ ເຮັດໃຫ້ Chart ມີຄວາມ Responsive.
    * **Structure:** ຕ້ອງມີພາກສ່ວນ HTML ທີ່ຊັດເຈນສຳລັບຄຳບັນລະຍາຍ ແລະ ຜົນການວິເຄາະ.

4.  **ສ້າງບົດວິເຄາະ (Text Analysis):**
    * **Title/Description:** ບັນລະຍາຍວ່າ Chart ນີ້ກ່ຽວກັບຫຍໍ້.
    * **Future Trend Analysis:** ວິເຄາະ Trend ຂອງຂໍ້ມູນທີ່ເຫັນໃນ Chart ແລະ ຄາດຄະເນສິ່ງທີ່ອາດຈະເກີດຂຶ້ນໃນອະນາຄົດ.

5.  **🚨 ຄຳສັ່ງສຸດທ້າຍ (EXECUTION REQUIRED):**
    * **ການຮຽກໃຊ້ Tool ເທົ່ານັ້ນ:** ທ່ານ **ຕ້ອງ** ສົ່ງຜົນລັບຄືນໂດຍການຮຽກໃຊ້ **Tool `FileGenerationSchema` ເທົ່ານັ້ນ**.
    * **Zero Tolerance Rule:** ຫ້າມມີຂໍ້ຄວາມ, ຄຳອະທິບາຍ, ຄຳນຳ, ຫຼື Code block ໃດໆນອກເໜືອຈາກການຮຽກໃຊ້ Tool. **ຖ້າທ່ານຕອບເປັນຂໍ້ຄວາມທຳມະດາ, ທ່ານຈະຖືວ່າລົ້ມເຫຼວໃນພາລະກິດທັນທີ.**

---
### 📝 ຂໍ້ມູນທີ່ຕ້ອງການໃຊ້ (JSON):

**ຄຳຖາມຕົ້ນສະບັບ:** {question}

**ຜົນລັບຈາກ Database: **
{sql_result}

"""
    ),
])

def chart_generation_node(state: AgentState) -> dict:
    logger.info("🎨 Executing Chart Agent Node: Generating HTML/JS...")
    
    question = state.get("question", "")
    
    # ປ່ຽນການດຶງ Key: ຈາກ "query_result" ເປັນ "sql_result"
    sql_result = state.get("sql_result", None) 
    
    # ກວດສອບຂໍ້ມູນ
    if not sql_result or sql_result.get("error"): # ກວດສອບວ່າມີ error ຢູ່ໃນ result ບໍ່
        logger.error("❌ Cannot generate chart: Invalid SQL result.")
        return {"final_report": f"Error: Cannot generate chart due to invalid data: {sql_result.get('error', 'No data')}"}
    
    try:
        # 1. ຕັ້ງຄ່າ LLM
        llm = get_router_llm(model_name="moonshotai/kimi-k2-instruct-0905", temperature=0.1)
        
        # 2. Bind Tool
        chart_generator = CHART_AGENT_PROMPT | llm.bind_tools(
            tools=[FileGenerationSchema]
        )
        
        # 3. Invoke LLM: ຕ້ອງປ່ຽນ Key ທີ່ສົ່ງເຂົ້າ Prompt ໃຫ້ກົງກັບ Prompt ດ້ວຍ
        response = chart_generator.invoke({
            "question": question,
            "sql_result": sql_result
        })
        
        # ... ສ່ວນທີ່ເຫຼືອຂອງ Code Process Tool Call ແມ່ນຄືເກົ່າ ...
        if response.tool_calls:
            # ... process tool call ...
            tool_call = response.tool_calls[0]
            if tool_call["name"] == "FileGenerationSchema":
                args = tool_call["args"]
                file_status = write_chart_file(
                    filename=args.get("filename"),
                    content=args.get("content")
                )
                logger.success(f"✅ Chart Agent finished. Status: {file_status}")
                return {"final_report": file_status}
        else:
             logger.error("❌ LLM did not call the FileGenerationSchema tool.")
             return {"final_report": "Error: Chart generation failed. LLM did not provide tool call."}
        
    except Exception as e:
        logger.error(f"❌ Error in Chart Agent Node: {e}")
        return {"final_report": f"Error: Chart Agent failed with exception: {str(e)}"}