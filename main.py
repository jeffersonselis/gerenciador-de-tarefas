from fastapi import FastAPI, HTTPException
from datetime import datetime,time,date
import pyodbc
from pydantic import BaseModel,Field
from typing import Literal
from pydantic import field_validator,model_validator
from ia_prioridade import modelo

## modelo de dados da tarefa, usado nas rotas
class Tarefa(BaseModel):
    titulo: str = Field(min_length=1)
    descriçao: str  |None = Field(default=None,max_length=300)
    status: str = Field (min_length=1,max_length=20)
    prioridade:Literal["baixa","média","alta"]
    categoria: str | None = Field(default=None,max_length=30)
    data_agendada:date| None = None
    hora_agendada:time | None = None
    data_criaçao: datetime
    data_limite: datetime | None = None
    data_conclusao: date | None = None
    observaçao: str | None = Field(default=None,max_length=300)
    @field_validator("prioridade",mode="before")
    @classmethod
    def normalizar_prioridade(cls,valor):
       if isinstance(valor,str):
          valor = valor.strip().lower()
       if valor == "media":
          valor = "média"
       return valor
    @model_validator(mode= "after")
    def validar_prazo(self):
       if self.data_agendada is not None and self.data_limite is not None:
          if self.data_limite.date() < self.data_agendada:
              raise ValueError("A data limite nao pode ser anterior á data agendada!")
          if self.hora_agendada is not None:
             if self.data_limite.date() == self.data_agendada:
                if self.data_limite.time().replace(tzinfo = None) < self.hora_agendada.replace(tzinfo = None):
                   raise ValueError("O horario limite nao pode ser anterior ao horario agendado!")
       return self
          
    
   

app = FastAPI(title="gerenciador de tarefas",
 description="API para gerenciar tarefas")
conexao = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL server};SERVER=localhost;DATABASE=Gerenciador de Tarefas;Trusted_Connection=yes;")
@app.get("/")
def inicio():
    return{"mensagem": "API Gerenciador de Tarefas funcionando"}
## Rota para criar uma nova tarefa,recebe dados validados pelo pydantic e insere no banco
@app.post("/tarefas")
def criar_tarefa(nova_tarefa:Tarefa):
    try:
      ## cria o cursor para executar comandos no banco
      cursor = conexao.cursor()
      ## A ia analiza a descrição ou o titulo da tarefa, e sugere prioridade alta media ou baixa
      ## a prioridade sugerida pela ia nao substitui a prioridade escolhida pelo usuario 
      prioridade_sugerida = str(modelo.predict([nova_tarefa.descriçao or nova_tarefa.titulo])[0])
      ## executa o comando SQL para inserir uma tarefa no banco
      cursor.execute("""INSERT INTO dbo.Tarefas ([Titulos],[Descriçao],[Status],[Prioridade],[Categoria],
      [Data agendada],[Hora agendada],[Data de criaçao],[Data limite],[Data conclusao],[Observaçao])
      VALUES (?,?,?,?,?,?,?,?,?,?,?)""", nova_tarefa.titulo,nova_tarefa.descriçao,nova_tarefa.status,nova_tarefa.prioridade,
      nova_tarefa.categoria,nova_tarefa.data_agendada,nova_tarefa.hora_agendada,nova_tarefa.data_criaçao,
      nova_tarefa.data_limite,nova_tarefa.data_conclusao,nova_tarefa.observaçao)
      ## confirma e salva a nova tarefa inserida no banco de dados 
      conexao.commit()
      ## retorna uma mensagem confirmando q a tarefa foi criada
      return {"mensagem":"Tarefa criada com sucesso!","prioridade_sugerida":prioridade_sugerida}
      ## Em caso de erro ,desfaz alteraçoes no banco
    except Exception as erro:
      print("Erro real:",erro)
      ## desfaz as alteraçoes nao confirmadas se ocorrer um erro
      conexao.rollback()
      ## propaga o erro para API tratar
      raise HTTPException(status_code=500,detail="Erro ao criar tarefa")
    
## rotas para listar tarefa
@app.get("/tarefas")
def listar_tarefa():
    try:
      cursor = conexao.cursor()
      ## execulta a consulta a consulta select para buscar todas as tarefas
      cursor.execute(" SELECT * FROM tarefas")
      ## obtém todos os resultados da consulta
      tarefas = cursor.fetchall()
      ## inicializa as lista de tarefa que retornada a resposta
      lista_tarefa = []
      ## percorre os resultados e monta lista 
      for tarefa in tarefas:
        lista_tarefa.append({"id":tarefa[0],"titulo":tarefa[1],"descriçao":tarefa[2],"status":tarefa[3],"prioridade":tarefa[4],"categoria":tarefa[5],
        "data_agendada":tarefa[6],"hora_agendada":tarefa[7],"data_criaçao":tarefa[8],"data_limite":tarefa[9],"data_conclusao":tarefa[10],
        "observaçao":tarefa[11]})   
      ## retorna a lista de tarefas para o cliente 
      return lista_tarefa
    except Exception as erro:
       print("Erro real:",erro)
       raise HTTPException(status_code=500,detail="Erro ao listar a tarefa")

## rota para buscar uma tarefa pelo ID           
@app.get("/tarefas/{id_tarefa}")
def buscar_tarefa(id_tarefa:int):
  try:
    cursor = conexao.cursor()
    ## Execulta consulta SELECT para buscar tarefa pelo ID
    cursor.execute(" SELECT * FROM tarefas WHERE ID=?",id_tarefa) 
    ## obtem um unico resultado da consulta
    tarefa = cursor.fetchone()
    ## Verifica se a tarefa foi encntrada
    if not tarefa:  
    ## retorna 404 se a tarefa nao existir
      raise HTTPException(status_code=404,detail="Tarefa nao encontrada!")
    ## retorna os dados da tarefa encontrada
    return ({"id":tarefa[0],"titulo":tarefa[1],"descriçao":tarefa[2],"status":tarefa[3],"prioridade":tarefa[4],"categoria":tarefa[5],
        "data_agendada":tarefa[6],"hora_agendada":tarefa[7],"data_criaçao":tarefa[8],"data_limite":tarefa[9],"data_conclusao":tarefa[10],
        "observaçao":tarefa[11]}) 
  except HTTPException: 
     raise 
  except Exception as erro:
        print("Erro real:",erro)
    ## retorna erro 500 se ocorrer falha interna ao buscar a tarefa 
        raise HTTPException(status_code=500,detail="Erro ao buscar a tarefa")
      
## Rota para atualizar uma tarefa pelo ID
@app.put("/tarefa/{id_tarefa}")
def atualizar_tarefa(id_tarefa:int,tarefa_atualizada: Tarefa):
    try:
       cursor = conexao.cursor()
       ## Executa o UPDATE  para atualizar a tarefa no banco 
       cursor.execute("""UPDATE tarefas SET [Titulos]=?,[Descriçao]=?,[Status]=?, [Prioridade]=?, [Categoria]=?,
       [Data agendada]=?,[Hora agendada]=?,[Data de criaçao]=?,[Data limite]=?,[Data conclusao]=?, [Observaçao]=?  WHERE ID=?""",tarefa_atualizada.titulo,tarefa_atualizada.descriçao,
       tarefa_atualizada.status,tarefa_atualizada.prioridade,tarefa_atualizada.categoria,tarefa_atualizada.data_agendada,
       tarefa_atualizada.hora_agendada,tarefa_atualizada.data_criaçao,tarefa_atualizada.data_limite,tarefa_atualizada.data_conclusao,tarefa_atualizada.observaçao,
       id_tarefa)
       linhas_atualizadas = cursor.rowcount
       if linhas_atualizadas == 0:
          raise HTTPException(status_code=404,detail="Tarefa nao enconttrada")
       ## confirma a atualização no banco 
       conexao.commit()
       ## Retorna mensagem de sucesso da atualização
       return {"mensagem":"Tarefa atualizada com sucesso!"}
    except HTTPException:
           raise
    except Exception as erro:
       print("Erro real:",erro)
       ## Desfaz a transação em caso de erro 
       conexao.rollback() 
       ## Propaga o erro interno para API retorná a resposta 
       raise HTTPException(status_code=500,detail="Erro ao atualizar a tarefa")
    
## Rota para excluir uma tarefa pelo ID
@app.delete("/tarefa/{id_tarefa}")
def deletar_tarefa(id_tarefa:int):
    try:
      cursor = conexao.cursor()
      ## Executa o comdando SQL para excluir uma tarefa pelo ID
      cursor.execute("delete from tarefas WHERE ID=?",id_tarefa)
      ## Armazena a quantida de linhas excluidas do banco 
      linhas_excluidas = cursor.rowcount
      ## Verifica se uma linha foi excluida 
      if linhas_excluidas == 0:
      ## Retorna erro 404  se nenhuma tarefa foi encontrada para exclusaão
         raise HTTPException(status_code=404,detail="Tarefa nao encontrada")
      ## Confirma á exclusão no banco
      conexao.commit()
      ## Retorna mensagem de sucesso da  exclusão 
      return{"mensagem":"Tarefa deletada com sucesso!"}
    except HTTPException:
       raise
    except Exception as erro:
        print("Erro real:",erro)
      ## Desfaz a transação em caso de erro 
        conexao.rollback() 
      ## Propaga  o erro para API retoná a resposta 
        raise HTTPException(status_code=500,detail="Erro ao deletar a tarefa")

@app.get("/ia/prioridade")
def sugerir_prioridade(descriçao:str):
    previsao = modelo.predict([descriçao])[0]
    return {"prioridade":previsao}
