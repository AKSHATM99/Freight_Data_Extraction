from pydantic import BaseModel, Field

class OutputSchema(BaseModel):
    id: str
    product_line: str
    incoterm: str

    origin_port_code: str | None = None
    origin_port_name: str | None = None
    destination_port_code: str | None = None
    destination_port_name: str | None = None

    cargo_weight_kg: float | None = Field(default=None, alias="weight")
    cargo_cbm: float | None = Field(default=None, alias="cbm")
    is_dangerous: bool = Field(alias="dangerous_goods")

    model_config = {
        "populate_by_name": True,
    }
