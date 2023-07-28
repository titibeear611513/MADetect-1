
import openai

with open('./static/doc/apikey.txt', 'r') as file:
    apikey = file.read().rstrip()

openai.api_key = apikey

ad_text = input("Enter the advertisement sentence you want to check: ")

responce = openai.ChatCompletion.create(
  model = "gpt-3.5-turbo",
  messages = [
    {"role": "system", "content": "You are a helpful Legal Consultant."},
    {"role": "user", "content": "請告訴我此廣告詞是否與醫療行為相關: " + ad_text},
  ]
)

result = responce['choices'][0]['message']['content']
print(result)