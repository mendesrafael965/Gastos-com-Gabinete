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

    def get_cabinet_table(self, payload) -> None:
        response = self.__extract_cabinet_table(payload)
        response = self.__transform_cabinet_table(response)
        response = self.__transform_df(response)
        self.__load_cabinet_table(response)
    
    def __extract_cabinet_table(self, payload):
        response = requests.post('https://www.saopaulo.sp.leg.br/transparencia/salarios-abertos/salarios-abertos/remuneracao-dos-servidores-e-afastados/', verify=False, data=payload).text
        return response

    def __transform_cabinet_table(self, response):
        soup = BeautifulSoup(response, 'html.parser')
        result  = str(soup.find('table'))
        return result
    
    def __transform_df(self, response):
        result = pd.read_html(response, encoding='UTF-8')
        result = result[0]
        return result
    
    def __load_cabinet_table(self, df) -> None:
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