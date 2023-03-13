from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
from typing import Any, Optional, List, Dict



class CellType(Enum):
    CODE = "code"
    MARKDOWN = "markdown"


@dataclass
class Execution:
    iopub_execute_input: datetime
    iopub_status_busy: datetime
    iopub_status_idle: datetime
    shell_execute_reply: datetime
        
    @staticmethod
    def from_dict(obj: dict | None) -> 'Execution | None':
        if obj is None:
            return None
        _iopub_execute_input = datetime.fromisoformat(str(obj.get("iopub.execute_input")))
        _iopub_status_busy = datetime.fromisoformat(str(obj.get("iopub.status.busy")))
        _iopub_status_idle = datetime.fromisoformat(str(obj.get("iopub.status.idle")))
        _shell_execute_reply = datetime.fromisoformat(str(obj.get("shell.execute_reply")))
        
        return Execution(
            iopub_execute_input=_iopub_execute_input, 
            iopub_status_busy=_iopub_status_busy, 
            iopub_status_idle=_iopub_status_idle, 
            shell_execute_reply=_shell_execute_reply)
        
    def to_dict(self) -> Dict[str, str]:
        return {
            "iopub.execute_input": self.iopub_execute_input.isoformat(),
            "iopub.status.busy": self.iopub_status_busy.isoformat(),
            "iopub.status.idle": self.iopub_status_idle.isoformat(),
            "shell.execute_reply": self.shell_execute_reply.isoformat()
        }
        


@dataclass
class CellMetadata:
    execution: Optional[Execution]
    scrolled: Optional[bool]
        
    @staticmethod
    def from_dict(obj: dict | None) -> 'CellMetadata | None':
        if obj is None:
            return None
        _execution = Execution.from_dict(obj.get("execution"))
        _scrolled = obj.get("scrolled") is not None and bool(obj.get("scrolled")) or None
        return CellMetadata(
            execution=_execution, 
            scrolled=_scrolled)
    
    def to_dict(self) -> Dict[str, dict | bool | None] | None:
        value = {}
        if self.execution is not None:
            value["execution"] = self.execution.to_dict()
        if self.scrolled is not None:
            value["scrolled"] = self.scrolled
        return value


@dataclass
class Data:
    image_svg_xml: Optional[List[str]]
    text_plain: List[str]
    text_html: Optional[List[str]]
    
    @staticmethod
    def create_image_svg_xml(image_svg_xml: List[str], text_plain: List[str]) -> 'Data':
        return Data(
            image_svg_xml=image_svg_xml, 
            text_plain=text_plain, 
            text_html=None)

    @staticmethod
    def from_dict(obj: dict | None) -> 'Data | None':
        if obj is None:
            return None
        _image_svg_xml = obj.get("image/svg+xml")
        _text_plain = obj.get("text/plain", [])
        _text_html = obj.get("text/html")
        return Data(
            image_svg_xml=_image_svg_xml, 
            text_plain=_text_plain, 
            text_html=_text_html)
    
    def to_dict(self) -> Dict[str, List[str]] | None:
        value = {
            "text/plain": self.text_plain
        }
        if self.image_svg_xml is not None:
            value["image/svg+xml"] = self.image_svg_xml
        if self.text_html is not None:
            value["text/html"] = self.text_html
        return value


@dataclass
class OutputMetadata:
    pass
    
    @staticmethod
    def from_dict(obj: dict | None) -> 'OutputMetadata | None':
        if obj is None:
            return None
        return OutputMetadata()
    
    def to_dict(self) -> Dict[str, Any] | None:
        return {}



class Name(Enum):
    STDERR = "stderr"
    STDOUT = "stdout"



class OutputType(Enum):
    DISPLAY_DATA = "display_data"
    EXECUTE_RESULT = "execute_result"
    STREAM = "stream"
    




@dataclass
class Output:
    name: Optional[Name]
    output_type: OutputType
    text: Optional[List[str]]
    data: Optional[Data]
    metadata: Optional[OutputMetadata]
    execution_count: Optional[int]
    
    @staticmethod
    def create_stream_output(text: str, name: Name, execution_count: int) -> 'Output':
        return Output(
            name=name, 
            output_type=OutputType.STREAM, 
            text=[text], 
            data=None, 
            metadata=None, 
            execution_count=execution_count)
    
    @staticmethod
    def create_display_data_output(data: Data | None, execution_count: int) -> 'Output':
        return Output(
            name=None, 
            output_type=OutputType.DISPLAY_DATA, 
            text=None, 
            data=data, 
            metadata=None, 
            execution_count=execution_count)
        
    @staticmethod
    def create_execute_result_output(data: Data | None, execution_count: int) -> 'Output':
        return Output(
            name=None, 
            output_type=OutputType.EXECUTE_RESULT, 
            text=None, 
            data=data, 
            metadata=None, 
            execution_count=execution_count)
        
    @staticmethod
    def from_dict(obj: dict | None) -> 'Output | None':
        if obj is None:
            return None
        _name = Name(obj.get("name"))
        _output_type = OutputType(obj.get("output_type"))
        _text = obj.get("text")
        _data = Data.from_dict(obj.get("data"))
        _metadata = OutputMetadata.from_dict(obj.get("metadata"))
        _execution_count = obj.get("execution_count") is not None and int(obj.get("execution_count", 0)) or None
        return Output(
            name=_name, 
            output_type=_output_type, 
            text=_text, 
            data=_data, 
            metadata=_metadata, 
            execution_count=_execution_count)
    
    def to_dict(self) -> Dict[str, List[str] | int | dict | None] | None:
        value = {
            "output_type": self.output_type.value,
            "execution_count": self.execution_count
        }
        if self.name is not None:
            value["name"] = self.name.value
        if self.text is not None:
            value["text"] = self.text
        if self.data is not None:
            value["data"] = self.data.to_dict()
        if self.metadata is not None:
            value["metadata"] = self.metadata.to_dict()
        else :
            value["metadata"] = {}
        return value


@dataclass
class Cell:
    cell_type: CellType
    metadata: Optional[CellMetadata]
    source: List[str]
    execution_count: Optional[int]
    outputs: List[Output | None]
        
    @staticmethod
    def from_dict(obj: dict | None) -> 'Cell | None':
        if obj is None:
            return None
        _cell_type = CellType(obj.get("cell_type"))
        _metadata = CellMetadata.from_dict(obj.get("metadata"))
        _source = obj.get("source", [])
        _execution_count = obj.get("execution_count") is not None and int(obj.get("execution_count", 0)) or None
        _outputs = [Output.from_dict(x) for x in obj.get("outputs", [])]
        return Cell(
            cell_type=_cell_type, 
            metadata=_metadata, 
            source=_source, 
            execution_count=_execution_count, 
            outputs=_outputs)
    
    def to_dict(self) -> Dict[str, List[str] | int | dict | None] | None:
        value = {
            "cell_type": self.cell_type.value, 
            "source": self.source,
            "outputs": []
        }
        if self.metadata is not None:
            value["metadata"] = self.metadata.to_dict()
        else:
            value["metadata"] = {}
        if self.execution_count is not None:
            value["execution_count"] = self.execution_count
        for x in self.outputs:
            if x is not None:
                value["outputs"].append(x.to_dict())
        return value
    
    def add_output(self, output: Output):        
        last_output = self.outputs[-1] if len(self.outputs) > 0 else None
        
        if last_output is None:
            self.outputs.append(output)  
        elif last_output.output_type == OutputType.STREAM and output.output_type == OutputType.STREAM:
            if output.text is not None and last_output.text is not None:
                last_output.text.extend(output.text)
            else :
                self.outputs.append(output)
        else :
            self.outputs.append(output)


@dataclass
class Kernelspec:
    display_name: str
    language: str
    name: str
        
    @staticmethod
    def from_dict(obj: dict | None) -> 'Kernelspec | None':
        if obj is None:
            return None
        _display_name = obj.get("display_name", "")
        _language = obj.get("language", "")
        _name = obj.get("name", "")
        return Kernelspec(
            display_name=_display_name, 
            language=_language, 
            name=_name)
    
    def to_dict(self) -> Dict[str, str] | None:
        value = {
            "display_name": self.display_name, 
            "language": self.language, 
            "name": self.name
        }
        return value


@dataclass
class CodemirrorMode:
    name: str
    version: int
        
    @staticmethod
    def from_dict(obj: dict | None) -> 'CodemirrorMode | None':
        if obj is None:
            return None
        _name = obj.get("name", "")
        _version = obj.get("version", 3)
        return CodemirrorMode(
            name=_name, 
            version=_version)
    
    def to_dict(self) -> Dict[str, str]:
        value = {
            "name": self.name, 
            "version": self.version
        }
        return value
    
@dataclass
class Interpreter:
    hash: str

    @staticmethod
    def from_dict(obj: dict | None) -> 'Interpreter | None':
        if obj is None:
            return None
        _hash = str(obj.get("hash"))
        return Interpreter(hash=_hash)
    
    def to_dict(self) -> Dict[str, str]:
        value = {
            "hash": self.hash
        }
        return value


@dataclass
class Vscode:
    interpreter: Interpreter | None

    @staticmethod
    def from_dict(obj: dict | None) -> 'Vscode | None':
        if obj is None:
            return None
        _interpreter = Interpreter.from_dict(obj.get("interpreter"))
        return Vscode(interpreter=_interpreter)
    
    def to_dict(self) -> Dict[str, Dict[str, str] | None]:
        value = {}
        if self.interpreter is not None:
            value["interpreter"] = self.interpreter.to_dict()
        return value


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
        _file_extension = obj.get("file_extension", "")
        _mimetype = obj.get("mimetype", "")
        _name = obj.get("name", "")
        _nbconvert_exporter = obj.get("nbconvert_exporter", "")
        _pygments_lexer = obj.get("pygments_lexer", "")
        _version = obj.get("version", "")
        return LanguageInfo(
            codemirror_mode=_codemirror_mode, 
            file_extension=_file_extension, 
            mimetype=_mimetype, 
            name=_name, 
            nbconvert_exporter=_nbconvert_exporter, 
            pygments_lexer=_pygments_lexer, 
            version=_version
            )
    
    def to_dict(self) -> Dict[str, str | Dict[str, str]]:
        value:  Dict[str, str | Dict[str, str]] = {
            "file_extension": self.file_extension, 
            "mimetype": self.mimetype, 
            "name": self.name, 
            "nbconvert_exporter": self.nbconvert_exporter, 
            "pygments_lexer": self.pygments_lexer, 
            "version": self.version
        }
        if self.codemirror_mode is not None:
            value["codemirror_mode"] = self.codemirror_mode.to_dict()
        return value


@dataclass
class NotebookMetadata:
    kernelspec: Kernelspec | None
    language_info: LanguageInfo | None
    orig_nbformat: int
    vscode: Vscode | None
        
    @staticmethod
    def from_dict(obj: dict | None) -> 'NotebookMetadata | None':
        if obj is None:
            return None
        _kernelspec = Kernelspec.from_dict(obj.get("kernelspec"))
        _language_info = LanguageInfo.from_dict(obj.get("language_info"))
        _orig_nbformat = int(obj.get("orig_nbformat", 4))
        _vscode = Vscode.from_dict(obj.get("vscode"))
        return NotebookMetadata(
            kernelspec=_kernelspec, 
            language_info=_language_info,
            orig_nbformat=_orig_nbformat,
            vscode=_vscode
            )
    
    def to_dict(self):
        value = {
            "orig_nbformat": self.orig_nbformat
        }
        if self.kernelspec is not None:
            value["kernelspec"] = self.kernelspec.to_dict() # type: ignore
        if self.language_info is not None:
            value["language_info"] = self.language_info.to_dict() # type: ignore
        if self.vscode is not None:
            value["vscode"] = self.vscode.to_dict() # type: ignore
        return value


@dataclass
class Notebook:
    cells: List[Cell | None]
    metadata: NotebookMetadata | None
    nbformat: int
    nbformat_minor: int
    output_file: str | None = None
        
    @staticmethod
    def from_dict(obj: dict | None) -> 'Notebook':
        if obj is None:
            raise ValueError("Notebook object cannot be None")
        
        _cells = [Cell.from_dict(x) for x in obj.get("cells", [])]
        _metadata = NotebookMetadata.from_dict(obj.get("metadata"))
        _nbformat = obj.get("nbformat", 0)
        _nbformat_minor = obj.get("nbformat_minor", 0)
        return Notebook(
            cells=_cells, 
            metadata=_metadata, 
            nbformat=_nbformat, 
            nbformat_minor=_nbformat_minor)
    
    def to_dict(self) -> Dict[str, List[Dict[str, str]] | Dict[str, Dict[str, str] | Dict[str, str | Dict[str, str]]] | int]:
        value = {
            "cells": [],
            "nbformat": self.nbformat, 
            "nbformat_minor": self.nbformat_minor
        }
        if self.metadata is not None:
            value["metadata"] = self.metadata.to_dict()
        for x in self.cells:
            if x is not None:
                value["cells"].append(x.to_dict())
        return value

    def count_code_cells(self) -> int:
        sum = 0
        for cell in self.cells:
            if cell is not None and cell.cell_type == CellType.CODE:
                sum += 1
        return sum
    
    def get_code_cell(self, index: int) -> Cell | None:
        temp_index = 0
        for cell in self.cells:
            if cell is not None and cell.cell_type == CellType.CODE:
                if temp_index == index:
                    return cell
                temp_index += 1
        return None
    
    def save(self, path: str | None = output_file) -> None:
        if path is None:
            path = self.output_file
            if path is None:
                raise ValueError("path cannot be None")
        return
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
            
    def add_output(self, cell_number: int, output: Output) -> None:
        cell = self.get_code_cell(cell_number)
        if cell is not None:
            cell.add_output(output)
            
    def set_execution_count(self, cell_number: int, count: int) -> None:
        cell = self.get_code_cell(cell_number)
        if cell is not None:
            cell.execution_count = count