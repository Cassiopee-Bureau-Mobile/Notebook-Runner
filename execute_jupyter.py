import os
import sys
import getopt
import json
import subprocess

from alive_progress import alive_bar

from notebook_bis import Notebook 
from state_machine import State, StateMachine


def parse_input_file(input_file_path) -> Notebook:
    with open(input_file_path, 'r', encoding="utf-8") as input_file:
        notebook = json.load(input_file)
        notebook = Notebook.from_dict(notebook)
        
        return notebook

    
def get_opts_args(sys_args):
    notebook_input_file = None
    notebook_output_file = None
    
    options = "hi:o:"
    long_options = ["help", "input=", "output="]
    help_message = "execute_jupyter.py -i <input_file> -o <output_file>"
    
    try :
        opts, _ = getopt.getopt(sys_args, options, long_options)
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_message)
            sys.exit()
        elif opt in ("-i", "--input"):
            notebook_input_file = arg
        elif opt in ("-o", "--output"):
            notebook_output_file = arg
            
    if notebook_input_file is None:
        print("Input file is required")
        print(help_message)
        sys.exit(2)
        
    if not os.path.exists(notebook_input_file):
        print("Input file does not exist")
        sys.exit(2)
        
    if not os.path.isfile(notebook_input_file):
        print("Input file is not a file")
        sys.exit(2)
    
    if not notebook_input_file.endswith(".ipynb"):
        print("Input file is not a .ipynb file")
        sys.exit(2)
    
    if notebook_output_file is None:
        default_output_file_name = os.path.basename(notebook_input_file)
        default_output_file = "{}_output.ipynb".format(default_output_file_name.split(".ipynb")[0])
        print("No output file specified, using default {}".format(default_output_file))
        notebook_output_file = default_output_file
            
    return notebook_input_file, notebook_output_file



if __name__ == '__main__':
    notebook_input_file, notebook_output_file = get_opts_args(sys.argv[1:])
    notebook = parse_input_file(notebook_input_file)
    notebook.output_file = notebook_output_file
    
    number_of_cells = notebook.count_code_cells()
    
    process = subprocess.Popen(["jupyter", "nbconvert", "--execute", "--log-level='DEBUG'", "--to", "notebook", notebook_input_file, "--output", notebook_output_file], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    
    if process.stdout is None:
        raise ValueError("No stdout")
    
    
    state_machine = StateMachine(notebook)
    current_cell = state_machine.cell_number
    
    
    with alive_bar(manual=True, stats=False, enrich_print=False) as bar:
        for line in process.stdout:
            out = line.decode("utf-8")
            print(out, end="")
            state_machine.interpret_output(out)
            state, cell_number = state_machine.get_state()
            
            bar(cell_number / number_of_cells)
            
            if cell_number != current_cell:
                current_cell = cell_number
            
            if state == State.FINISHED:
                #break
                print("Finished")
        

