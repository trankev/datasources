import pydantic


class SampleModel(pydantic.BaseModel):
    str_field: str
    int_field: int
    bool_field: bool
