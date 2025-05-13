from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    """
    Base class for all models.
    """

    id: int
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generate the table name from the class name.
        """
        return cls.__name__.lower()