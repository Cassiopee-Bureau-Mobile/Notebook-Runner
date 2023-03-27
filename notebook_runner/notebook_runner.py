import os
import sys
import getopt
import subprocess

from alive_progress import alive_bar

from .notebook import Notebook 
from .state_machine import SaveLevel, State, StateMachine

__version__ = "0.1.0"

    
help_msg="""Usage: {name} <input_file> [OPTIONS]

Information:
    Execute a jupyter notebook and save the output in a new notebook.
    
    If you visualize the output notebook in jupyter on your browser, the output will not be
    synchronized with the code because thre is no refresh option in jupyter to refresh the file when its content changes.

    The output file will be saved in the same directory as the input file.
    
Options:
    -h, --help                   Display this help message and exit
    -o, --output FILENAME        Specify the output filename (default: input_file.nbconvert.ipynb)            
        --save-level LEVEL       Specify the save level during the process:
                                    * NO_SAVE: No save during the process, only at the end
                                    * CELL_SAVE: Save after each cell execution
                                    * FULL_SAVE: SAVE after each output
                                (default: CELL_SAVE)
"""          

    
def get_opts_args(sys_args):
    notebook_input_file = None
    notebook_output_file_for_jupyter = None
    save_level = SaveLevel.CELL_SAVE
    
    options = "ho:"
    long_options = ["help", "output=", "save-level="]
    help_message = help_msg.format(name=sys_args[0])
    
    try:
        opts, args = getopt.gnu_getopt(sys_args[1:], options, long_options)
    except Exception as e:
        print(e)
        print(help_message)
        sys.exit(2)
    
    ### Args part ###
    if len(args) > 0:
        notebook_input_file = args[0]
    
    ### Options part ###
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_message)
            sys.exit()
        elif opt in ("-o", "--output"):
            notebook_output_file_for_jupyter = arg
        elif opt in ("--save-level"):
            try: 
                save_level = SaveLevel[arg.upper()]
            except:
                print("Invalid save level: {}".format(arg))
                print(help_message)
                sys.exit(2)
    
    ### Exceptions ###
            
    if notebook_input_file is None:
        print("Input file is required")
        print(help_message)
        sys.exit(2)
        
    default_output_file_name = os.path.basename(notebook_input_file)
    default_output_file = "{}.nbconvert.ipynb".format(default_output_file_name.split(".ipynb")[0])
        
    if not os.path.exists(notebook_input_file):
        print("Input file does not exist")
        sys.exit(2)
        
    if not os.path.isfile(notebook_input_file):
        print("Input file is not a file")
        sys.exit(2)
    
    if not notebook_input_file.endswith(".ipynb"):
        print("Input file is not a .ipynb file")
        sys.exit(2)
    
    if notebook_output_file_for_jupyter is None:
        print("No output file specified, using default {}".format(default_output_file))
        notebook_output_file_for_jupyter = default_output_file
    
    #Get the path of the input file without the file name
    notebook_output_file_for_save = os.path.dirname(notebook_input_file) + "/" + notebook_output_file_for_jupyter
    
    print("Input file: {}".format(notebook_input_file))
    print("Output file: {}".format(notebook_output_file_for_save))
    
    res = {
        "input_file": notebook_input_file,
        "output_file_name": notebook_output_file_for_jupyter,
        "output_file": notebook_output_file_for_save,
        "save_level": save_level
    }
            
    return res

def notebook_runner():
    options = get_opts_args(sys.argv)
    
    cmd = ["jupyter", "nbconvert", "--execute", "--log-level='DEBUG'", "--to", "notebook", options["input_file"] , "--output", options["output_file_name"]]
    
    process = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    
    if process.stdout is None:
        raise ValueError("No stdout")
    
    
    notebook = Notebook(options["input_file"] , options["output_file"])
    state_machine = StateMachine(notebook, options["save_level"] )
    
    current_cell = state_machine.cell_number
    number_of_cells = notebook.count_code_cells()
    
    
    with alive_bar(manual=True, stats=False, enrich_print=False) as bar:
        for line in process.stdout:
            out = line.decode("utf-8")
            state_machine.interpret_output(out)
            state, cell_number = state_machine.get_state()
            
            bar(cell_number / number_of_cells)
            
            if cell_number != current_cell:
                current_cell = cell_number
            
            if state == State.FINISHED:
                break
        state_machine.printer.print_finished()
        state_machine.notebook.save()
            
        

