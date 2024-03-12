import requests

url = 'https://pluto.tv/en/on-demand?utm_source=google&utm_medium=paidsearch&utm_campaign=12080790684&utm_term=pluto+tv&utm_creative=617765758688&device=c&campaign=Search_Brand_Desktop_E&gad_source=1&gclid=EAIaIQobChMIg--hmNrUgwMVw0dHAR06tgZnEAAYASAAEgK8yvD_BwE'

response = requests.get(url)

json_data = response.json()

print(json_data)
