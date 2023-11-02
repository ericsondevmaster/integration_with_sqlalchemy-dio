from sqlalchemy.orm import declarative_base, relationship, Session
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, inspect, select, func

Base = declarative_base()


class User(Base):
    __tablename__ = "user_account"
    id = Column(Integer, primary_key=True)
    name = Column(String(10))
    full_name = Column(String(30))

    address = relationship(
        "Address", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, fullname={self.full_name})"


class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True)
    email_address = Column(String(50), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("user_account.id"), nullable=False)

    user = relationship(
        "User", back_populates="address"
    )

    def __repr__(self):
        return f"Address(id={self.id}, email_address={self.email_address})"


print(User.__tablename__)
print(Address.__tablename__)

# conexão com o banco de dados
engine = create_engine("sqlite://")

# criando as classe como tabelas no banco de dados
Base.metadata.create_all(engine)

# investiga o esquema de banco de dados
inspetor_engine = inspect(engine)
print(inspetor_engine.has_table("user_account"))

print(inspetor_engine.get_table_names())
print(inspetor_engine.default_schema_name)

with Session(engine) as session:
    ericson = User(
        name='ericson',
        full_name='Ericson Alves',
        address=[Address(email_address='ericson.devmaster@gmail.com')]
    )

    joao = User(
        name='joao',
        full_name='João Silva',
        address=[Address(email_address='joaosilva@gmail.com'),
                 Address(email_address='joaosilva@hotmail.com')]
    )

    maria = User(
        name='maria',
        full_name='Maria Pereira'
    )

# enviando para o DB (persistência de dados)
session.add_all([ericson, joao, maria])
session.commit()

stmt = select(User).where(User.name.in_(['ericson', 'joao']))
print("Recuperando usuários a partir de condição de filtragem")
for user in session.scalars(stmt):
    print(user)

stmt_address = select(Address).where(Address.user_id.in_([2]))
print("\nRecuperando os endereços de email de João")
for addres in session.scalars(stmt_address):
    print(addres)

stmt_order = select(User).order_by(User.full_name.desc())
print("\nRecuperando info de maneira ordenda")
for result in session.scalars(stmt_order):
    print(result)

stmt_join = select(User.full_name, Address.email_address).join_from(Address, User)
print("\n")
for result in session.scalars(stmt_join):
    print(result)

connection = engine.connect()
results = connection.execute(stmt_join).fetchall()
print("\nExecutando statement a partir da connection")
for result in results:
    print(result)

stmt_count = select(func.count('*')).select_from(User)
print("\nTotal de instâncias em User")
for result in session.scalars(stmt_count):
    print(result)
