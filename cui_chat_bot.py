# embeddingsのapi
import openai

# vector indexのapi
import pinecone

# api keyの管理
import os
from dotenv import load_dotenv

load_dotenv('.env')

# pinecone
YOUR_API_KEY = os.getenv("YOUR_API_KEY")
YOUR_ENVIRONMENT = os.getenv("YOUR_ENVIRONMENT")
pinecone.init(api_key=YOUR_API_KEY, environment=YOUR_ENVIRONMENT)
index = pinecone.Index("shin-uni-teacher")

# gpt-api
openai.api_key = os.getenv("OPEN_AI_API_KEY")
def call_api(message):
          # message_role =[{"role": "system", "content": """Answer the following questions in Japanese for each laboratory at Shinshu University using some of the following websites. 
          #           If you cannot find the answer on a part of the site, we do not know. Answer with "I don't know."""}]
          message_role =[{"role": "system", "content": """以下は学生がどの研究室に応募しようか迷っている学生の質問にです。付属の情報を利用して学生の興味や関心にあった研究室を2つか3つ提案しなさい。
                          付属の情報からわからない場合は、正直にわからないと回答しなさい。"""}]
          message_all = message_role + message
          # print(messages)
          response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages = message_all,
          )
          return response.choices[0]["message"]["content"].strip()

# embeddings
def encode_text(input_message):
          
          response = openai.Embedding.create(
          input= input_message,
          model="text-embedding-ada-002"
          )
          embeddings = response['data'][0]['embedding']
          return embeddings

# teacher_id -> pinecone_id
def get_id(teacher_id):
          first = 6 * (int(teacher_id) - 1) + 1
          last = first + 5
          return [i for i in range(first, last+1)]




# 毎回リセットする    
# messages = [] 

print("----- gpt-3.5-turbo start ----")
print("""## type "exit" to quite ##""")
print("")
# print("role:", end=" ")
# role = input()
# messages.append({"role": "system", "content": role})

print("こんにちは。")

while True:
    # 毎回リセットする    
    messages = [] 
    
    print("信州大学電子情報システム工学科の研究室への質問は何かありますか?")
    print("質問: ", end ="")
    
    chat = input()
    if chat == "exit":
        break

    # 入力をembeddingsする
    vector_chat = encode_text(chat)
    # pineconeで検索する 上位3つを取得
    # result = index.query(vector=vector_chat,top_k=3,include_metadata=True, filter={'status': 'outline', 'status': 'discription', 'status': 'profile'})
    result = index.query(vector=vector_chat,top_k=3,include_metadata=True)
    
    # pineconeから関連のある教員データを再取得
    pinecone_id = []
    teacher_list = []
    for match in result['matches']:
          teacher_id = match['metadata']['teacher_id']
          # print(match['metadata']['name'])
          # print(match['metadata']['text'])
          teacher_list.append(teacher_id)
          pinecone_id += get_id(teacher_id)
          
    result = ""
    pinecone_list = list(set(pinecone_id))
    # print(pinecone_list)
    pinecone_list.sort()
#     print(pinecone_list)
    for pinecone_id in pinecone_list:
              data_all = index.fetch(ids=[f'{pinecone_id}'])
              data = data_all['vectors'][f'{pinecone_id}']['metadata']
            #   print(data['name'])
              if data['teacher_id'] not in teacher_list:
                        continue
              if data['status'] == 'teacher_name':
                        name = '名前:' + data['text']
                        result += name
              elif data['status'] == 'outline':
                        study = '研究の概要:' + data['text']
                        result += study
              elif data['status'] == 'discription':
                        study = '研究紹介:' + data['text']
                        result += study
              elif data['status'] == 'study-future':
                        study = '研究から始まる未来:' + data['text']
                        result += study
              elif data['status'] == 'graduation-future':
                        study = '研究から始まる未来:' + data['text']
                        result += study
              elif data['status'] == 'profile':
                        study = 'プロフィール:' + data['text'] + ', '
                        result += study
          
              
    # gpt-apiへ入力
    
    print("...")
    question = "質問: " + chat +". " "以下がweb siteの一部です: " + result
#     print(question)
    messages.append({"role": "user", "content": question})
    responcse = call_api(messages)
    print(responcse)
    print("")
    print("回答には間違っている情報が含まれている可能性があります。ホームページを確認して見てください。")
    print("")
#     messages.append({"role": "assistant", "content": responcse})