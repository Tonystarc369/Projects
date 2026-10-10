import os
import numpy as np
import pandas as pd

print("Enter the excel file path to load the portfolio data: ")
excel_path = input().strip()

class risk_engine:
    def load_excel_file(self,filepath: str)-> pd.DataFrame:
        if os.path.exists(filepath):
            df=pd.read_excel(filepath)
            return df
        else:
            raise FileNotFoundError("File not found, check the path !!")
            #print(f"File not found at {filepath}, check the path !!")
    
    
    def mtm_values(self,df: pd.DataFrame)-> pd.DataFrame:
        uniq_list=df['company'].unique().tolist()
        net=0;mtmvalues=[];
        mtm_total_exposure = df.groupby('company')['value'].sum().reset_index()
        return mtm_total_exposure
    
test=risk_engine().mtm_values(risk_engine().load_excel_file(excel_path))
print(test)