from enum import Enum
from typing import Any, Dict

from printer import Printer


class State(Enum):
    STARTED = 1
    CELL_EXECUTING = 2
    CELL_OUTPUT = 3
    CELL_IDLE = 4
    CELL_ERROR = 5
    FINISHED = 6

class StateMachine:
    START_CELL_STR = "[NbConvertApp] msg_type: execute_input"
    OUTPUT_CELL_STR_1 = "[NbConvertApp] msg_type: stream"
    OUTPUT_CELL_STR_2 = "[NbConvertApp] msg_type: execute_result"
    OUTPUT_CELL_STR_3 = "[NbConvertApp] msg_type: display_data"
    ERROR_CELL_STR = "[NbConvertApp] msg_type: error"
    END_STR = "[NbConvertApp] Destroying"
    
    def __init__(self, _number_of_cells):
        self.state = State.STARTED
        self.cell_number = 0
        self.number_of_cells = _number_of_cells
        self.current_cell_has_output = False
        self.printer = Printer(_number_of_cells, self)
        
        
    def get_state(self):
        return (self.state, self.cell_number)
    
    def set_executing(self):
        self.state = State.CELL_EXECUTING
        self.cell_number += 1
        
    def set_idle(self):
        self.state = State.CELL_IDLE
        
    def set_output(self):
        self.state = State.CELL_OUTPUT
        
    def set_error(self):
        self.state = State.CELL_ERROR
        
    def set_finished(self):
        self.state = State.FINISHED
        
    def get_content(self, out) -> Dict[str, Any]:
        message = out.split("content: ")[1]
        content = eval(message)
        return content
        
    def interpret_output(self, out):
        if self.ERROR_CELL_STR in out:
            self.set_error()
            return
        
        if self.START_CELL_STR in out:
            self.set_executing()
            self.current_cell_has_output = False
            self.printer.new_cell()
            return
        
        state, _ = self.get_state()
        
        if state == State.CELL_ERROR:
            content = self.get_content(out)
            ename: str = content.get("ename", "Error")
            evalue: str = content.get("evalue", "Unknown error")
            self.printer.print_error(ename, evalue)
            self.printer.print_finished()
            self.set_finished()
            return
        
        if state == State.CELL_EXECUTING:
            content = self.get_content(out)
            code: str = content.get("code", "")
            
            self.printer.print_code(code)
            self.set_idle()
            return
        
        if state == State.CELL_IDLE:
            if self.OUTPUT_CELL_STR_1 in out or self.OUTPUT_CELL_STR_2 in out or self.OUTPUT_CELL_STR_3 in out:
                self.set_output()
                return
        
        if state == State.CELL_OUTPUT:
            content = self.get_content(out)
            text = content.get("text")
            
            if text == None:
                text = content.get("data", {}).get("text/plain", "")
            
            self.printer.print_output(text)
            self.set_idle()
            return
        
        if self.END_STR in out:
            self.set_finished()
            self.printer.print_finished()
            return
        
    