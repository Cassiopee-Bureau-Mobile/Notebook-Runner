class Printer:
    def __init__(self, _number_of_cells, _state_machine):
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