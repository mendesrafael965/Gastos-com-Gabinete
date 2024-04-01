from io import StringIO
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

class WEBCRAWLER():
    
    def __rename_columns(self, df) -> None:
        n_cols = df.shape[1]
        new_name_columns = ['Col_'+str(i) for i in range(1,n_cols+1)]
        return new_name_columns
    
    def __find_index_cabinet(self, df):
        indicies_cabinet = list(df[df['Col_1'].str.contains(r'[0-9][1-9]º GABINETE DE VEREADOR')].index)
        equal_columns = df[(df['Col_1']==df['Col_2']) & (df['Col_2']==df['Col_3'])].index
        indicies_cabinet.append(equal_columns[equal_columns > indicies_cabinet[-1]][0])
        return indicies_cabinet

    def __extract_table(self, objeto, payload=''):
        if objeto == 'cabinet':
            response = requests.post(
                'https://www.saopaulo.sp.leg.br/transparencia/salarios-abertos/salarios-abertos/remuneracao-dos-servidores-e-afastados/', 
                verify=False, 
                data=payload
                ).text
        elif objeto == 'councilor':
            response = requests.get(
                'https://www.saopaulo.sp.leg.br/atividade-legislativa/gabinetes/', 
                verify=False
                ).text
        return response

    def __transform_cabinet_table(self, response):
        soup = BeautifulSoup(response, 'html.parser')
        result  = str(soup.find('table'))
        return result
    
    def __transform_df(self, response, format_in):
        if format_in == 'html':
            result = pd.read_html(response, encoding='UTF-8')
            result = result[0]
        elif format_in  == 'xml':
            result = pd.read_xml(StringIO(response))
        return result
    
    def __load(self, df, objeto) -> None:
        if objeto == 'cabinet':
            new_name_columns = self.__rename_columns(df)
            df.columns = new_name_columns
            index_cabinet = self.__find_index_cabinet(df)

            i = 0
            for i in range(len(index_cabinet)-1):
                file_name = df.iloc[index_cabinet[i],0]
                col_names = list(df.iloc[index_cabinet[i]+1].values)

                df_i = df.iloc[index_cabinet[i]+2:index_cabinet[i+1]]
                df_i.columns=col_names
                df_i.to_excel('gabinetes' + os.sep + file_name + '.xlsx', index=None)
                i += 1

        elif objeto == 'councilor':
            df.to_excel('gabinete_vereador'+ os.sep +'gabinete_vereador.xlsx', index=None)

        elif objeto == 'employees':
            df.to_excel('funcionarios'+ os.sep +'Funcionarios.xlsx', index=None)

    def __extract_employees(self):
        response = requests.get('https://www.saopaulo.sp.leg.br/static/transparencia/funcionarios/CMSP-XML-Funcionarios.xml', verify=False)
        return response

    def __transform_employees(self, response):
        response.encoding = response.apparent_encoding
        result = response.text
        return result
    
    def get_cabinet_table(self, payload) -> None:
        response = self.__extract_table(objeto='cabinet', payload=payload)
        response = self.__transform_cabinet_table(response)
        response = self.__transform_df(response, format_in='html')
        self.__load(response, objeto='cabinet')

        response = self.__extract_employees()
        response = self.__transform_employees(response)
        response = self.__transform_df(response, format_in='xml')
        self.__load(response, objeto='employees')

        response = self.__extract_table(objeto='councilor')
        response = self.__transform_df(response, format_in='html')
        self.__load(response, objeto='councilor')