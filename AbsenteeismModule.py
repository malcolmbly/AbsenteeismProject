#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin


# the custom scaler class 
class CustomScaler (BaseEstimator, TransformerMixin):
    
    def __init__(self, columns, copy=True, with_mean=True, with_std=True):
        self.scaler = StandardScaler(copy,with_mean,with_std)
        self.columns=columns
        self.mean=None
        self.var_=None
    
    def fit(self, X, y=None):
        self.scaler.fit(X[self.columns], y)
        self.mean_= np.array(np.mean(x[self.Columns]))
        self.var_ = np.array(np.var(x[self.Columns]))
        return self
    
    def transform (self, y=None, copy=None):
        init_col_order=X.columns
        X_scaled = pd.Dataframe(self.scaler.transform(X[self.columns]), columns = self.columns)

        
class absenteeism_model():
    
    def __init__(self, model_file, scaler_file):
        with open ('model', 'rb') as model_file, open('scaler', 'rb') as scaler_file:
            self.reg= pickle.load(model_file)
            self.scaler=pickle.load(scaler_file)
            self.data = None
            
    # take a data file (*.csv) and preprocess it in the same way as in the lectures       
    def load_and_clean_data (self, data_file):
        # import the data
        df= pd.read_csv(data_file)

        # drop the 'ID' column        
        df= df.drop('ID', axis=1)
        # create a separate dataframe, containing dummy values for ALL avaiable reasons        
        reason_columns=pd.get_dummies(df['Reason for Absence'], drop_first= True)

        df=df.drop(['Reason for Absence'], axis=1)
        # split reason_columns into 4 types
        reason_1= reason_columns.loc[:, 1:14].max(axis=1)
        reason_2= reason_columns.loc[:, 15:17].max(axis=1)
        reason_3= reason_columns.loc[:, 18:21].max(axis=1)
        reason_4= reason_columns.loc[:, 22:].max(axis=1)

        # concatenate df and the 4 types of reason for absence
        df= pd.concat([df, reason_1, reason_2, reason_3, reason_4], axis=1)
        # add column names
        column_names = ['Date', 'Transportation Expense', 'Distance to Work', 'Age',
                           'Daily Work Load Average', 'Body Mass Index', 'Education', 'Children',
                           'Pet', 'Reason_1', 'Reason_2', 'Reason_3', 'Reason_4']
        
        df.columns = column_names
        # convert the 'Date' column into datetime
        df['Date'] = pd.to_datetime(df['Date'], format= '%d/%m/%Y')
        # create a list with month values retrieved from the 'Date' column
        list_months=[]
        for i in df['Date']:
            list_months.append(i.month)
                               
        # insert the values in a new column in df, called 'Month Value'    
        df['Month Value']= list_months
        # create a new feature called 'Day of the Week'
        df['Day of the Week'] =  df['Date'].apply(lambda x: x.weekday())
        
        df= df.drop(['Date'], axis=1)
        df = df.fillna(value=0)
        # re-order the columns in df
        column_names_upd = ['Reason_1', 'Reason_2', 'Reason_3', 'Reason_4', 'Month Value', 'Day of the Week',
                                'Transportation Expense', 'Distance to Work', 'Age',
                                'Daily Work Load Average', 'Body Mass Index', 'Education', 'Children',
                                'Pet']
        df = df[column_names_upd]
        # map 'Education' variables; the result is a dumm
        df['Education']= df['Education'].map({2:1, 3:1, 4:1, 1:0})                     
        # drop the variables we decide we don't need
        df = df.drop(['Day of the Week','Daily Work Load Average','Distance to Work'],axis=1)
        
        #create properties to be used in other methods
        self.preprocessed_data = df.copy()
        self.data = self.scaler.transform(df)
    
    # a function which outputs the probability of a data point to be 1
    def predicted_probability(self):
        if (self.Data is not None):
            pred = self.reg.predict_proba(self.data)[:,1]
            return pred
    
    # a function which outputs 0 or 1 based on our model
    def predicted_output_category(self):
        if (self.data is not None):
            pred_outputs = self.reg.predict(self.data)
            return pred_outputs

    # predict the outputs and the probabilities and 
    # add columns with these values at the end of the new data
    def predicted_outputs(self):
        if (self.data is not None):
            self.preprocessed_data['Probability'] = self.reg.predict_proba(self.data)[:,1]
            self.preprocessed_data ['Prediction'] = self.reg.predict(self.data)
            return self.preprocessed_data

