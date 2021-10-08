# Aqui aplicamos o VADER na tabela de tweets retornada via webscrapping.
#  1. Classificamos cada tweet via VADER
#  2. Aplicamos média diária ponderada por followers para agrupar por dia

import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns,plotly.graph_objects as go
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

# Definindo função com Vader para sentimentos
def sentiment_scores(tweet, followers, likes, retweets):
    """Análise de sentimento ponderada de tweets usando VADER

    Args:
        tweet (str): Tweet, textual
        followers (int): Número de followers
        likes (int): Número de likes (do Tweet)
        retweets (int): Número de retweets (do Tweet)

    Returns:
        [float]: Polarização ponderada do tweet, variando entre [-1,1].
        Segue a conta: Polarização = tweet * (followers) * (likes+1)*(retweets+1)
        * Se followers = 0, assumimos que é bot e a polarização é 0 (neutra)
        * Se likes = 0, não zeramos (por isso o +1), pois a obs ainda é importante
        * Se retweets = 0, não zeramos (por isso o +1), pois a obs ainda é importante
    """
    # Objeto para análise de sentimento
    sent_an = SentimentIntensityAnalyzer()
 
    #o método abaixo retorna um dicionário de polarizades, com pontuação % para polaridades
    # positiva, neutra, negativa e composta. Esta última normaliza os resultados entre -1 e 1
    sentiment_dict = sent_an.polarity_scores(tweet)
 
    # Usando a polarização composta supracitada para definir a pontuação do texto.
    # Como vamos ponderar por número de followers, vamos manter compound como numérico
    return sentiment_dict['compound']*(followers)*(likes+1)*(retweets+1)
 
# Função para limpar tweets
def limpa(text):
    """Limpa conteúdo desnecessário de tweets

    Args:
        tweet (str): Tweet em texto

    Returns:
        [str]: Tweet tratado
    """
    #remove RT (retweets)
    text = re.sub("RT @[\w]*:","",text)
    #remove referências a usuários
    text = re.sub("(@[A-Za-z0-9_]+)","", text)
    #remove URLs
    text = re.sub("https?://[A-Za-z0-9./]*","",text)
    # remove espaços extra
    text = ' '.join(text.split())
    return text

# Carregando JSON de Tweets:
df = pd.read_json('tweets.json',lines = True)
# df.head(3) #checando formato

#Trazendo número de seguidores para fora do dict de dados do usuário:
df['followers'] = df['user'].apply(lambda x: x['followersCount'])

#Selecionando as colunas que serão necessárias para análise e checando:
df = df[['date','content','retweetCount','lang','hashtags','followers','likeCount']]
# df.head(3)
#Podemos perceber que os dados que podem levar à identificação do usuário já foram parcialmente removidos, restando "content"

# Aqui removemos todas os tweets que não são em inglês, para que o VADER funcione:
print(df.shape[0],' Linhas pré seleção de idioma!')
df.query('lang=="en"',inplace=True)
print(df.shape[0],' Linhas pós seleção de idioma!')

# Checando se existem NaNs no conteúdo dos Tweets:
print(df['content'].isna().sum(), "NaNs encontrados nos tweets")

# Removemos a coluna de linguagem pois não é mais relevante:
df.drop(columns='lang',inplace=True)

#Aplica limpador de tweets para melhorar performance do VADER:
df['content'] = df['content'].apply(lambda x:limpa(x))

# Em seguida, aplicamos a função de sentiment_scores definidas no preâmbulo, com os pesos:
df['sentiment'] = df.apply(lambda x: sentiment_scores(x['content'],x['followers'], x['likeCount'],x['retweetCount']), axis=1)

# Aqui agrupamos por hora e somamos os scores:
df=df.groupby(pd.Grouper(key='date',freq='H'), as_index=True)[['sentiment']].sum()

# Então exportamos para um CSV para fazer tanto a análise quanto treinar o algoritmo:
df.to_csv('db_tweets.csv')

