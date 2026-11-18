# Gerenciador de Tarefas 

API para gerenciar tarefas usando FastAPI,SQL Server e IA

## Como executar 
```
pip install -r requirements.txt
```

## Iniciar a API
```
uvicorn main:app --reload
```
## Rotas da API 

- POST /tarefas - cria uma nova tarefa 
- GET /tarefas lista todas as tarefas cadastradas 
- GET /tarefas/{ID_tarefa} busca uma tarefa pelo ID
- PUT /tarefa/{ID_tarefa} atualiza uma tarefa pelo ID 
- DELETE /tarefa/{ID_tarefa} exclui uma tarefa pelo ID 

## Como testar a API

inicia o servidor com uvicorn main:app --reload e acesse http://127.0.0.1:8000/docs 

## Tecnologias Ultilizadas

- Python
- FastAPI
- SQL Server
- Inteligencia Artificial (scikit-learn)

## Próximos passos

- Finalizar README
- Testes finais no Swagger
- Publicar no GitHub
- Front End
- IA com modelo treinado pelo usuario

