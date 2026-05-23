from sqlalchemy import Column, String, Numeric, Integer, Date, Float, UUID as SQLUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, Table
from app.database import engine

ViewBase = declarative_base()


class UserFinancialSummary(ViewBase):
    __tablename__ = "user_financial_summary"

    id = Column(SQLUUID(as_uuid=True), primary_key=True)
    email = Column(String)
    full_name = Column(String)
    total_accounts = Column(Integer)
    total_transactions = Column(Integer)
    total_income = Column(Numeric(15, 2))
    total_expense = Column(Numeric(15, 2))
    net_savings = Column(Numeric(15, 2))


class GoalProgress(ViewBase):
    __tablename__ = "goal_progress"

    goal_name = Column(String, primary_key=True)
    email = Column(String)
    account_name = Column(String)
    target_amount = Column(Numeric(15, 2))
    saved_amount = Column(Numeric(15, 2))
    progress_percent = Column(Float)
    deadline = Column(Date)
    status = Column(String)


def reflect_views():
    metadata = MetaData()
    metadata.reflect(bind=engine, only=['user_financial_summary', 'goal_progress'])

    for table_name, model in [('user_financial_summary', UserFinancialSummary),
                              ('goal_progress', GoalProgress)]:
        if table_name in metadata.tables:
            table = metadata.tables[table_name]
            for column in table.columns:
                if hasattr(model, column.name):
                    col_attr = getattr(model, column.name)
                    col_attr.key = column.name