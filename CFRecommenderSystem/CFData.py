import surprise as surp
import pandas as pd
class CFData:
    def __init__(self, df_rating, test_ratio=None, df_id_name_table=None, rating_scale=(1, 5)):
        """
        Initialize collaborative filtering data class
        :param df_rating: pandas dataframe containing columns: 'userID', 'itemID', 'rating' in correct order
        :param df_id_name_table: table to convert itemID to readable item name (like movie title). 
                                 dataframe containg columns: 'itemID' and 'itemName' in correct order
        :return: None
        Eg: 
            df_id_name_table = df_movie[['movieId', 'title']].\
                rename(index=str, columns={'movieID':'itemID', 'title':'itemName'})
            cfdata_example = CFData(data, df_id_name_table)
            cfdata_example.convert_name_to_id('Toy Story (1995)')
            cfdata_example.convert_id_to_name(1)
        """      
        reader = surp.Reader(rating_scale=rating_scale)
        rating_data = surp.Dataset.load_from_df(df_rating, reader)
        self.trainset = rating_data.build_full_trainset()
  
        if test_ratio is not None:
            self.trainset, self.testset = surp.model_selection.train_test_split(data=rating_data, test_size=test_ratio)
        else:
            self.trainset = rating_data.build_full_trainset()

        # self.__dict_id_to_name: id_1: [name1_1, name1_2...], id_2: [name2_1, name2_2....]
        # self.__dict_name_to_id: name1: [id1_1, id1_2...], name2: [id2_1, id2_2...]
        if df_id_name_table is not None:
            self.__dict_id_to_name = df_id_name_table.groupby('itemID')['itemName'].apply(lambda x: x.tolist()).to_dict()
            self.__dict_name_to_id = df_id_name_table.groupby('itemName')['itemID'].apply(lambda x: x.tolist()).to_dict()
              
    def convert_name_to_id(self, item_name):
        """
        Convert item name to item id
        :param item_name: item name
        :return: item id if single id is found
                 None if nothing or multiple id's are found
        """  
        if item_name not in self.__dict_name_to_id or len(self.__dict_name_to_id[item_name]) > 1:
            return None
        return self.__dict_name_to_id[item_name][0]
        
    def convert_id_to_name(self, item_id):
        """
        Convert item id to item name
        :param item_id: item id
        :return: item name if single name is found
                 None if nothing or multiple id's are found
        """
        if item_id not in self.__dict_id_to_name or len(self.__dict_id_to_name[item_id]) > 1:
            return None
        return self.__dict_id_to_name[item_id][0]
