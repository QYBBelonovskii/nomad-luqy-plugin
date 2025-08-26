from nomad.config.models.plugins import ParserEntryPoint
from pydantic import Field


class LuQYParserEntryPoint(ParserEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from .parser import LuQYParser

        return LuQYParser()


parser_entry_point = LuQYParserEntryPoint(
    name='LuQYParser',
    description='Parser for LuQY Pro time-series + spectrum files.',
)


"""
from nomad.config.models.plugins import ParserEntryPoint
from pydantic import Field


class NewParserEntryPoint(ParserEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from nomad_luqy_plugin.parsers.parser import NewParser

        return NewParser(**self.model_dump())


parser_entry_point = NewParserEntryPoint(
    name='NewParser',
    description='New parser entry point configuration.',
    mainfile_name_re=r'.*\.newmainfilename',
)
"""
