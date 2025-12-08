# src/Agent/tools.py
from pydantic import BaseModel, Field
import os

class FileGenerationSchema(BaseModel):
    """
    Schema ສຳລັບການສ້າງ File ຜົນລັບສຸດທ້າຍ.
    """
    filename: str = Field(
        description="ຊື່ File ທີ່ຕ້ອງການສ້າງ (ຕ້ອງເປັນ .html ເທົ່ານັ້ນ), ຕົວຢ່າງ: 'chart.html'."
    )
    content: str = Field(
        description=(
            "ເນື້ອໃນຂອງ File ທັງໝົດ, ລວມທັງ HTML, CSS, ແລະ JavaScript (Chart.js ຫຼື D3.js). "
            "ຕ້ອງເປັນ Code HTML ທີ່ສົມບູນພ້ອມສຳລັບການເປີດໃນ Browser."
        )
    )

def write_chart_file(filename: str, content: str) -> str:
    """
    Function ສຳລັບການຂຽນເນື້ອໃນໃສ່ File ໂດຍໃຊ້ Relative Path 
    (ສຳລັບສ້າງ Display/ ຢູ່ຂ້າງ tools.py, ເຊັ່ນ: src/Agent/Display).
    """
    # ກຳນົດ Path ປາຍທາງທີ່ຕ້ອງການ (Relative Path ພາຍໃນ src/Agent/)
    DISPLAY_FOLDER = os.path.join(os.path.dirname(__file__), "Display") 

    # ສ້າງ Path File ທີ່ສົມບູນ
    full_path = os.path.join(DISPLAY_FOLDER, filename)
    
    try:
        # 1. ສ້າງ Directory ຖ້າມັນຍັງບໍ່ມີ (ໃຊ້ DISPLAY_FOLDER ທີ່ເປັນ Absolute Path)
        # ໃຊ້ os.path.dirname(__file__) ເພື່ອໃຫ້ໄດ້ Path ຂອງ Folder ທີ່ tools.py ຢູ່
        if not os.path.exists(DISPLAY_FOLDER):
            os.makedirs(DISPLAY_FOLDER, exist_ok=True)
            
        # 2. ຂຽນ File ໂດຍໃຊ້ Full Path
        with open(full_path, "w", encoding="utf-8") as f: 
            f.write(content)
            
        # 3. Return Status
        return f"File '{full_path}' ໄດ້ຖືກສ້າງສຳເລັດແລ້ວ."
        
    except Exception as e:
        return f"Error: ບໍ່ສາມາດຂຽນ File '{full_path}' ໄດ້: {e}"