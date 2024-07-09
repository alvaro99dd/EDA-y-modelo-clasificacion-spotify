import kaggle
import opendatasets as od

# kaggle.api.download_file("nelgiriyewithana/world-stock-prices-daily-updating", outfile=r"C:\Users\NITROPC\Desktop\Bootcamp\Temario\Modulo_3\Proyecto\stock_prices.csv")
# kaggle.api.dataset_download_file(dataset="nelgiriyewithana/world-stock-prices-daily-updating", file_name="stock_prices.csv", path=r"C:\Users\NITROPC\Desktop\Bootcamp\Temario\Modulo_3\Proyecto")
# Assign the Kaggle data set URL into variable
dataset = 'https://www.kaggle.com/datasets/nelgiriyewithana/world-stock-prices-daily-updating/data'
# Using opendatasets let's download the data sets
od.download(dataset)