class CFModel:
# Simplified method to train Surprise collaborative filtering model
    def __init__(self, model, *args, **kwargs):
             
        self.model = model(*args, **kwargs)
    
    def fit(self, data_train):
             
        self.model.fit(data_train)
    
    def get_similar_item(self, input_item_id, num_neighbor):
              
        # Convert input item_id to inner id generated during training
        input_inner_id = self.model.trainset.to_inner_iid(input_item_id)
        
        # 'sim' method is used to execute get_neighbors like KNN method
        
        if 'sim' in dir(self.model):
            # get a list of inner_id. Need to convert to item_id
            neighbor_inner_id = self.model.get_neighbors(input_inner_id, k=num_neighbor) 
            
            return [self.model.trainset.to_raw_iid(inner_id) for inner_id in neighbor_inner_id]
        else:
            return self.__get_top_similarities(input_inner_id, num_neighbor)
            

    def __get_top_similarities(self, item_inner_id, k):
             
        # Get TOP-k similar item for matix factorization model
        from math import sqrt
        def cosine_distance(vector_a, vector_b):
            ab = sum([i*j for (i, j) in zip(vector_a, vector_b)])
            a2 = sum([i*i for i in vector_a])
            b2 = sum([i*i for i in vector_b])
            eta = 1./10**9
            return 1.0 - ab/sqrt((a2+eta)*(b2+eta))
                
        # obtain the vector representation of input item
        item_vector = self.model.qi[item_inner_id]
        similarity_table = []
    
        for other_inner_id in self.model.trainset.all_items():
            if other_inner_id == item_inner_id:
                continue
            other_item_vector = self.model.qi[other_inner_id]
            similarity_table.append((cosine_distance(other_item_vector, item_vector), 
                                     self.model.trainset.to_raw_iid(other_inner_id)
                                    )) 
        similarity_table.sort()
        if k > len(similarity_table):
            return [i[1] for i in similarity_table]
        else:
            return [i[1] for i in similarity_table[0:k]]
