from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, registry
from sqlalchemy import String

table_registry = registry()

@table_registry.mapped_as_dataclass
class ExtractedData:
    __tablename__ = 'extracted_data'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    cnpj: Mapped[str] = mapped_column(String(18))
    cep: Mapped[str] = mapped_column(String(9))
    data_emissao: Mapped[str] = mapped_column(String(19))
    valor_total: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )