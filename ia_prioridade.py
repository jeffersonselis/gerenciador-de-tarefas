from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
modelo = make_pipeline(CountVectorizer(),MultinomialNB())
tarefas = ["lavar o carro","pagar conta urgente","comprar pão","regar planta depois","estudar ingles hj","pegar remedio na farmacia urgemte",
"levar o filho no hospital","estudar python","organizar gaveta",]
prioridades = ["baixa","alta","baixa","baixa","média","alta","alta","média","baixa"]
modelo.fit(tarefas,prioridades)

  