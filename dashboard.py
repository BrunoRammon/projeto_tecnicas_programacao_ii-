import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from ast import literal_eval
import plotly.express as px
import streamlit as st

# Initial setting up 
pd.set_option('display.max_columns', 500)
# plt.rcParams['figure.figsize'] = [24, 9]
# plt.rcParams['font.size'] = 24
sns.set()

# Functions

def get_columns_part(df,parts = []):
    columns = []
    for column in df.columns:
        column_formmatado = column[0]
        if column_formmatado[:2] in parts:
            columns.append(column)
    return columns

def clean_column_names(columns_df):
    try:
        new_names = [col[1] for col in columns_df] 
    except:
        new_names = columns_df
    
    return new_names

def get_columns_question(df,part,question):
    df_part = df[get_columns_part(df,parts = [part])]
    columns = [col for col in df_part.columns if col[0].split('_')[1]== question]
    return columns

def get_question(df,part,question):
    df_question = df[get_columns_question(df,part,question)]
    
    df_question.columns = clean_column_names(df_question.columns)
    
    if len(df_question.columns) > 1:
        level_0_name = df_question.columns[0]
        df_question = df_question[df_question.columns[1:]]
        df_question.columns = pd.MultiIndex.from_product([[level_0_name],df_question.columns])
    
    return df_question

def range_char(start, stop):
    
    return (chr(n) for n in range(ord(start), ord(stop) + 1))

def get_part(df,part):
    cols_part = get_columns_part(df,parts=[part])
    
    min_question = cols_part[1][0].split('_')[1]
    max_question = cols_part[-1][0].split('_')[1]
    
    questions = range_char(min_question,max_question)
    
    df_part = pd.concat([get_question(df,part,question) for question in questions],axis=1)
    return df_part

def plot_heat_map(dataframe,annotate,figsize,title=''):
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(dataframe, annot=annotate, cmap='plasma', fmt=".0f")
    ax.set_title(title)
    return fig


def stacked_bar(dados,titulo):
    fig, ax = plt.subplots(figsize=(4, 3))
    dados.plot(kind='bar', stacked=True, rot=0,width = 0.35, ax=ax)
    plt.title(label= titulo ,fontsize=15)
    plt.gca().set_frame_on(False)
    plt.gca().axes.get_yaxis().set_visible(False)
    for c in ax.containers:

        labels = [f'{round(v.get_height(),1)}%'if v.get_height() > 0 else '' for v in c]

        ax.bar_label(c, labels=labels, label_type='center', color='white')
        
    return fig

def bar_plotly(df,pergunta,titulo,cor,x_label,y_label,top=0):
    respostas = list(df[pergunta])[:]
    if not top:
        top = len(respostas)
    dados = df[pergunta][respostas].sum().sort_values(ascending=False).to_frame()[:top]
    fig = px.bar(dados,title=titulo,color_discrete_sequence=[cor])
    fig.update_layout(xaxis_title=x_label)
    fig.update_layout(yaxis_title=y_label)
    fig.update_layout(showlegend=False)
    return fig

def set_up_main_dataframe(career):
    df_all = pd.read_csv('./datasets/State of Data 2021 - Dataset - Pgina1.csv')
    df_all = df_all[df_all["('P1_e_b ', 'Regiao onde mora')"] != 'Exterior'].reset_index(drop=True)
    df_all.columns=[col.replace("'s","s") for col in df_all.columns]
    df_all.columns=[col.replace("P2_q","P2_p") for col in df_all.columns]
    df_all.columns=[col.replace("P2_r","P2_q") for col in df_all.columns]
    df_all.columns=[col.replace("P2_s","P2_r") for col in df_all.columns]
    df_all.columns = [literal_eval(col) for col in df_all.columns]
    df_all.columns = [(col[0].strip(),col[1].strip()) for col in df_all.columns]
    df_filtered_by_career = df_all[df_all[('P4_a', 'Atuacao')]==career]
    return df_filtered_by_career

def set_up_main_dataframe_demography_data(df_filtered_by_career):
    #getting P1
    part = 'P1'
    df_dem = get_part(df_filtered_by_career,part)
    df_dem = df_dem[[('Idade','Faixa idade'),('Estado onde mora', 'Regiao onde mora'),
            'Nivel de Ensino','??rea de Forma????o','Genero']]
    df_dem.rename(columns = {('Idade','Faixa idade'):'Faixa idade',
                ('Estado onde mora', 'Regiao onde mora'): 'Regiao onde mora'},inplace=True)
    return df_dem

def set_up_main_dataframe_career_data(df_filtered_by_career):
    #getting P2
    part = 'P2'
    df_career = get_part(df_filtered_by_career,part)
    df_career['Faixa salarial'] = df_career['Faixa salarial'].str.replace('de ','')
    df_career['Faixa salarial'] = df_career['Faixa salarial'].str.replace('Menos ','<')
    df_career['Faixa salarial'] = df_career['Faixa salarial'].str.replace('Acima ','>')
    df_career['Faixa salarial'] = df_career['Faixa salarial'].str.replace('R\$ ','',regex=True)
    df_career['Faixa salarial'] = df_career['Faixa salarial'].str.replace('/m??s','')
    df_career['Faixa salarial'] = df_career['Faixa salarial'].str.replace(' a ','-')

    df_career['Quanto tempo de experi??ncia na ??rea de dados voc?? tem?'] =\
    df_career['Quanto tempo de experi??ncia na ??rea de dados voc?? tem?'].str.replace('de ','')
    df_career['Quanto tempo de experi??ncia na ??rea de dados voc?? tem?'] =\
    df_career['Quanto tempo de experi??ncia na ??rea de dados voc?? tem?'].str.replace('Menos ','<')
    df_career['Quanto tempo de experi??ncia na ??rea de dados voc?? tem?'] =\
    df_career['Quanto tempo de experi??ncia na ??rea de dados voc?? tem?'].str.replace('Mais ','>')
    df_career['Quanto tempo de experi??ncia na ??rea de dados voc?? tem?'] =\
    df_career['Quanto tempo de experi??ncia na ??rea de dados voc?? tem?'].str.replace(' a ','-')
    df_career['Quanto tempo de experi??ncia na ??rea de dados voc?? tem?'] =\
    df_career['Quanto tempo de experi??ncia na ??rea de dados voc?? tem?'].str.replace('N??o tenho experi??ncia na ??rea dados',
                                                                                    'Sem experi??ncia')
    df_career = df_career[['Faixa salarial','Quanto tempo de experi??ncia na ??rea de dados voc?? tem?',
            'Atualmente qual a sua forma de trabalho?','Qual a forma de trabalho ideal para voc???',
            'Nivel']]
    return df_career

def set_up_main_dataframe_knowhow_data(df_filtered_by_career):
    #getting P3    
    part = 'P4'
    df_knowledge = get_part(df_filtered_by_career,part)
    df_knowledge = df_knowledge[['Entre as linguagens listadas abaixo, qual ?? a que voc?? mais utiliza no trabalho?',
                'Quais dos bancos de dados/fontes de dados listados abaixo voc?? utiliza no trabalho?',
                'Quais as Ferramentas de Business Intelligence voc?? utiliza no trabalho?',
                'Quais das op????es de Cloud listadas abaixo voc?? utiliza no trabalho?']]
    return df_knowledge

############################### STREAMLIT APP ################################################
# plt.rcParams.update({'font.size': 5})
with st.sidebar:
    career = st.radio(
        "Selecione o tipo de gr??fico",
        ("An??lise de Dados", "Ci??ncia de Dados", "Engenharia de Dados")
    )

df_main = set_up_main_dataframe(career)
df_dem = set_up_main_dataframe_demography_data(df_main)
df_career = set_up_main_dataframe_career_data(df_main)
df_knowledge = set_up_main_dataframe_knowhow_data(df_main)


st.header('Um vis??o geral dos diferentes perfis de profissionais de dados')
st.markdown('#### Introdu????o')
st.write("""
No per??odo entre 18 de outubro de 2021 e 6 de dezembro de 2021, a maior comunidade de dados do Brasil,o Data Hackers juntamente com a consultoria global Bain & Company realizaram uma pesquisa por meio da aplica????o de um question??rio online, cujo objetivo ?? mapear o mercado profissional de dados brasileiro. A pesquisa compreendeu as seguintes dimens??es:

(1) dados demogr??ficos, (2) dados sobre a carreira, (3) desafios de gestores de times de dados, (4) conhecimentos na ??rea de dados, (5) objetivos na ??rea de dados, (6) conhecimentos de engenharia de dados, (7) an??lise de dados, (8) ci??ncia de dados, e (9) engajamento com a comunidade DH.

Em Maio de 2022, foram abertos os dados da pesquisa, para que a comunidade pudesse realizar suas pr??prias an??lises, concorrendo a pr??mios, mas tamb??m podendo contar com o privil??gio de grandes profissionais da ??rea como jurados dessa competi????o.
""")

st.markdown('### Descri????o de base de dados')
col1, col2, col3 = st.columns(3)
col1.metric("Respostas:", "2645")
col2.metric("Vivem no Brasil:", "2592")
col3.metric("Trabalham (AD | CD | ED):", "1635")
st.metric(
    label='',
    value=len(df_dem),
    delta=f"Profissionais da ??rea de {career}",
    delta_color = 'off'
)
st.markdown('#### Parte 1 - Dados demogr??ficos')
st.markdown('- Faixa idade')
st.markdown('- Regiao onde mora')
st.markdown('- Nivel de Ensino')
st.markdown('- ??rea de Forma????o')
st.markdown('- Genero')
st.dataframe(df_dem)
st.markdown('#### Parte 2 - Dados sobre carreira')
st.markdown('- Faixa salarial')
st.markdown('- Quanto tempo de experi??ncia na ??rea de dados voc?? tem?')
st.markdown('- Atualmente qual a sua forma de trabalho?')
st.markdown('- Qual a forma de trabalho ideal para voc???')
st.markdown('- Nivel')
st.dataframe(df_career)
st.markdown('#### Parte 4 - Conhecimentos na ??rea de dados')
st.markdown('- Entre as linguagens listadas abaixo, qual ?? a que voc?? mais utiliza no trabalho?')
st.markdown('- Quais dos bancos de dados/fontes de dados listados abaixo voc?? utiliza no trabalho?')
st.markdown('- Quais as Ferramentas de Business Intelligence voc?? utiliza no trabalho?')
st.markdown('- Quais das op????es de Cloud listadas abaixo voc?? utiliza no trabalho?')
st.dataframe(df_knowledge)

st.header('Dados demogr??ficos')


# st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)

# st.markdown("""
# <nav class="navbar fixed-top navbar-expand-lg navbar-dark" style="background-color: #3498DB;">
#   <a class="navbar-brand" href="https://youtube.com/dataprofessor" target="_blank">Data Professor</a>
#   <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
#     <span class="navbar-toggler-icon"></span>
#   </button>
#   <div class="collapse navbar-collapse" id="navbarNav">
#     <ul class="navbar-nav">
#       <li class="nav-item active">
#         <a class="nav-link disabled" href="#">Home <span class="sr-only">(current)</span></a>
#       </li>
#       <li class="nav-item">
#         <a class="nav-link" href="https://youtube.com/dataprofessor" target="_blank">YouTube</a>
#       </li>
#       <li class="nav-item">
#         <a class="nav-link" href="https://twitter.com/thedataprof" target="_blank">Twitter</a>
#       </li>
#     </ul>
#   </div>
# </nav>
# """, unsafe_allow_html=True)

#plot 1
fig, ax = plt.subplots(figsize=(10, 5))
age_class_dist = df_dem['Faixa idade'].value_counts().sort_index()
age_class_dist.plot(kind='bar',title='Distribui????o de faixas et??rias',grid=False,subplots=False);
plt.xticks(rotation=0)
for i, val in enumerate(age_class_dist, start=0):
    ax.annotate(text = str(val), xy=(i-0.18,val))

st.pyplot(fig)

#plot 2
fig, ax = plt.subplots(figsize=(10, 5))
region_freq = df_dem['Regiao onde mora'].value_counts()
width = 0.5
region_freq.plot(kind='barh',title='N??mero de profissionais por regi??o',grid=False,subplots=False,width = width);
for i, val in enumerate(region_freq, start=0):
    ax.annotate(text = str(val), xy=(val,i-0.06))

st.pyplot(fig)


#plot 3
order_level_degree = {'P??s-gradua????o':3, 'Doutorado ou Phd':5, 'Gradua????o/Bacharelado':2,
           'N??o tenho gradua????o formal':0, 'Estudante de Gradua????o':1, 'Mestrado':4}

fig, ax = plt.subplots(figsize=(10, 5))
education_freq = df_dem['Nivel de Ensino'].value_counts().sort_index(key=lambda x : x.map(order_level_degree))
education_freq.plot(kind='area',title='N??mero de profissinais por n??vel de ensino',grid=False,subplots=False,stacked=False);
plt.xticks(rotation=90)

for i, (idx,val) in enumerate(education_freq.iteritems(), start=0):
    ax.annotate(text = str(val), xy=(i, val))

st.pyplot(fig)

#plot 4
dic_areas = {'Computa????o / Engenharia de Software / Sistemas de Informa????o/ TI':'Computa????o',
       'Outras Engenharias':'Engenharias',
       'Economia/ Administra????o / Contabilidade / Finan??as':'Administra????o',
       'Marketing / Publicidade / Comunica????o / Jornalismo':'Comunica????o',
       'Estat??stica/ Matem??tica / Matem??tica Computacional':'Exatas', 
       'Qu??mica / F??sica':'Exatas',
       'Ci??ncias Biol??gicas/Farm??cia/Medicina/??rea da Sa??de':'Ci??ncias Biol??gicas'}
df_dem['??rea de Forma????o'] = df_dem['??rea de Forma????o'].apply(lambda x: dic_areas[x] if x in dic_areas else x)
df_dem['??rea de Forma????o'].unique()

fig, ax = plt.subplots(figsize=(10, 5))
degree_area_freq = df_dem['??rea de Forma????o'].value_counts()
plt.bar(x = df_dem['??rea de Forma????o'].dropna().unique(), height = degree_area_freq);
ax.set_title('N??mero de profissinais por ??rea de atua????o')
plt.xticks(rotation=90)
for i, val in enumerate(degree_area_freq, start=0):
    ax.annotate(text = str(val), xy=(i-0.18,val+2))
st.pyplot(fig)

st.header('Carreira')

salary_order = { '<1.000':0,
                 '1.001-2.000':1,
                 '2.001-3000':2,
                 '3.001-4.000':3,
                 '4.001-6.000':4, 
                 '6.001-8.000':5,
                 '8.001-12.000':6,
                 '12.001-16.000':7,
                 '16.001-20.000':8,
                 '20.001-25.000':9, 
                 '25.001-30.000':10,
                 '30.001-40.000':11,
                 '>40.001':12}
experience_order = {'1-2 anos':2, '>10 anos':6, '<1 ano':1,
       'Sem experi??ncia':0, '6-10 anos':5,
       '2-3 anos':3, '4-5 anos':4}


# plot 5
df_salary_exp = df_career[['Faixa salarial','Quanto tempo de experi??ncia na ??rea de dados voc?? tem?']].value_counts().unstack(level=1)
df_salary_exp = df_salary_exp.sort_index(key=lambda x : x.map(salary_order))
df_salary_exp = df_salary_exp[sorted(df_salary_exp.columns,key=lambda x: experience_order[x])]

# plot 6
df_salary_nivel = df_career[['Faixa salarial','Nivel']].value_counts().unstack(level=1)
df_salary_nivel = df_salary_nivel.sort_index(key=lambda x : x.map(salary_order))


# plot 7
df_salary_gender = pd.concat([df_career['Faixa salarial'],df_dem['Genero']],axis=1).value_counts().unstack(level=1)
df_salary_gender = df_salary_gender.sort_index(key=lambda x : x.map(salary_order))


st.pyplot(plot_heat_map(df_salary_exp.T,annotate=True,figsize=(9,6),
title='Faixa salarial em rela????o ao tempo de experi??ncia na ??rea'))

st.pyplot(plot_heat_map(df_salary_nivel.T,annotate=True,figsize=(6,3),
title='Faixa salarial em rela????o a senioridade'))
st.write('')
st.write('')
st.write('')
st.pyplot(plot_heat_map(df_salary_gender.T,annotate=True,figsize=(8,3),
    title='Faixa salarial em rela????o ao g??nero'))

#plot 8
dict_modelo_trabalho = {'Modelo 100% remoto':'100% remoto',
            'Modelo 100% presencial':'100% presencial',
            'Modelo h??brido flex??vel (o funcion??rio tem liberdade para escolher quando estar no escrit??rio presencialmente)':'H??brido flex??vel',
            'Modelo h??brido com dias fixos de trabalho presencial':'H??brido dias fixos'}

cols =  ['Atualmente qual a sua forma de trabalho?','Qual a forma de trabalho ideal para voc???']

for col in cols:
    df_career[col] = df_career[col].apply(lambda x: dict_modelo_trabalho[x])

modelo_trabalho_atual = df_career['Atualmente qual a sua forma de trabalho?'].value_counts().sort_index().to_frame()
modelo_trabalho_desejavel = df_career['Qual a forma de trabalho ideal para voc???'].value_counts().sort_index().to_frame()
trabalho_atual_desejavel = pd.concat([modelo_trabalho_atual,modelo_trabalho_desejavel], axis=1).T
trabalho_atual_desejavel = trabalho_atual_desejavel.div(trabalho_atual_desejavel.sum(axis=1), axis=0)*100

st.pyplot(stacked_bar(trabalho_atual_desejavel,titulo='Formas de Trabalho'))

#plot 9
df_career['Genero'] = df_dem['Genero']
nivel_genero = pd.crosstab(df_career['Nivel'],df_career['Genero']).drop(['Outro'],axis=1)
nivel_genero = nivel_genero.div(nivel_genero.sum(axis=1), axis=0)*100

st.pyplot(stacked_bar(nivel_genero,titulo='Distribui????o de g??nero por n??veis de cargo'))

st.header('Tecnologias')

#plot 10
pergunta = 'Entre as linguagens listadas abaixo, qual ?? a que voc?? mais utiliza no trabalho?'
titulo = 'Linguagens de programa????o mais utilizadas no trabalho'
cor = 'orange'
x_label = 'Linguagens'
y_label = 'Quantidade'
st.plotly_chart(bar_plotly(df_knowledge,pergunta,titulo,cor,x_label,y_label,top=8))

#plot 11
pergunta = 'Quais dos bancos de dados/fontes de dados listados abaixo voc?? utiliza no trabalho?'
titulo = 'Bancos de dados utilizados'
cor = 'dodgerblue'
x_label = 'Bancos de Dados'
y_label = 'Quantidade'
st.plotly_chart(bar_plotly(df_knowledge,pergunta,titulo,cor,x_label,y_label,top=10))

#plot 12
pergunta = 'Quais as Ferramentas de Business Intelligence voc?? utiliza no trabalho?'
titulo = 'Ferramentas de Business Intelligence mais utilizadas'
cor = 'orangered'
x_label = 'Ferramentas de B.I.'
y_label = 'Quantidade'
st.plotly_chart(bar_plotly(df_knowledge,pergunta,titulo,cor,x_label,y_label,top=10))

st.write('')
st.write('')
st.write('')

#plot 13
pergunta = 'Quais das op????es de Cloud listadas abaixo voc?? utiliza no trabalho?'
titulo = 'Principais Clouds'
cor = 'olive'
x_label = 'Cloud'
y_label = 'Quantidade'
st.plotly_chart(bar_plotly(df_knowledge,pergunta,titulo,cor,x_label,y_label))