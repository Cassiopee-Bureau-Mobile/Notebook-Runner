from enum import Enum
from typing import Any, Dict

from nbformat import NotebookNode, read, write, v4


class OutputType(Enum):
    EXECUTE_RESULT = "execute_result"
    DISPLAY_DATA = "display_data"
    STREAM = "stream"
    ERROR = "error"

class Notebook:
    notebook: NotebookNode
    output_file: str
    
    def __init__(self, input_file, output_file: str):
        notebook = read(input_file, as_version=4)
        if not isinstance(notebook, NotebookNode):
            raise ValueError("Input file is not a valid notebook")
        self.notebook = notebook
        self.output_file = output_file
        
    def count_code_cells(self) -> int:
        sum = 0
        for cell in self.notebook.cells:
            if cell.cell_type == "code":
                sum += 1
        return sum
    
    def get_code_cell(self, cell_number: int) -> NotebookNode:
        count = 0
        
        for cell in self.notebook.cells:
            if cell.cell_type == "code":
                if count == cell_number:
                    return cell
                count += 1
        
        raise ValueError("Cell number is out of range")
    
    def get_cell(self, cell_number: int) -> NotebookNode:
        return self.notebook.cells[cell_number]
    
    def create_output_for_cell(self, output_type: OutputType | None, content: Dict[str, Any], cell_number: int):
        if output_type is None:
            raise ValueError("Output type is None")
        
        msg = {
            "header": {
                "msg_type": output_type.value
            },
            "content": content
        }
        
        output = v4.output_from_msg(msg)
        
        self.add_output(cell_number, output)
        
        
    def add_output(self, cell_number: int, output: NotebookNode):
        cell = self.get_code_cell(cell_number)
        
        last_output = cell.outputs[-1] if len(cell.outputs) > 0 else None
        
        if last_output is not None :
            if last_output.output_type == "stream" and output.output_type == "stream":
                if last_output.name == output.name:
                    if isinstance(last_output.text, str):
                        last_output.text = [last_output.text]
                    if isinstance(output.text, str):
                        output.text = [output.text]
                    last_output.text.extend(output.text)
                    return
        
        cell.outputs.append(output)
            
    def set_execution_count(self, cell_number: int, execution_count: int):
        cell = self.get_code_cell(cell_number)
        cell.execution_count = execution_count
            
    def save(self):
        write(self.notebook, self.output_file)
       