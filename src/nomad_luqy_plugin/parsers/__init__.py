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
    mainfile_name_re=r'.*\.(?:txt|csv|tsv)$',
)
