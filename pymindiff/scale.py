class MinMaxScaler():
    def fit_transform(self, data):
        self.min = data.min()
        self.max = data.max()
        for column in data.columns.values:
            data[column] = data[column].apply(lambda x : (x - self.min[column]) / (self.max[column] - self.min[column]))
        return data

    def inverse_transform(self, data):
        for column in data.columns.values:
            data[column] = data[column].apply(lambda x : x * (self.max[column] - self.min[column]) + self.min[column])
        return data