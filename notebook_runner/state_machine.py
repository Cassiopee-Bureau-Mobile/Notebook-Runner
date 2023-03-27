from enum import Enum
from typing import Any, Dict, List

from .notebook import Notebook, OutputType

from rich.console import Console
from rich.syntax import Syntax
from rich.segment import Segment, Segments
from rich.markdown import Markdown

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
        
    def get_prefix(self, cell_number: int):
        return " " * (self.number_of_spaces - len(str(cell_number))) + "{cell_number} | ".format(cell_number=cell_number)
    
    def print_separator(self):
        self.print_markdown("---")
        
    def print_new_lines(self, number_of_lines: int = 1):
        for _ in range(number_of_lines):
            print()
            
    def print_markdown(self, text: str):
        console.print(Markdown(text))
            
    def print_markdown_with_prefix(self, text: str, cell_number: int):
        md = Markdown("```" + text + "```", code_theme="one-dark", inline_code_theme="one-dark")
        prefix_segment = Segment(self.get_prefix(cell_number))

        for line in console.render_lines(md):
            line.insert(0, prefix_segment)
            console.print(Segments(line))
         
        
    def new_cell(self):
        if self.already_printed == True:
            self.print_separator()
            
        self.already_printed = True 
        _, cell_number = self.state_machine.get_state()
        
        self.print_new_lines(2)
        self.print_separator()
        self.print_markdown("# Executing cell `{}` :".format(cell_number))
        self.print_separator()
    
    def print_code(self, code: str):
        syntax = Syntax(code, "python", theme="one-dark", line_numbers=True)
        console.print(syntax)
        
    def print_non_executing(self, source: List[str]):
        if self.already_printed == True:
            self.print_separator()
            
        self.already_printed = True 
        
        self.print_new_lines(2)
        self.print_separator()
        
        for line in source:
            self.print_markdown(line)
            

            
    def print_output(self, output: str):
        _, cell_number = self.state_machine.get_state()
        
        if self.state_machine.current_cell_has_output == False:
            self.print_separator()
            self.state_machine.current_cell_has_output = True
        
        lines = output.split("\n")
        if len(lines) != 1:
            lines = lines[:-1]
        
        for line in lines:
            self.print_markdown_with_prefix(line, cell_number)
            
    def print_error(self, evalue: str, ename: str):
        _, cell_number = self.state_machine.get_state()
        
        if self.state_machine.current_cell_has_output == False:
            self.print_separator()
            self.print_markdown("# Error:")
            self.print_separator()
            self.state_machine.current_cell_has_output = True
        
        self.print_markdown_with_prefix("Error: " + evalue + ": " + ename, cell_number)
            
    def print_finished(self):
        self.print_separator()
        self.print_new_lines(2)


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
    SKIPPING_STR = "[NbConvertApp] Skipping non-executing cell"
    
    
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
            
    def switcher(self, out: str):
        if self.OUTPUT_CELL_STR_2 in out:
            return OutputType.EXECUTE_RESULT
        if self.OUTPUT_CELL_STR_3 in out:
            return OutputType.DISPLAY_DATA
        return OutputType.STREAM
        
        
        
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
        
        if self.SKIPPING_STR in out:
            cell_skip = int(out.split("cell ")[1].split(" ")[0])
            
            try:
                source = self.notebook.get_cell(cell_skip).source
            except:
                return
            
            if isinstance(source, str):
                source = [source]
            
            self.printer.print_non_executing(source)
        
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
                
                new_output_type = self.switcher(out)
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
            ### State Machine ###
            self.set_finished()
            return
        
    