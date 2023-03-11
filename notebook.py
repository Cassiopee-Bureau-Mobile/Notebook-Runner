from typing import List
from dataclasses import dataclass

@dataclass
class Execution:
    iopub_execute_input: str
    iopub_status_busy: str
    iopub_status_idle: str
    shell_execute_reply: str

    @staticmethod
    def from_dict(obj: dict | None) -> 'Execution | None':
        if obj is None:
            return None
        _iopub_execute_input = str(obj.get("iopub.execute_input"))
        _iopub_status_busy = str(obj.get("iopub.status.busy"))
        _iopub_status_idle = str(obj.get("iopub.status.idle"))
        _shell_execute_reply = str(obj.get("shell.execute_reply"))
        return Execution(iopub_execute_input=_iopub_execute_input, iopub_status_busy=_iopub_status_busy, iopub_status_idle=_iopub_status_idle, shell_execute_reply=_shell_execute_reply)

@dataclass
class MetadataCell:
    execution: Execution | None

    @staticmethod
    def from_dict(obj: dict | None) -> 'MetadataCell | None':
        if obj is None:
            return None
        _execution = Execution.from_dict(obj.get("execution"))
        return MetadataCell(execution=_execution)

@dataclass
class Interpreter:
    hash: str

    @staticmethod
    def from_dict(obj: dict | None) -> 'Interpreter | None':
        if obj is None:
            return None
        _hash = str(obj.get("hash"))
        return Interpreter(hash=_hash)


@dataclass
class Vscode:
    interpreter: Interpreter | None

    @staticmethod
    def from_dict(obj: dict | None) -> 'Vscode | None':
        if obj is None:
            return None
        _interpreter = Interpreter.from_dict(obj.get("interpreter"))
        return Vscode(interpreter=_interpreter)
    


@dataclass
class Kernelspec:
    display_name: str
    language: str
    name: str

    @staticmethod
    def from_dict(obj: dict | None) -> 'Kernelspec | None':
        if obj is None:
            return None
        _display_name = str(obj.get("display_name"))
        _language = str(obj.get("language"))
        _name = str(obj.get("name"))
        return Kernelspec(display_name=_display_name, language=_language, name=_name)

@dataclass
class CodemirrorMode:
    name: str
    version: int

    @staticmethod
    def from_dict(obj: dict | None) -> 'CodemirrorMode | None':
        if obj is None:
            return None
        _name = str(obj.get("name", ""))
        _version = int(obj.get("version", 3))
        return CodemirrorMode(name=_name, version=_version)

@dataclass
class LanguageInfo:
    codemirror_mode: CodemirrorMode | None
    file_extension: str
    mimetype: str
    name: str
    nbconvert_exporter: str
    pygments_lexer: str
    version: str

    @staticmethod
    def from_dict(obj: dict | None) -> 'LanguageInfo | None':
        if obj is None:
            return None
        _codemirror_mode = CodemirrorMode.from_dict(obj.get("codemirror_mode"))
        _file_extension = str(obj.get("file_extension", ""))
        _mimetype = str(obj.get("mimetype", ""))
        _name = str(obj.get("name", ""))
        _nbconvert_exporter = str(obj.get("nbconvert_exporter", ""))
        _pygments_lexer = str(obj.get("pygments_lexer", ""))
        _version = str(obj.get("version", ""))
        return LanguageInfo(codemirror_mode=_codemirror_mode, file_extension=_file_extension, mimetype=_mimetype, name=_name, nbconvert_exporter=_nbconvert_exporter, pygments_lexer=_pygments_lexer, version=_version)



@dataclass
class Metadata:
    kernelspec: Kernelspec | None
    language_info: LanguageInfo | None
    orig_nbformat: int
    vscode: Vscode | None

    @staticmethod
    def from_dict(obj: dict | None) -> 'Metadata | None':
        if obj is None:
            return None
        _kernelspec = Kernelspec.from_dict(obj.get("kernelspec"))
        _language_info = LanguageInfo.from_dict(obj.get("language_info"))
        _orig_nbformat = int(obj.get("orig_nbformat", 4))
        _vscode = Vscode.from_dict(obj.get("vscode"))
        return Metadata(kernelspec=_kernelspec, language_info=_language_info, orig_nbformat=_orig_nbformat, vscode=_vscode)

@dataclass
class Output:
    name: str # stout or stderr
    output_type: str # stream or ??
    text: List[str]

    @staticmethod
    def from_dict(obj: dict | None) -> 'Output | None':
        if obj is None:
            return None
        _name = str(obj.get("name"))
        _output_type = str(obj.get("output_type"))
        _text = [str(y) for y in obj.get("text", [])]
        return Output(name=_name, output_type=_output_type, text=_text)


@dataclass
class Cell:
    cell_type: str
    execution_count: int
    metadata: MetadataCell | None
    outputs: List[Output | None]
    source: List[str]

    @staticmethod
    def from_dict(obj: dict | None) -> 'Cell | None':
        if obj is None:
            return None
        _cell_type = str(obj.get("cell_type"))
        _execution_count = obj.get("execution_count") is not None and int(obj.get("execution_count", 0)) or 0
        _metadata = MetadataCell.from_dict(obj.get("metadata"))
        _outputs = [Output.from_dict(y) for y in obj.get("outputs", [])]
        _source = [str(y) for y in obj.get("source", [])]
        return Cell(cell_type=_cell_type, execution_count=_execution_count, metadata=_metadata, outputs=_outputs, source=_source)


@dataclass
class Notebook:
    cells: List[Cell | None]
    metadata: Metadata | None
    nbformat: int
    nbformat_minor: int

    @staticmethod
    def from_dict(obj: dict | None) -> 'Notebook':
        if obj is None:
            raise ValueError("Notebook object cannot be None")
        
        _cells = [Cell.from_dict(y) for y in obj.get("cells", [])]
        try :
            _metadata = Metadata.from_dict(obj.get("metadata"))
            _nbformat = int(obj.get("nbformat", 4))
            
            _nbformat_minor = int(obj.get("nbformat_minor", 2))
        except Exception:
            _metadata = None
            _nbformat = 4
            _nbformat_minor = 2
        return Notebook(cells=_cells, metadata=_metadata, nbformat=_nbformat, nbformat_minor=_nbformat_minor)
    
    def count_code_cells(self) -> int:
        sum = 0
        for cell in self.cells:
            if cell is not None and cell.cell_type == "code":
                sum += 1
        return sum
