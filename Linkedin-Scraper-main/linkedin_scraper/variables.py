from dotenv import load_dotenv

load_dotenv()

my_username = 'your_mail'
my_password = 'your_password'
num_pages = 30

file_name = '../Data/Scraped/AI.csv'  # file where the results will be saved

query = 'site:linkedin.com/in/ AND "ESPRIT" AND "Artificial Intelligence" OR "Intelligence Artificielle"'
