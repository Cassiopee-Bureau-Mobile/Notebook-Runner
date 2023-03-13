from enum import Enum
from typing import Any, Dict
from notebook_bis import Data, Name, Notebook, Output, OutputType

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
    
    def __init__(self, notebook: Notebook):
        self.notebook = notebook
        self.state = State.STARTED
        self.cell_number = 0
        self.number_of_cells = notebook.count_code_cells()
        self.current_cell_has_output = False
        self.printer = Printer(notebook.count_code_cells(), self)
        self.next_output_type = None
        
        
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
            self.notebook.save()
            self.notebook.set_execution_count(self.cell_number -1, self.cell_number)
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
                switcher = {
                    self.OUTPUT_CELL_STR_1: OutputType.STREAM,
                    self.OUTPUT_CELL_STR_2: OutputType.EXECUTE_RESULT,
                    self.OUTPUT_CELL_STR_3: OutputType.DISPLAY_DATA
                }
                
                new_output_type = switcher.get(out, OutputType.STREAM)
                if new_output_type != self.next_output_type:
                    self.current_cell_has_output = False
                    self.next_output_type = new_output_type
                    self.notebook.save()
                
                self.set_output()
                return
        
        if state == State.CELL_OUTPUT:
            content = self.get_content(out)
            text = content.get("text")
            execution_count = content.get("execution_count", self.cell_number)
            
            if text == None:
                text = content.get("data", {}).get("text/plain", "")
            
            output = None   
            if self.next_output_type == OutputType.STREAM:
                text = content.get("text", "")
                name = Name.STDOUT if content.get("name", "stdout") == "stdout" else Name.STDERR
                output = Output.create_stream_output(text, name, execution_count)
            elif self.next_output_type == OutputType.EXECUTE_RESULT:
                data = Data.from_dict(content.get("data", {}))
                output = Output.create_execute_result_output(data, execution_count)
            else:
                data = Data.from_dict(content.get("data", {}))
                output = Output.create_display_data_output(data, execution_count)
                
            self.notebook.add_output(self.cell_number -1, output)
            
            self.printer.print_output(text)
            self.set_idle()
            return
        
        if self.END_STR in out:
            self.set_finished()
            self.printer.print_finished()
            return
        
    