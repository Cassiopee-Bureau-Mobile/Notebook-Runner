from enum import Enum
from typing import Any, Dict

from notebook import Notebook, OutputType

from rich.console import Console
from rich.syntax import Syntax
from rich.segment import Segment

console = Console()

class SaveLevel(Enum):
    NO_SAVE = 0
    CELL_SAVE = 1
    FULL_SAVE = 2


class Printer:
    def __init__(self, _number_of_cells, _state_machine: 'StateMachine'):
        self.state_machine = _state_machine
        self.number_of_spaces = len(str(_number_of_cells)) + 1
        self.already_printed = False
        
        
    def new_cell(self):
        if self.already_printed == True:
            print("-" * (self.number_of_spaces) + "-| ----------------------------------------------------------")
            
        self.already_printed = True 
        _, cell_number = self.state_machine.get_state()
        
        print("\n\n")
        print("-" * (self.number_of_spaces) + "-| ----------------------------------------------------------")
        print(" " * (self.number_of_spaces - len(str(cell_number))) + "{} | Executing cell {} :".format(cell_number, cell_number))
        print(" " * (self.number_of_spaces) + " | ----------------------------------------------------------")
    
    def print_code(self, code: str):
        _, cell_number = self.state_machine.get_state()
        
        for line in code.split("\n"):
            print(" " * (self.number_of_spaces - len(str(cell_number))) + "{cell_number} | {line}".format(cell_number=cell_number, line=line))
            
        syntax = Syntax(code, "python", theme="material")
        prefix = " " * (self.number_of_spaces - len(str(cell_number))) + "{cell_number} |" 
        prefix_segment = Segment(prefix.format(cell_number=cell_number))
        
        
        for line in console.render_lines(syntax):
            line.insert(0, prefix_segment)
            console.print(*line)

            
    def print_output(self, output: str):
        _, cell_number = self.state_machine.get_state()
        
        if self.state_machine.current_cell_has_output == False:
            print(" " * (self.number_of_spaces) + " | ----------------------------------------------------------")
            self.state_machine.current_cell_has_output = True
        
        lines = output.split("\n")
        if len(lines) != 1:
            lines = lines[:-1]
        
        for line in lines:
            print(" " * (self.number_of_spaces - len(str(cell_number))) + "{cell_number} | {line}".format(cell_number=cell_number, line=line))
            
    def print_error(self, evalue: str, ename: str):
        _, cell_number = self.state_machine.get_state()
        
        if self.state_machine.current_cell_has_output == False:
            print(" " * (self.number_of_spaces) + " | ----------------------------------------------------------")
            print(" " * (self.number_of_spaces) + " | ERROR: ")
            print(" " * (self.number_of_spaces) + " | ----------------------------------------------------------")
            self.state_machine.current_cell_has_output = True
            
        print(" " * (self.number_of_spaces - len(str(cell_number))) + "{cell_number} | {error}".format(cell_number=cell_number, error=(evalue + ": " + ename)))
            
    def print_finished(self):
        print("-" * (self.number_of_spaces) + "-| ----------------------------------------------------------")
        print("\n\n")


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
    
    switcher = {
        OUTPUT_CELL_STR_1: OutputType.STREAM,
        OUTPUT_CELL_STR_2: OutputType.EXECUTE_RESULT,
        OUTPUT_CELL_STR_3: OutputType.DISPLAY_DATA
    }
    
    def __init__(self, notebook: Notebook, save_level: SaveLevel):
        self.notebook = notebook
        self.printer = Printer(notebook.count_code_cells(), self)
        self.state = State.STARTED
        self.cell_number = 0
        self.number_of_cells = notebook.count_code_cells()
        self.current_cell_has_output = False
        self.current_output_type = None
        self.save_level = save_level
        
    def save(self, cell_save: bool = False):
        if self.save_level == SaveLevel.FULL_SAVE:
            self.notebook.save()
        elif self.save_level == SaveLevel.CELL_SAVE and cell_save:
            self.notebook.save()
        
        
    def get_state(self):
        return (self.state, self.cell_number)
    
    def set_executing(self):
        self.state = State.CELL_EXECUTING
        
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
            self.current_cell_has_output = False
            self.cell_number += 1
            
            ### Notebook ###
            self.notebook.set_execution_count(self.cell_number -1, self.cell_number)
            self.save(cell_save=True)
            
            ### Printer ###
            self.printer.new_cell()
            
            ### State Machine ###
            self.set_executing()
            return
        
        state, _ = self.get_state()
        
        if state == State.CELL_ERROR:
            content = self.get_content(out)
            ename: str = content.get("ename", "Error")
            evalue: str = content.get("evalue", "Unknown error")
            
            ### Notebook ###
            self.notebook.create_output_for_cell(OutputType.ERROR, content, cell_number=self.cell_number - 1)
            self.save(cell_save=True)
            
            ### Printer ###
            self.printer.print_error(ename, evalue)
            self.printer.print_finished()
            
            ### State Machine ###
            self.set_finished()
            return
        
        if state == State.CELL_EXECUTING:
            content = self.get_content(out)
            code: str = content.get("code", "")
            
            ### Printer ###
            self.printer.print_code(code)
            
            ### State Machine ###
            self.set_idle()
            return
        
        if state == State.CELL_IDLE:
            if self.OUTPUT_CELL_STR_1 in out \
            or self.OUTPUT_CELL_STR_2 in out \
            or self.OUTPUT_CELL_STR_3 in out:
                
                new_output_type = self.switcher.get(out, OutputType.STREAM)
                if new_output_type != self.current_output_type:
                    self.current_cell_has_output = False
                    self.current_output_type = new_output_type
                
                ### Notebook ###
                self.save()
                
                ### State Machine ###
                self.set_output()
                return
        
        if state == State.CELL_OUTPUT:
            content = self.get_content(out)
            text = content.get("text")
            
            if text == None:
                text = content.get("data", {}).get("text/plain", "")
            
            ### Notebook ###
            self.notebook.create_output_for_cell(self.current_output_type, content, cell_number=self.cell_number - 1)
            
            ### Printer ###
            self.printer.print_output(text)
            
            ### State Machine ###
            self.set_idle()
            return
        
        if self.END_STR in out:
            ### Notebook ###
            self.save(cell_save=True)
            
            ### Printer ###
            self.printer.print_finished()
            
            ### State Machine ###
            self.set_finished()
            return
        
    