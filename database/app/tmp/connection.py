class EntityConnection(Base):
    __tablename__ = "entity_connection"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_type = Column(String, nullable=False)  # 'legal' or 'natural'
    from_id = Column(Uuid(as_uuid=True), nullable=False)
    to_type = Column(String, nullable=False)
    to_id = Column(Uuid(as_uuid=True), nullable=False)
    relation = Column(String, nullable=False)  # SHAREHOLDER, DIRECTOR, etc.
    share_percentage = Column(Numeric(6,3))
    start_date = Column(Date)
    end_date = Column(Date)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
