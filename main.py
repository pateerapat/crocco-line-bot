import json, random, requests, gspread
from flask import Flask, request
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

#ดึงข้อมูล Q&A
with open('src/Q&A.json') as json_file_01:
    qa_List = json.load(json_file_01)

#ดึงข้อมูล สถานที่ภายในมหาลัย
with open('src/emoji.json') as json_file_02:
    emoji_List = json.load(json_file_02)

#ดึงข้อมูล สถานที่ภายในมหาลัย
with open('src/covid.json') as json_file_03:
    covid_Scan = json.load(json_file_03)

@app.route('/')
def hello_world():
    return "Hello world!"

@app.route('/webhook', methods=['POST'])
def webhook():
    
    #ดึงข้อความที่ผู้ใช้ส่ง
    req = request.get_json(silent=True, force=True)
    query_result = req.get('queryResult')
    
    #แสดงหมวดหมู่ Q&A
    if query_result.get('action') == "action-show-qalist":
        if query_result.get('queryText') == "ไม่ต้องการ":
            category_List = "ถ้าต้องการเลือกหมวดหมู่ข้อมูลของคำถามใหม่อีกครั้ง สามารถกดที่ปุ่ม คุยกับพี่ค๊อกโค่ -> แสดงข้อมูลคำถามในระบบ"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [
                    {
                        "text": {"text": [category_List]},
                        "platform": "LINE"
                    }
                ]
            }
        else:
            category_List = "สามารถเลือกหมวดหมู่ข้อมูลของคำถามได้โดยพิมพ์ 'ตัวเลข' หมวดหมู่ด้านล่างนี้ลงไปแล้วกดส่ง\n\nตัวอย่างเช่น พิมพ์ '1' ระบบจะแสดงข้อมูลของ 'งานประกัน'\n\nหมวดหมู่ข้อมูลของคำถามที่พบบ่อย มีดังนี้\n\n"
            for i in range(0, len(qa_List), 1):
                if i == len(qa_List)-1:
                    category_List += str(i+1)+". "+qa_List[i][0]
                else:
                    category_List += str(i+1)+". "+qa_List[i][0]+"\n"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "outputContexts" : [
                    {
                        "name" : "projects/full-crocco-qjkd/agent/sessions/00beed55-3c7d-8a47-2fc6-02f4dd100e91/contexts/context_to_category",
                        "lifespanCount" : 1
                    }
                ],
                "fulfillmentMessages": [
                    {
                        "text": {"text": [category_List]},
                        "platform": "LINE"
                    }
                ]
            }
    
    #ค้นหาสถานที่
    elif query_result.get('action') == "action-search":
        API_KEY = 'AIzaSyC_HWZLbWZOlxL2HtB1AThf27Don0kNqe8'
        searchBy = query_result.get('queryText')
        params = {
            'key': API_KEY,
            'address': searchBy
        }
        base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
        response = requests.get(base_url, params=params).json()
        response.keys()
        if response['status'] == 'OK':
            address = response['results'][0]['formatted_address']
            geometry = response['results'][0]['geometry']
            lat = geometry['location']['lat']
            lon = geometry['location']['lng']
            title = query_result.get('queryText')
        return {
            "displayText": '25',
            "source": "webhookdata",
            "fulfillmentMessages": [
                {
                    "payload": {
                        "line": {
                            "address": address,
                            "latitude": lat,
                            "title": title,
                            "longitude": lon,
                            "type": "location"
                        }
                    },
                    "platform": "LINE"
                }
            ]
        }

    #ส่งคำร้องเรียน
    elif query_result.get('action') == "action-task":
        level = query_result.get('outputContexts')[0].get('parameters').get('task-level')
        faculty = query_result.get('outputContexts')[0].get('parameters').get('task-faculty')
        category = query_result.get('outputContexts')[0].get('parameters').get('task-category')
        node = "พิมพ์ปัญหาที่คุณต้องการบอกกับเรา แล้วกดส่ง"
        return {
            "displayText": '25',
            "source": "webhookdata",
            "fulfillmentMessages": [
                {
                    "text": {"text": [node]},
                    "platform": "LINE"
                }
            ]
        }

    #ส่งคำร้องเรียนคำถาม
    elif query_result.get('action') == "action-task-send":
        level = query_result.get('outputContexts')[0].get('parameters').get('task-level')
        faculty = query_result.get('outputContexts')[0].get('parameters').get('task-faculty')
        category = query_result.get('outputContexts')[0].get('parameters').get('task-category')
        ques = query_result.get('queryText')
        node = "ยืนยันการส่งข้อมูลปัญหาดังต่อไปนี้\nระดับ : "+level+"\nคณะ : "+faculty+"\nหมวดหมู่ : "+category+"ปัญหา : "+ques
        return {
            "displayText": '25',
            "source": "webhookdata",
            "fulfillmentMessages": [
                {
                    "text": {"text": [node]},
                    "platform": "LINE"
                },
                {
                    "quickReplies": {
                        "title": "ยืนยันการส่งข้อมูล",
                        "quickReplies": ["ยืนยัน", "ยกเลิก"]
                    },
                    "platform": "LINE"
                }
            ]
        }

    #ยืนยันส่งคำร้องเรียน
    elif query_result.get('action') == "action-task-accept":
        level = query_result.get('outputContexts')[0].get('parameters').get('task-level')
        faculty = query_result.get('outputContexts')[0].get('parameters').get('task-faculty')
        category = query_result.get('outputContexts')[0].get('parameters').get('task-category')
        ques = query_result.get('outputContexts')[0].get('parameters').get('task-question')
        if query_result.get('queryText') == "ยืนยัน":
            node = "ปัญหาถูกส่งเข้าสู่ระบบเรียบร้อยแล้ว สามารถกดส่งปัญหาใหม่ได้ที่ช่องด้านล่าง"
            scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name('src/mapapi.json', scope)
            client = gspread.authorize(creds)
            sheet = client.open("คำร้องเรียน").sheet1
            data = sheet.get_all_records()
            insertRow = [level, faculty, category, ques]
            sheet.append_row(insertRow)
        else:
            node = "ยกเลิกการส่งปัญหาเรียบร้อยแล้ว สามารถกดส่งปัญหาใหม่ได้ที่ช่องด้านล่าง"
        return {
            "displayText": '25',
            "source": "webhookdata",
            "fulfillmentMessages": [
                {
                    "text": {"text": [node]},
                    "platform": "LINE"
                }
            ]
        }

    #แสดงข้อมูลคำถาม
    elif query_result.get('action') == "action-show-category":
        selected = int(query_result.get('queryText'))-1
        question_List = "สามารถเลือกข้อมูลคำถามได้โดยพิมพ์ 'ตัวเลข' คำถามด้านล่างนี้ลงไปแล้วกดส่ง\n\nตัวอย่างเช่น พิมพ์ '1' หรือสามารถพิมพ์ '1,2,3,4' โดยเว้นระหว่างตัวเลขด้วยสัญลักษณ์ ',' (ลูกน้ำ, จุลภาค, คอมม่า) โดยให้เรียงลำดับเลขจากน้อยไปมาก คำถามจะถูกตอบตามจำนวนที่ถูกพิมพ์เข้าไป\n\n"
        question_List += "คำถามที่พบบ่อยของหมวดหมู่ '"+ qa_List[selected][0] +"' มีดังนี้\n\n"
        if selected == 7:
            question_List += "- หัวข้อการขอใช้ยานพาหนะ\n"
            for i in range(2, 7, 1):
                question_List += str(qa_List[7][i][0])+". "+qa_List[7][i][1]+" ?\n"
            question_List += "\n- หัวข้อการขอใช้สถานที่ห้องประชุม และสนามกีฬา\n"
            for i in range(7, 11, 1):
                question_List += str(qa_List[7][i][0])+". "+qa_List[7][i][1]+" ?\n"
            question_List += "\n- หัวข้อการจัดทำหนังสือขอบคุณบริษัทต่างๆ ที่ให้การสนับสนุน\n"
            for i in range(11, 13, 1):
                if i == 13:
                    question_List += str(qa_List[7][i][0])+". "+qa_List[7][i][1]+" ?"
                else:
                    question_List += str(qa_List[7][i][0])+". "+qa_List[7][i][1]+" ?\n"
        else:
            for i in range(2, len(qa_List[selected]), 1):
                if i == len(qa_List[selected])-1:
                    question_List += str(qa_List[selected][i][0])+". "+qa_List[selected][i][1]+" ?"
                else:
                    question_List += str(qa_List[selected][i][0])+". "+qa_List[selected][i][1]+" ?\n"
        return {
            "displayText": '25',
            "source": "webhookdata",
            "outputContexts" : [
                {
                    "name" : "projects/full-crocco-qjkd/agent/sessions/00beed55-3c7d-8a47-2fc6-02f4dd100e91/contexts/context_to_answer",
                    "lifespanCount" : 1,
                    "parameters" : {
                        "select" : selected
                    }
                }
            ],
            "fulfillmentMessages": [
                {
                    "text": {"text": [question_List]},
                    "platform": "LINE"
                }
            ]
        }

    #แสดงข้อมูลคำตอบที่ถูกถามตามหมวดหมู่
    elif query_result.get('action') == "action-show-answer":
        selected = int(query_result.get('outputContexts')[0].get('parameters').get('select'))
        to_Answer = query_result.get('queryText')
        answer_List = ""
        if len(to_Answer) == 1:
            if selected == 9:
                emoji = random.choice(emoji_List)
                answer_List += "- คำถามข้อที่ "+str(qa_List[selected][int(to_Answer)+1][0])+". "+qa_List[selected][int(to_Answer)+1][1]+"?\n+ คำตอบ : "+qa_List[selected][int(to_Answer)+1][2]+" "+emoji+"\n\n"
            else:
                answer_List += "- คำถามข้อที่ "+str(qa_List[selected][int(to_Answer)+1][0])+". "+qa_List[selected][int(to_Answer)+1][1]+"?\n+ คำตอบ : "+qa_List[selected][int(to_Answer)+1][2]+"\n\n"
        else:
            to_Answer = query_result.get('queryText').split(",")
            for i in to_Answer:
                if selected == 9:
                    emoji = random.choice(emoji_List)
                    answer_List += "- คำถามข้อที่ "+str(qa_List[selected][int(i)+1][0])+". "+qa_List[selected][int(i)+1][1]+"?\n+ คำตอบ : "+qa_List[selected][int(i)+1][2]+" "+emoji+"\n\n"
                else:
                    answer_List += "- คำถามข้อที่ "+str(qa_List[selected][int(i)+1][0])+". "+qa_List[selected][int(i)+1][1]+"?\n+ คำตอบ : "+qa_List[selected][int(i)+1][2]+"\n\n"
        return {
            "displayText": '25',
            "source": "webhookdata",
            "outputContexts" : [
                {
                    "name" : "projects/full-crocco-qjkd/agent/sessions/00beed55-3c7d-8a47-2fc6-02f4dd100e91/contexts/re_answer",
                    "lifespanCount" : 1
                }
            ],
            "fulfillmentMessages": [
                {
                    "text": {"text": [answer_List]},
                    "platform": "LINE"
                },
                {
                    "quickReplies": {
                        "title": "ต้องการเลือกหมวดหมู่ที่ต้องการถามใหม่หรือไม่",
                        "quickReplies": ["ต้องการ", "ไม่ต้องการ"]
                    },
                    "platform": "LINE"
                }
            ]
        }

    #เริ่มต้นการเช็ค COVID-19
    elif query_result.get('action') == "covid-starter":
        return {
            "displayText": '25',
            "source": "webhookdata",
            "fulfillmentMessages": [
                {
                    "text": {"text": ["มาประเมินความเสี่ยงการติดเชื้อโควิด (COVID-19) กันเถอะ!"]},
                    "platform": "LINE"
                },
                {
                    "quickReplies": {
                        "title": "ต้องการประเมินหรือไม่ ?",
                        "quickReplies": ["ต้องการ", "ไม่ต้องการ"]
                    },
                    "platform": "LINE"
                }
            ]
        }

    #ขั้นตอนการเช็ค COVID-19
    elif query_result.get('action') == "covid-analyzing":
        if query_result.get('queryText') == "ต้องการ":
            return {
                "displayText": '25',
                "source": "webhookdata",
                "outputContexts" : [
                    {
                        "name" : "projects/full-crocco-qjkd/agent/sessions/00beed55-3c7d-8a47-2fc6-02f4dd100e91/contexts/covid_starter",
                        "lifespanCount" : 10,
                        "parameters" : {
                            "code" : '{"c":[0, 0, 11]}'
                        }
                    }
                ],
                "fulfillmentMessages": [
                    {
                        "text": {"text": ["1/11 | "+covid_Scan["Symptom"][0]]},
                        "platform": "LINE"
                    },
                    {
                        "quickReplies": {
                            "title": "ใช่หรือไม่",
                            "quickReplies": ["ใช่", "ไม่"]
                        },
                        "platform": "LINE"
                    }
                ]
            }
        elif query_result.get('queryText') == "ไม่ต้องการ":
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [
                    {
                        "text": {"text": ["หากต้องการประเมินใหม่ สามารถกดที่ปุ่ม 'COVID-19' ได้เลย"]},
                        "platform": "LINE"
                    }
                ]
            }
        code = query_result.get('outputContexts')[0].get('parameters').get('code')
        c = json.loads(code)
        if query_result.get('queryText') == "ใช่":
            c["c"][0] += covid_Scan["Risk_Score"][c["c"][1]]
            c["c"][1] += 1
            if c["c"][1] == c["c"][2]:
                your_Score = c["c"][0]
                if your_Score > 11:
                    result = "\nคุณมีความเสี่ยงสูงที่จะเป็น COVID-19\n*หากมีอาการหอบเหนื่อย หายใจไม่ทัน พูดไม่เป็นคำ โทรเรียกรถฉุกเฉิน 1669\nพร้อมแจ้งความเสี่ยงในการติดเชื้อ COVID-19"
                elif your_Score > 7:
                    result = "\n'คุณมีความเสี่ยงปานกลาง' ในการได้รับเชื้อ COVID-19\n*หากมีอาการหอบเหนื่อย หายใจไม่ทัน พูดไม่เป็นคำ โทรเรียกรถฉุกเฉิน 1669\nพร้อมแจ้งความเสี่ยงในการติดเชื้อ COVID-19\nวิธีปฎิบัติตัวในช่วงของการระบาด COVID-19\n1. หมั่นล้างมือให้สะอาดด้วยสบู่หรือแอลกอฮอล์เจล\n2. หลีกเลี่ยงการสัมผัสผู้ที่มีอาการคล้ายไข้หวัด หรือหลีกเลี่ยงการไปที่มีฝูงชน\n3. ปรุงอาหารประเภทเนื้อสัตว์และไข่ให้สุกด้วยความร้อน\n4. ให้ผ้าปิดปากหรือจมูก เพื่อป้องกันการได้รับเชื้อโรค"
                elif your_Score > 3:
                    result = "\n'คุณมีความเสี่ยงน้อย' ในการได้รับเชื้อ COVID-19\nวิธีปฎิบัติตัวในช่วงของการระบาด COVID-19\n1. หมั่นล้างมือให้สะอาดด้วยสบู่หรือแอลกอฮอล์เจล\n2. หลีกเลี่ยงการสัมผัสผู้ที่มีอาการคล้ายไข้หวัด หรือหลีกเลี่ยงการไปที่มีฝูงชน\n3. ปรุงอาหารประเภทเนื้อสัตว์และไข่ให้สุกด้วยความร้อน\n4. ให้ผ้าปิดปากหรือจมูก เพื่อป้องกันการได้รับเชื้อโรค"
                else:
                    result = "\n'คุณมีความเสี่ยงน้อยมาก' ในการได้รับเชื้อ COVID-19\nวิธีปฎิบัติตัวในช่วงของการระบาด COVID-19\n1. หมั่นล้างมือให้สะอาดด้วยสบู่หรือแอลกอฮอล์เจล\n2. หลีกเลี่ยงการสัมผัสผู้ที่มีอาการคล้ายไข้หวัด หรือหลีกเลี่ยงการไปที่มีฝูงชน\n3. ปรุงอาหารประเภทเนื้อสัตว์และไข่ให้สุกด้วยความร้อน\n4. ให้ผ้าปิดปากหรือจมูก เพื่อป้องกันการได้รับเชื้อโรค"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [result]},
                            "platform": "LINE"
                        }
                    ]
                }
            cr = ""
            for i in str(c):
                if i == " ":
                    continue
                elif i == "\'":
                    cr += "\""
                else:
                    cr += i
            return {
                "displayText": '25',
                "source": "webhookdata",
                "outputContexts" : [
                    {
                        "name" : "projects/full-crocco-qjkd/agent/sessions/00beed55-3c7d-8a47-2fc6-02f4dd100e91/contexts/covid_starter",
                        "lifespanCount" : c["c"][2]-c["c"][1],
                        "parameters" : {
                            "code" : cr
                        }
                    }
                ],
                "fulfillmentMessages": [
                    {
                        "text": {"text": [str((c["c"][1])+1)+"/11 | "+covid_Scan["Symptom"][c["c"][1]]]},
                        "platform": "LINE"
                    },
                    {
                        "quickReplies": {
                            "title": "ใช่หรือไม่",
                            "quickReplies": ["ใช่", "ไม่"]
                        },
                        "platform": "LINE"
                    }
                ]
            }
        elif query_result.get('queryText') == "ไม่":
            c["c"][1] += 1
            if c["c"][1] == c["c"][2]:
                your_Score = c["c"][0]
                if your_Score > 11:
                    result = "\nคุณมีความเสี่ยงสูงที่จะเป็น COVID-19\n*หากมีอาการหอบเหนื่อย หายใจไม่ทัน พูดไม่เป็นคำ โทรเรียกรถฉุกเฉิน 1669\nพร้อมแจ้งความเสี่ยงในการติดเชื้อ COVID-19"
                elif your_Score > 7:
                    result = "\n'คุณมีความเสี่ยงปานกลาง' ในการได้รับเชื้อ COVID-19\n*หากมีอาการหอบเหนื่อย หายใจไม่ทัน พูดไม่เป็นคำ โทรเรียกรถฉุกเฉิน 1669\nพร้อมแจ้งความเสี่ยงในการติดเชื้อ COVID-19\nวิธีปฎิบัติตัวในช่วงของการระบาด COVID-19\n1. หมั่นล้างมือให้สะอาดด้วยสบู่หรือแอลกอฮอล์เจล\n2. หลีกเลี่ยงการสัมผัสผู้ที่มีอาการคล้ายไข้หวัด หรือหลีกเลี่ยงการไปที่มีฝูงชน\n3. ปรุงอาหารประเภทเนื้อสัตว์และไข่ให้สุกด้วยความร้อน\n4. ให้ผ้าปิดปากหรือจมูก เพื่อป้องกันการได้รับเชื้อโรค"
                elif your_Score > 3:
                    result = "\n'คุณมีความเสี่ยงน้อย' ในการได้รับเชื้อ COVID-19\nวิธีปฎิบัติตัวในช่วงของการระบาด COVID-19\n1. หมั่นล้างมือให้สะอาดด้วยสบู่หรือแอลกอฮอล์เจล\n2. หลีกเลี่ยงการสัมผัสผู้ที่มีอาการคล้ายไข้หวัด หรือหลีกเลี่ยงการไปที่มีฝูงชน\n3. ปรุงอาหารประเภทเนื้อสัตว์และไข่ให้สุกด้วยความร้อน\n4. ให้ผ้าปิดปากหรือจมูก เพื่อป้องกันการได้รับเชื้อโรค"
                else:
                    result = "\n'คุณมีความเสี่ยงน้อยมาก' ในการได้รับเชื้อ COVID-19\nวิธีปฎิบัติตัวในช่วงของการระบาด COVID-19\n1. หมั่นล้างมือให้สะอาดด้วยสบู่หรือแอลกอฮอล์เจล\n2. หลีกเลี่ยงการสัมผัสผู้ที่มีอาการคล้ายไข้หวัด หรือหลีกเลี่ยงการไปที่มีฝูงชน\n3. ปรุงอาหารประเภทเนื้อสัตว์และไข่ให้สุกด้วยความร้อน\n4. ให้ผ้าปิดปากหรือจมูก เพื่อป้องกันการได้รับเชื้อโรค"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [result]},
                            "platform": "LINE"
                        }
                    ]
                }
            cr = ""
            for i in str(c):
                if i == " ":
                    continue
                elif i == "\'":
                    cr += "\""
                else:
                    cr += i
            return {
                "displayText": '25',
                "source": "webhookdata",
                "outputContexts" : [
                    {
                        "name" : "projects/full-crocco-qjkd/agent/sessions/00beed55-3c7d-8a47-2fc6-02f4dd100e91/contexts/covid_starter",
                        "lifespanCount" : c["c"][2]-c["c"][1],
                        "parameters" : {
                            "code" : cr
                        }
                    }
                ],
                "fulfillmentMessages": [
                    {
                        "text": {"text": [str((c["c"][1])+1)+"/11 | "+covid_Scan["Symptom"][c["c"][1]]]},
                        "platform": "LINE"
                    },
                    {
                        "quickReplies": {
                            "title": "ใช่หรือไม่",
                            "quickReplies": ["ใช่", "ไม่"]
                        },
                        "platform": "LINE"
                    }
                ]
            }
    
    # การส่งเรื่องร้องเรียน
    elif query_result.get('action') == "action-sent":
        return {
            "displayText": '25',
            "source": "webhookdata",
            "fulfillmentMessages": [
                {
                    "text": {"text": ["โปรดส่งคำร้องเรียนที่ต้องการบอก โดยการพิมพ์ลงไปในแชท"]},
                    "platform": "LINE"
                }
            ]
        }

    # การส่งเรื่องร้องเรียนสำเร็จ
    elif query_result.get('action') == "action-have-sent":

        file = open('/home/PlT/crocco/etc.json', "r")
        etc_List = json.load(file)
        file.close()
        etc_List["Appeal_Sent"] = etc_List["Appeal_Sent"]+1
        order = str(etc_List["Appeal_Sent"])
        file = open('/home/PlT/crocco/etc.json', "w")
        json.dump(etc_List, file)
        file.close()

        appeal = query_result.get('queryText')
        with open("/home/PlT/crocco/appeal.txt", "a") as text_file:
            text_file.write("คำร้องเรียนที่ "+order+" | "+appeal+"\n")
        return {
            "displayText": '25',
            "source": "webhookdata",
            "fulfillmentMessages": [
                {
                    "text": {"text": ["ส่งคำร้องเรียนสำเร็จ"]},
                    "platform": "LINE"
                }
            ]
        }

    # คำถามต่างๆ
    else:
        # คลินิก
        if "คลินิก" in query_result.get('queryText') or "ไม่สบาย" in query_result.get('queryText') or "ไข้" in query_result.get('queryText') or "ปวดหัว" in query_result.get('queryText') or "เจ็บ" in query_result.get('queryText') or "ป่วย" in query_result.get('queryText') or "เป็นหวัด" in query_result.get('queryText') or "หมอ" in query_result.get('queryText'):
            node = "เวลาเปิดให้บริการคลินิก\nจันทร์ - ศุกร์  เวลา 08.00 น. - 18.00 น.\nเสาร-อาทิตย์ เวลา 09.00 น. - 12.00 น."
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        # หอพัก
        elif "หอพัก" in query_result.get('queryText'):
            node = "สามารถติดต่อเพื่อสอบถามข้อมูลด้วยตนเองได้ที่ สำนักงานหอพักนักศึกษา หรือโทร 02-329-8145 หรือ เพจ Facebook ชาวหอใน KMITL Dormitory"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        # กยศ
        elif "กยศ" in query_result.get('queryText'):
            node = "ติดต่องาน กยศ.สจล สำนักงานกิจการนักศึกษาและศิษย์เก่าสัมพันธ์ได้ที่ อาคารกรมหลวงนราธิวาสราชนครินทร์ (ตึกสำนักงานอธิการบดี) ชั้น 4, โทรศัพท์ 02-329-8032 สายใน 02-329-8000 ต่อ 3183, 3185 และเพจ Facebook : กยศ.สจล. (facebook.com/StudentLoan.KMITL)"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [
                    {
                    "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        # ประกัน
        elif "ประกัน" in query_result.get('queryText'):
            if "บัตร" in query_result.get('queryText'):
                node = "ติดตามข่าวกิจกรรมจิตอาสาได้ที่ Page Facebook จิตอาสาพระจอมเกล้าลาดกระบัง/KMITL Student Life"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "สุขภาพ" in query_result.get('queryText'):
                node = "ทางสถาบันไม่มีประกันสุขภาพ ถ้านักศึกษามีปัญหาเรื่องสุขภาพ สามารถติดต่อได้ที่คลินิกเวชกรรม ตรวจสอบข้อมูล และตารางแพทย์ได้ที่ medicalcenter.kmitl.ac.th"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "อุบัติเหตุ" in query_result.get('queryText'):
                node = "สถาบันได้ทำประกันภัยอุบัติเหตุให้กับผู้ที่มีสถานภาพเป็นนักศึกษาทุกคน\nสำหรับปีการศึกษานั้นๆ บริษัทที่ได้รับประกันภัยคือ บริษัทไทยไพบูลย์ประกันภัย จำกัด (มหาชน) โดยมีความคุ้มครอง ดังนี้\n- ระยะเวลาเอาประกันภัยอุบัติเหตุ เริ่มคุ้มครองตั้งแต่วันที่ 1 กรกฎาคม เริ่มเวลา 16.30 น. สิ้นสุดวันที่ 1 กรกฎาคม ของปีถัดไป เวลา 16.30 น. ขอบเขตความคุ้มครองคุ้มครองตลอด 24 ชั่วโมง ทั่วประเทศ/ต่างประเทศ ประกันอุบัติเหตุของนักศึกษาจะเป็นความคุ้มครองปีต่อปี\n- ผู้เอาประกันภัยหากประสบอุบัติเหตุสามารถเข้ารักษาได้ทั้งสถานพยาบาลของรัฐ เอกชน และคลินิก ทั่วประเทศ/ต่างประเทศ ตลอด 24 ชั่วโมง\n- บริษัทจะออกบัตรประจำตัวผู้เอาประกันภัยให้กับผู้ที่มีสถานภาพเป็นนักศึกษาสถาบันเท่านั้น โดยบริษัทจะส่งบัตรประกันให้ประมาณเดือนกันยายน-ตุลาคม เป็นต้นไป โดยส่งผ่านงานกิจการนักศึกษาคณะ/วิทยาลัย/ภาควิชาที่สังกัด\n- บัตรประกันอุบัติเหตุที่บริษัทออกให้กับผู้เอาประกันภัย ใช้ได้ในโรงพยาบาลของเอกชนที่เปิดสัญญากับบริษัทฯ จำนวน 350 แห่งทั่วประเทศตรวจสอบรายชื่อโรงพยาบาลได้ที่ www.thaipaiboon.com/index.php\n- กรณีเข้ารักษาในสถานพยาบาลของรัฐบาล/คลินิก/โรงพยาบาลที่ไม่ใช่คู่สัญญา/หรือหากบริษัทมอบบัตรประกันฯให้ผู้เอาประกันไปแล้ว แต่ทำบัตรประกันสูญหายหรือไม่ได้พกบัตรฯ ผู้เอาประกันจะต้องสำรองจ่ายเงินค่ารักษาพยาบาลอุบัติเหตุไปก่อน และให้นำหลักฐานเอกสารการจ่ายเงินมายื่นคำร้องขอเบิกเงินคืนได้ในภายหลัง"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "ครอบคลุม" in query_result.get('queryText') or "คุ้มครอง" in query_result.get('queryText'):
                node = "ประกันมีความคุ้มครอง ดังต่อไปนี้\n- ค่ายา\n- ค่าหมอ\n- ค่าห้อง\n- ค่ารักษาพยาบาล\n- ค่าบริการทางการแพทย์\n- ค่าผ่าตัดฯ\nประกันไม่มีความคุ้มครอง ดังต่อไปนี้\nค่ารักษาพยาบาลบางรายการจะไม่คุ้มครอง เช่น\n\n- ค่าบริการอื่นๆ ที่โรงพยาบาลระบุไม่ชัดเจน\n- ค่าเวชภัณฑ์ 2 \n- รถเข็น\n- ค่านิติเวช\n- ค่ารถพยาบาล\n- ศัลยกรรมตกแต่ง\n- การทำฟัน\n- อุดฟันฯ\n- เจ็บป่วย\n- รักษารากฟันเกิน  7 วัน\n- ทะเลาะวิวาท\n- กีฬาเสี่ยงภัย ยกเว้นกีฬาที่สถาบันจัดการแข่งขันกีฬามหาวิทยาลัย"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "โควิด" in query_result.get('queryText') or "covid" in query_result.get('queryText'):
                node = "ทุนช่วยเหลือนักศึกษาในสถานการณ์การแพร่ระบาด COVID-19 สามารถหาข้อมูลได้จาก https://office.kmitl.ac.th/osda/kmitl-scholarships/"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            else:
                node = "สามารถติดต่อได้ที่พี่ตุ๊กและพี่อภิชัย งานบริการนักศึกษา สำนักงานกิจการนักศึกษาและศิษย์เก่าสัมพันธ์ชั้น 4 อาคารสำนักงานอธิการบดี สจล."
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
        # จิตอาสา
        elif "จิตอาสา" in query_result.get('queryText'):
            node = "ติดตามข่าวกิจกรรมจิตอาสาได้ที่ Page Facebook จิตอาสาพระจอมเกล้าลาดกระบัง/KMITL Student Life"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        # สุขภาพ
        elif "สุขภาพ" in query_result.get('queryText'):
            node = "ติดตามข่าวกิจกรรมจิตอาสาได้ที่ Page Facebook จิตอาสาพระจอมเกล้าลาดกระบัง/KMITL Student Life"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        # ทุน
        elif "ทุน" in query_result.get('queryText'):
            if "สมัคร" in query_result.get('queryText'):
                node = "สมัครได้ที่ระบบทุนการศึกษา Online หรือตามลิงค์นี้ :https://scholarship.kmitl.ac.th"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "เอกสาร" in query_result.get('queryText'):
                node = "1. สำเนาบัตรนักศึกษาหรือสำเนาบัตรประชาชน\n2. สำเนาหน้าบัญชีธนาคารหน้าชื่อบัญชี\n3. สำเนาหน้าบัญชีปรับปัจจุบันมีการเคลื่อนไหวไม่เกิน 2 เดือน"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "สัมภาษณ์" in query_result.get('queryText'):
                node = "ให้นักศึกษาติดตามที่ Facebook : KMITL Student Life และในระบบทุนการศึกษา Online หรือตามลิงค์นี้ : https://scholarship.kmitl.ac.th"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            else:
                node = "ทุนสถาบันมีดังนี้\n- ทุน กยศ. ( office.kmitl.ac.th/osda/studentloan/# )\n- ทุน สจล. ( office.kmitl.ac.th/osda/kmitl/ ) มีดังนี้\n1. ทุนอุดหนุนการศึกษา ประเภท ก\n2. ทุนอุดหนุนการศึกษา ประเภท ข\n3. ทุนเรียนดี\n4. ทุนผู้ทำคุณประโยชน์ให้แก่สถาบัน\n5. ทุนผู้สร้างชื่อเสียงในนามสถาบัน\n6. ทุนให้ยืมเพื่อการศึกษาในกรณีฉุกเฉิน\n7. ทุนสนับสนุนนักศึกษาในภาวะวิกฤต\n8. ทุนสนับสนุนการนำเสนอผลงานทางวิชาการ\n9. ทุนสนับสนุนการแลกเปลี่ยนและฝึกงานต่างประเทศ\n10. ทุนช่วยเหลือนักศึกษาในสถานการณ์การแพร่ระบาด COVID-19\n- ทุน ภายนอก ( https://office.kmitl.ac.th/osda/outside-scholarship/ )\n\nสอบถามเพิ่มเติมเกี่ยวกับทุนได้ โดยกดไปที่ เมนู > เกี่ยวกับนักศึกษา > ทุนการศึกษา\n\nสามารถรับใบสมัครทุนได้ที่คณะหรือที่งานทุนการศึกษา สำนักงานกิจการนักศึกษาและศิษย์เก่าสัมพันธ์ ชั้น 4 อาคาร สำนักงานอธิการบดี และสามารถส่งใบสมัครทุนได้ที่คณะของตนเอง\n\nเอกสารที่ต้องการ มีดังนี้\n1. สำเนาบัตรนักศึกษาหรือสำเนาบัตรประชาชน\n2. สำเนาหน้าบัญชีธนาคารหน้าชื่อบัญชีและสำเนาหน้าบัญชีปรับปัจจุบันมีการเคลื่อนไหวไม่เกิน 2 เดือน\n"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
        # ทหาร
        elif "ทหาร" in query_result.get('queryText') and "ผ่อนผัน" in query_result.get('queryText'):
            if "กี่" in query_result.get('queryText'):
                node = "ผ่อนผันให้เฉพาะผู้ซึ่งอยู่ในระหว่างการศึกษาที่ไม่สูงกว่าชั้นปริญญาโทและผ่อนผันให้จนถึงอายุครบ 26 ปีบริบูรณ์ เว้นแต่นักศึกษาแพทยศาสตร์ผ่อนผันให้ระหว่างที่ปฏิบัติงานเพื่อขึ้นทะเบียนและรับใบอนุญาตฯ อีก 1 ปี"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "ติดต่อ" in query_result.get('queryText') or "ถาม" in query_result.get('queryText'):
                node = "สำนักงานกิจการนักศึกษาและศิษย์เก่าสัมพันธ์ ชั้น 4 สำนักงานอธิการบดี หรือ เพจเฟสบุ๊ค งานวิชาทหารพระจอมเกล้าลาดกระบังหรือ โทรศัพท์ 084-139-6929 ว่าที่ ร.ต.อภิชัย แส้ทอง"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            else:
                node = "เอกสารที่ใช้ในการผ่อนผันการเกณฑ์ทหาร\n1. คำร้องขอผ่อนผันทหาร จำนวน 1 ฉบับ\n2. สำเนาหนังสือ สด.9 (ด้านหน้า-ด้านหลัง) จำนวน 3 ฉบับ\n3. สำเนาหมายเรียก สด.35 (ติดต่อขอรับได้ที่ สัสดีอำเภอ/เขต ตามภูมิลำเนาทหาร) จำนวน 3 ฉบับ\n 4. สำเนาทะเบียนบ้านที่มีชื่อนักศึกษาและหน้าที่มีเลขที่บ้าน จำนวน 3 ฉบับ\n5. สำเนาบัตรประจำตัวนักศึกษา จำนวน 3 ฉบับ\n6. สำเนาบัตรประจำตัวประชาชน จำนวน 3 ฉบับ\n7. หนังสือรับรองสถานภาพเป็นนักศึกษา ฉบับจริง 1 ฉบับ และถ่ายสำเนา จำนวน 2 ฉบับ\n** เพิ่มเติมข้อ 7. ติดต่อที่สำนักทะเบียนและประมวลผล (ชั้น 2) สำนักงานอธิการบดี โดยระบุในคำร้องว่า “เพื่อใช้ผ่อนผันการเกณฑ์ทหารทหาร” ระยะเวลาในหนังสือรับรองจะต้องระบุ 360 วัน (ค่าธรรมเนียม 50 บาท)"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
        # รด
        elif "รด" in query_result.get('queryText') or "ทหาร" in query_result.get('queryText'):
            if "ติดต่อ" in query_result.get('queryText') or "ถาม" in query_result.get('queryText'):
                node = "สำนักงานกิจการนักศึกษาและศิษย์เก่าสัมพันธ์ ชั้น4 สำนักงานอธิการบดี หรือ เพจเฟสบุ๊ค งานวิชาทหารพระจอมเกล้าลาดกระบัง หรือ โทรศัพท์ 084-139-6929 ว่าที่ ร.ต.อภิชัย แส้ทอง"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "หลักฐาน" in query_result.get('queryText'):
                node = "ใบสมัคร/หนังสือรับรองวุฒิ ม.6/สำเนา สด.9(ถ้ามี)/รูปถ่าย นร. จำนวน 1 ใบ"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "เอกสาร" in query_result.get('queryText'):
                node = "1.ใช้หนังสือรับรองการฝึก รด.ชั้นปีที่ผ่านมา  กทม.ขอที่ศูนย์วิภาวดี/ต่างจังหวัดขอที่หน่วยฝึกที่เรียนวิชาทหาร\n2.รูป นศท. ขนาด 1 นิ้ว จำนวน 1 รูป (รูปเก่าใช้ได้)"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            else:
                node = "สมัครได้ที่สำนักงานกิจการนักศึกษาและศิษย์เก่าสัมพันธ์ ชั้น 4 อาคารสำนักงานอธิการบดี หรือ เพจเฟสบุ๊ค งานวิชาทหารพระจอมเกล้าลาดกระบัง หรือ โทรศัพท์ 084-139-6929 ว่าที่ ร.ต.อภิชัย แส้ทอง"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
        #รหัสเข้าเว็บไซต์
        elif "เว็บ" in query_result.get('queryText'):
            if "รหัส" in query_result.get('queryText'):
                node = "ขอรหัสผู้ใช้งานจากสำนักบริการคอมพิวเตอร์\nโทร 02-329-8000 ต่อ 6000 หรือติดต่อ ตามช่องทางนี้\n Line ID : @helpcenter.kmitl\n Email   : helpcenter@kmitl.ac.th\n Mobile  : 091-190-6000"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
        #โรงพยาบาลที่เข้ารักษาได้
        elif "โรง" in query_result.get('queryText') and "บาล" in query_result.get('queryText') or "รพ" in query_result.get('queryText'):
            node = "ผู้เอาประกันภัยหากประสบอุบัติเหตุสามารถเข้ารักษาได้ทั้งสถานพยาบาลของรัฐ เอกชน คลินิก ทั่วประเทศ/ต่างประเทศ ตลอด 24 ชั่วโมง และสามารถตรวจสอบรายชื่อโรงพยาบาล ได้ที่ www.thaipaiboon.com/index.php"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #ลงทะเบียนเรียน
        elif "ลงเรียน" in query_result.get('queryText') or "ลงทะเบียน" in query_result.get('queryText'):
            if "ไม่ทัน" in query_result.get('queryText'):
                node = "หากลงทะเบียนเรียนจริงไม่ทันในช่วงเวลาที่กำหนด ช่วงเวลาต่อไปจะเป็นการลงทะเบียนล่าช้าจะต้องเสียค่าปรับการลงทะเบียนล่าช้า 300 บาท รายละเอียดดูได้จากปฏิทินการศึกษา"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
        #ลาออก
        elif "ลาออก" in query_result.get('queryText'):
            node = "หากต้องการลาออกจากสถาบัน\n1. เจ้าหน้าที่ตรวจสอบสถานะ/ตรวจสอบยอดค้างชำระ (หากมียอดค้างชำระไม่สามารถลาออกได้)\n2. นำคำร้องลาออกให้นักศึกษากรอก และผู้ปกครองลงนามรับทราบและยินยอมการลาออก พร้อมแนบสำเนาบัตรประชาชนผู้ปกครอง\n3. แจ้งนักศึกษาไปติดต่อหน่วยงานดังนี้\n  3.1. ติดต่อสำนักหอสมุดกลาง ตรวจสอบว่าค้างหนังสือหรือไม่\n  3.2. ติดต่อภาควิชา/สาขาวิชา ตรวจสอบว่าค้างอุปกรณ์หรือไม่\n  3.3. ติดต่อประสานงานทะเบียนฯ คณะ/วิทยาลัย รับทราบการลาออก\n  3.4. เมื่อนักศึกษาติดต่อหน่วยงานครบทั้ง 3 หน่วยงาน นำคำร้องกลับมายื่นต่อสำนักทะเบียนฯ เพื่องานรับเข้าศึกษาดำเนินการต่อไป\n\nข้อควรระวัง\n1. นักศึกษาที่มียอดค้างชำระไม่สามารถลาออกได้\n2. นักศึกษาที่มีสถานะพ้นสภาพไม่ต้องยื่นเอกสารลาออก"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #ตำรวจ
        elif "ตำรวจ" in query_result.get('queryText'):
            node = "สถานีตำรวจนครบาลจรเข้น้อย โทรศัพท์ : 02-326-9056, 0-2326-9993\nสถานีตำรวจนครบาลลาดกระบัง โทรศัพท์ : 02-326-6505-6\nสถานีตำรวจนครบาลฉลองกรุง โทรศัพท์ : 02-175-4109-12"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #หอสมุด
        elif "หอสมุด" in query_result.get('queryText') or "ห้องสมุด" in query_result.get('queryText'):
            if "เปิด" in query_result.get('queryText'):
                node = "สำนักหอสมุดกลาง เปิดให้บริการ\n- วันจันทร์ – วันศุกร์ เวลา 08.30 – 20.30 น.\n- วันเสาร์ – วันอาทิตย์ เวลา 10.00 – 18.00  น.\nวันหยุดนักขัตฤกษ์ ปิดบริการ\n\nห้องสมุดคณะสถาปัตยกรรมศาสตร์ เปิดให้บริการ\n- วันจันทร์ - วันศุกร์ เวลา  08.30 – 16.30 น.\n- วันเสาร์ – วันอาทิตย์ และ วันหยุดนักขัตฤกษ์ ปิดบริการ\n\nหมายเหตุ\n: ช่วงปิดภาคการศึกษาทุกห้องสมุดเปิดบริการ\nวันจันทร์ – วันศุกร์ เวลา  08.30 – 16.30 น.\nวันเสาร์ – วันอาทิตย์ และวันหยุดนักขัตฤกษ์  ปิดบริการ\n: เปิดบริการพื้นที่นั่งอ่าน 24 ชม. เฉพาะบริเวณชั้น 1 ช่วงสอบกลางภาคและปลายภายการศึกษา"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "สมัคร" in query_result.get('queryText'):
                node = "อาจารย์/เจ้าหน้าที่ ของสถาบันฯ\n- สมัครสมาชิกห้องสมุด ได้ที่เคาน์เตอร์บริการยืม – คืนหนังสือ ชั้น 1 อาคารใหม่ \n\nหลักฐานการสมัคร\n1. กรอกแบบฟอร์มในสมัครได้ที่เคาน์เตอร์บริการยืม-คืน\n2. ยื่นบัตรพนักงานสถาบันฯ หรือ เอกสารหลักฐานการบรรจุเป็นพนักงาน หรือ สัญญาการจ้างงาน (เลือกอย่างใดอย่างหนึ่ง)\n\nนักศึกษา\nนักศึกษาเป็นสมาชิกห้องสมุดโดยอัตโนมัติจนจบการศึกษา หากนักศึกษาลงทะเบียนเรียนในทุกเทอม ยกเว้นกรณีนักศึกษาค้างชำระค่าปรับ และมีหนังสือเกินกำหนดคืนในระหว่างการลงทะเบียนเรียน ระบบจะล็อกสิทธิ์การลงทะเบียนเรียน และไม่สามารถยืมหนังสือได้"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
        #กู้ยืม
        elif "กู้ยืม" in query_result.get('queryText'):
            node = "เอกสารที่ต้องการสำหรับประกอบการทำสัญญากู้ยืม\n- สัญญากู้ยืมที่พิมพ์จากระบบ e-studentloan จำนวน 3 ชุด พร้อมเอกสารประกอบได้แก่\n1. สำเนาบัตรประชาชน+สำเนาทะเบียนบ้าน+สำเนาหน้าสมุดบัญชี ของผู้กู้ยืมเงิน อย่างละ 3 ฉบับ\n2. สำเนาบัตรประจำตัวประชาชน+สำเนาทะเบียนบ้านของผู้ค้ำประกัน อย่างละ 3 ฉบับ โดยจะต้องจัดเรียงเอกสารเป็นชุดๆ"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #อุบัติเหตุ
        elif "อุบัติเหตุ" in query_result.get('queryText') or "รถชน" in query_result.get('queryText') or "รถล้ม" in query_result.get('queryText'):
            if "ติดต่อ" in query_result.get('queryText'):
                node = "สายด่วน พี่ตุ๊ก (วรรนิภา) เจ้าหน้าที่การสวัสดิการนักศึกษาที่เบอร์ สำนักงาน 02-329-8000 ต่อ 3243 (08.00-16.30 น.) ยกเว้นวันหยุดราชการ\nและโทรศัพท์ 081-364-9071 จะประสานในเรื่องการรักษาในโรงพยาบาล"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            else:
                node = "หากเข้าโรงพยาบาลเอกชน ใช้บัตรประกันที่มอบให้นักศึกษายื่นคู่กับบัตรประชาชนได้\nหากไม่มีบัตร หรือยังไม่ได้รับบัตรประกัน ต้องสำรองจ่ายค่ารักษา\nกรณีสำรองจ่ายค่ารักษาพยาบาลอุบัติเหตุ ให้นำหลักฐานมายื่นคำร้องขอเบิกเงินคืน โดยให้เตรียมเอกสาร ดังนี้\n\n- เขียนคำร้องเบิกค่าสินไหม (มารับด้วยตนเองหรือโหลดแบบฟอร์มได้ office.kmitl.ac.th/osda)\n- ใบเสร็จรับเงิน ฉบับจริง พร้อมถ่ายสำเนาทุกฉบับ จำนวน 1 ชุด\n- ใบรับรองแพทย์ ฉบับจริง พร้อมถ่ายสำเนาทุกฉบับ จำนวน 1 ชุด\n- สำเนาบัตรประจำตัวประชาชนของผู้เอาประกัน จำนวน 1 ฉบับ\n- สำเนาสมุดบัญชีหน้าแรกของผู้เอาประกันธนาคารใดก็ได้ จำนวน 2 ฉบับ\n- บันทึกประจำวันของสถานีตำรวจพื้นที่เกิดเหตุกรณีเป็นคดีความ พร้อมถ่ายสำเนา 1 ชุด (ถ้ามี)"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
        #เบิกค่ารักษา
        elif "รักษา" in query_result.get('queryText') and "เบิก" in query_result.get('queryText'):
            node = "กรณีสำรองจ่ายค่ารักษาพยาบาลอุบัติเหตุ ให้นำหลักฐานมายื่นคำร้องขอเบิกเงินคืน โดยให้นำเอกสารดังนี้\n\n1. เขียนคำร้องเบิกค่าสินไหม (มารับด้วยตนเองหรือโหลดแบบฟอร์มได้ที่ office.kmitl.ac.th/osda)\n2. ใบเสร็จรับเงินฉบับจริง พร้อมถ่ายสำเนาทุกฉบับ จำนวน 1 ชุด\n3. ใบรับรองแพทย์ฉบับจริง พร้อมถ่ายสำเนาทุกฉบับ จำนวน 1 ชุด\n4. สำเนาบัตรประจำตัวประชาชนของผู้เอาประกัน จำนวน 1 ฉบับ\n5. สำเนาสมุดบัญชีหน้าแรกของผู้เอาประกันธนาคารใดก็ได้ จำนวน 2 ฉบับ\n6. บันทึกประจำวันของสถานีตำรวจพื้นที่เกิดเหตุ กรณีเป็นคดีความ พร้อมถ่ายสำเนา 1 ชุด (ถ้ามี)\nยื่นเอกสารได้ที่ พี่ตุ๊ก งานบริการนักศึกษา สำนักงานกิจการนักศึกษาและศิษยืเก่าสัมพันธ์ชั้น 4 อาคารสำนักงานอธิการบดี สจล. เวลา 08.00-16.30 น. เว้นวันหยุดราชการ"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [ 
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #สระว่ายน้ำ
        elif "สระ" in query_result.get('queryText') or "ว่ายน้ำ" in query_result.get('queryText'):
            if "สมาชิก" in query_result.get('queryText'):
                node = "ประเภทสมาชิกของศูนย์กีฬา สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง แบ่งเป็นประเภทดังนี้\nประเภทที่ 1 : นักศึกษาระดับปริญญาตรีของสถาบัน\nประเภทที่ 2 : ข้าราชการ พนักงานสถาบัน ลูกจ้างของสถาบันสามีหรือภรรยาที่ชอบด้วยกฏหมายและบุตรที่ชอบด้วยกฏหมายของข้าราชการ พนักงานสถาบัน หรือลูกจ้างของสถาบัน พนักงานหรือลูกจ้างของโงเรียนสาธิตนานาชาติ สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง และพนักงานหรือลูกจ้างของหลักสูตรอื่นๆ ที่จัดตั้งภายใต้สถาบัน นักศึกษาระดับปริญญาโท นักศึกษาระดับปริญญาเอก และศิษย์เก่าของสถาบัน รวมทั้งข้าราชการ พนักงานสถาบัน ลูกจ้างของสถาบันที่เกษียณอายุไปแล้ว\nประเภทที่ 3 : นักศึกษาโรงเรียนสาธิตนานาชาติ สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง นักศึกษามหาวิทยาลัยซีเอ็มเคแอล นักเรียนหรือนักศึกษาหลักสูตรอื่นๆ ที่จัดตั้งภายใต้สถาบัน\nประเภทที่ 4 : บุคคลภายนอก"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [ 
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "ค่า" in query_result.get('queryText'):
                node = "ค่าบริการลงสระ (บาท/คน/รอบ) ตามประเภทของสมาชิก ดังนี้\nประเภทที่ 1, 2 และ 3\n08:30 - 16:00 น. : 20 บาท\n16:00 น. - 21:00 น. : 30 บาท\nประเภทที่ 4\n08:30 - 16:00 น. : 40 บาท\n16:00 น. - 21:00 น. : 80 บาท\nไม่เป็นสมาชิก\n08:30 - 16:00 น. : 80 บาท\n16:00 น. - 21:00 น. : 120 บาท\nเด็กที่มีความสูงต่ำกว่า 135 ซม.\n08:30 - 16:00 น. : 30 บาท\n16:00 น. - 21:00 น. : 50 บาท\nค่าสมาชิก และค่าธรรมเนียมในการใช้บริการ อาจมีการเปลี่ยนแปลงได้ตามความเหมาะสม ในกรณีที่มีการเปลี่ยนแปลงให้เป็นไปตามประกาศสถาบัน"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [ 
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            else:
                node = "สระว่ายน้ำเปิดให้บริการทุกวันเวลา 08:30 - 21:00 น. ไม่เว้นวันหยุดนักขัตฤกษ์ ยกเว้นวันที่สถาบันประกาศหยุด"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [ 
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
        #สนามแบดมินตัน
        elif "แบด" in query_result.get('queryText'):
            if "สมาชิก" in query_result.get('queryText'):
                node = "ประเภทสมาชิกของศูนย์กีฬา สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง แบ่งเป็นประเภทดังนี้\nประเภทที่ 1 : นักศึกษาระดับปริญญาตรีของสถาบัน\nประเภทที่ 2 : ข้าราชการ พนักงานสถาบัน ลูกจ้างของสถาบันสามีหรือภรรยาที่ชอบด้วยกฏหมายและบุตรที่ชอบด้วยกฏหมายของข้าราชการ พนักงานสถาบัน หรือลูกจ้างของสถาบัน พนักงานหรือลูกจ้างของโงเรียนสาธิตนานาชาติ สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง และพนักงานหรือลูกจ้างของหลักสูตรอื่นๆ ที่จัดตั้งภายใต้สถาบัน นักศึกษาระดับปริญญาโท นักศึกษาระดับปริญญาเอก และศิษย์เก่าของสถาบัน รวมทั้งข้าราชการ พนักงานสถาบัน ลูกจ้างของสถาบันที่เกษียณอายุไปแล้ว\nประเภทที่ 3 : นักศึกษาโรงเรียนสาธิตนานาชาติ สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง นักศึกษามหาวิทยาลัยซีเอ็มเคแอล นักเรียนหรือนักศึกษาหลักสูตรอื่นๆ ที่จัดตั้งภายใต้สถาบัน\nประเภทที่ 4 : บุคคลภายนอก"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [ 
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "ค่า" in query_result.get('queryText'):
                node = "อัตราค่าธรรมเนียมในการใช้บริการ (บาท/คน/ชั่วโมง) ตามประเภทของสมาชิก ดังนี้\nประเภทที่ 1, 2 และ 3\n08:30 - 16:00 น. : ฟรี\n16:00 น. - 21:00 น. : ฟรี\nประเภทที่ 4\n08:30 - 16:00 น. : 20 บาท\n16:00 น. - 21:00 น. : 60 บาท\nไม่เป็นสมาชิก\n08:30 - 16:00 น. : 40 บาท\n16:00 น. - 21:00 น. : 120 บาท\nค่าสมาชิก และค่าธรรมเนียมในการใช้บริการ อาจมีการเปลี่ยนแปลงได้ตามความเหมาะสม ในกรณีที่มีการเปลี่ยนแปลงให้เป็นไปตามประกาศสถาบัน"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [ 
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            else:
                node = "สนามแบดมินตันเปิดให้บริการทุกวันเวลา 08:30 - 21:00 น. ไม่เว้นวันหยุดนักขัตฤกษ์ ยกเว้นวันที่สถาบันประกาศหยุด"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [ 
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
        #ยิม
        elif "ยิม" in query_result.get('queryText') or "ออกกำลังกาย" in query_result.get('queryText'):
            if "สมาชิก" in query_result.get('queryText'):
                node = "ประเภทสมาชิกของศูนย์กีฬา สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง แบ่งเป็นประเภทดังนี้\nประเภทที่ 1 : นักศึกษาระดับปริญญาตรีของสถาบัน\nประเภทที่ 2 : ข้าราชการ พนักงานสถาบัน ลูกจ้างของสถาบันสามีหรือภรรยาที่ชอบด้วยกฏหมายและบุตรที่ชอบด้วยกฏหมายของข้าราชการ พนักงานสถาบัน หรือลูกจ้างของสถาบัน พนักงานหรือลูกจ้างของโงเรียนสาธิตนานาชาติ สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง และพนักงานหรือลูกจ้างของหลักสูตรอื่นๆ ที่จัดตั้งภายใต้สถาบัน นักศึกษาระดับปริญญาโท นักศึกษาระดับปริญญาเอก และศิษย์เก่าของสถาบัน รวมทั้งข้าราชการ พนักงานสถาบัน ลูกจ้างของสถาบันที่เกษียณอายุไปแล้ว\nประเภทที่ 3 : นักศึกษาโรงเรียนสาธิตนานาชาติ สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง นักศึกษามหาวิทยาลัยซีเอ็มเคแอล นักเรียนหรือนักศึกษาหลักสูตรอื่นๆ ที่จัดตั้งภายใต้สถาบัน\nประเภทที่ 4 : บุคคลภายนอก"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [ 
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "ค่า" in query_result.get('queryText'):
                node = "อัตราค่าธรรมเนียมในการใช้บริการ (บาท/คน/ชั่วโมง) ตามประเภทของสมาชิก ดังนี้\nประเภทที่ 1, 2 และ 3\n08:30 - 16:00 น. : 10 บาท\n16:00 น. - 21:00 น. : 20 บาท\nประเภทที่ 4\n08:30 - 16:00 น. : 20 บาท\n16:00 น. - 21:00 น. : 60 บาท\nไม่เป็นสมาชิก\n08:30 - 16:00 น. : 30 บาท\n16:00 น. - 21:00 น. : 80 บาท\nค่าสมาชิก และค่าธรรมเนียมในการใช้บริการ อาจมีการเปลี่ยนแปลงได้ตามความเหมาะสม ในกรณีที่มีการเปลี่ยนแปลงให้เป็นไปตามประกาศสถาบัน"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [ 
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            else:
                node = "ห้องออกกำลังกายเปิดให้บริการทุกวันเวลา 08:30 - 21:00 น. ไม่เว้นวันหยุดนักขัตฤกษ์ ยกเว้นวันที่สถาบันประกาศหยุด"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [ 
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
        #เทนนิส
        elif "เทนนิส" in query_result.get('queryText'):
            if "สมาชิก" in query_result.get('queryText'):
                node = "ประเภทสมาชิกของศูนย์กีฬา สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง แบ่งเป็นประเภทดังนี้\nประเภทที่ 1 : นักศึกษาระดับปริญญาตรีของสถาบัน\nประเภทที่ 2 : ข้าราชการ พนักงานสถาบัน ลูกจ้างของสถาบันสามีหรือภรรยาที่ชอบด้วยกฏหมายและบุตรที่ชอบด้วยกฏหมายของข้าราชการ พนักงานสถาบัน หรือลูกจ้างของสถาบัน พนักงานหรือลูกจ้างของโงเรียนสาธิตนานาชาติ สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง และพนักงานหรือลูกจ้างของหลักสูตรอื่นๆ ที่จัดตั้งภายใต้สถาบัน นักศึกษาระดับปริญญาโท นักศึกษาระดับปริญญาเอก และศิษย์เก่าของสถาบัน รวมทั้งข้าราชการ พนักงานสถาบัน ลูกจ้างของสถาบันที่เกษียณอายุไปแล้ว\nประเภทที่ 3 : นักศึกษาโรงเรียนสาธิตนานาชาติ สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง นักศึกษามหาวิทยาลัยซีเอ็มเคแอล นักเรียนหรือนักศึกษาหลักสูตรอื่นๆ ที่จัดตั้งภายใต้สถาบัน\nประเภทที่ 4 : บุคคลภายนอก"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [ 
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "ค่า" in query_result.get('queryText'):
                node = "อัตราค่าธรรมเนียมในการใช้บริการ (บาท/คน/ชั่วโมง) ตามประเภทของสมาชิก ดังนี้\nประเภทที่ 1, 2 และ 3\n08:30 - 16:00 น. : ฟรี\n16:00 น. - 21:00 น. : ฟรี\nประเภทที่ 4\n08:30 - 16:00 น. : 20 บาท\n16:00 น. - 21:00 น. : 40 บาท\nไม่เป็นสมาชิก\n08:30 - 16:00 น. : 40 บาท\n16:00 น. - 21:00 น. : 80 บาท\nค่าสมาชิก และค่าธรรมเนียมในการใช้บริการ อาจมีการเปลี่ยนแปลงได้ตามความเหมาะสม ในกรณีที่มีการเปลี่ยนแปลงให้เป็นไปตามประกาศสถาบัน"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [ 
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            else:
                node = "สนามเทนนิสเปิดให้บริการทุกวันเวลา 08:30 - 21:00 น. ไม่เว้นวันหยุดนักขัตฤกษ์ ยกเว้นวันที่สถาบันประกาศหยุด"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [ 
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
        #ติดต่อ
        elif "ติดต่อ" in query_result.get('queryText') or "osda" in query_result.get('queryText'):
            node = "หากต้องการติดต่องานใด สามารถเข้าไปหาข้อมูลได้ที่ คุยกับพี่ค๊อกโค่ -> แสดงข้อมูลคำถามในระบบ -> เลือกหน่วยงานต่างๆ"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [ 
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #เปลี่ยนชื่อ
        elif "เปลี่ยน" in query_result.get('queryText') and "ชื่อ" in query_result.get('queryText'):
            node = "2.1 นักศึกษากรอกคำร้องขอเปลี่ยนชื่อ-นามสกุล-คำนำหน้าชื่อ\n2.2 แนบสำเนาหลักฐานการเปลี่ยนชื่อ-นามสกุล-คำนำหน้าชื่อ พร้อมรับรองสำเนาถูกต้อง\nข้อควรระวัง \n1. นักศึกษาที่สำเร็จการศึกษาหรือมีการส่งรายชื่อไปขออนุมัติสำเร็จการศึกษา ไม่สามารถเปลี่ยนชื่อ-นามสกุลได้\n2. กรณีเปลี่ยนคำนำหน้าชื่อเป็น ว่าที่ร้อยตรี หากยื่นเปลี่ยนหลังสำเร็จการศึกษา ต้องตรวจสอบว่าคำแต่งตั้งอนุมัติก่อนสำเร็จการศึกษาหรือไม่ หากอนุมัติก่อนสามารถเปลี่ยนได้"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [ 
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #กีฬา
        elif "กีฬา" in query_result.get('queryText'):
            if "จัด" in query_result.get('queryText'):
                node = "กีฬามหาวิทยาลัยแห่งประเทศไทย จัดขึ้น 2 รอบ คือ รอบคัดเลือกซึ่งมีกีฬาประเภททีมทั้งหมด จัดการแข่งขันประมาณต้นเดือนพฤศจิกายน และรอบมหกรรม จะรวมที่ผ่านรอบคัดเลือกเข้ามาแข่งขัน จัดการแข่งขันประมาณ เดือนมกราคม หรือแล้วแต่เจ้าภาพนั้น"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [ 
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "สมัคร" in query_result.get('queryText'):
                node = "ผู้ที่สมัครเข้าร่วมการแข่งขันจะต้องเข้าคัดตัวแทนของชนิดกีฬานั้น กับชมรมกีฬาต่างๆ ที่มีการเข้าร่วมการแข่งขัน จะเริ่มสมัครประมาณเดือนสิงหาคม ในแต่ละปีมีชนิดกีฬาที่จัดการแข่งขันไม่เท่ากัน ขึ้นอยู่กับเจ้าภาพจัดการแข่งขัน"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [ 
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "คุณสมบัติ" in query_result.get('queryText'):
                node = "ผู้สมัครเข้าแข่งขันกีฬามหาวิทยาลัยต้องเป็นนักศึกษาหรือนักศึกษาบัณฑิต ตาม หลักสูตรการศึกษาระดับปริญญาตรีขึ้นไป โดยต้องมีคุณสมบัติ ดังนี้\n\n1. กรณีเป็นนักศึกษาแรกเข้า และเข้าแข่งขันกีฬามหาวิทยาลัยครั้งแรก ต้อง ลงทะเบียนเรียน ในภาคการศึกษาที่ 1 หรือ ภาคต้น ของปีการศึกษาที่มีการแข่งขันกีฬามหาวิทยาลัย ไม่น้อยกว่า 12 หน่วยกิต สำหรับนักศึกษาบัณฑิตแรกเข้า ต้องลงทะเบียนเรียนในภาคการศึกษาที่ 1 หรือ ภาคต้น ของปีการศึกษาที่มีการแข่งขันกีฬามหาวิทยาลัย ไม่น้อยกว่า 6 หน่วยกิต\n2. กรณีไม่ใช่นักศึกษาแรกเข้า ต้องลงทะเบียนเรียนในภาคการศึกษาที่ 1 หรือ ภาคต้น ของปีการศึกษาที่มีการแข่งขันกีฬามหาวิทยาลัย และในปีการศึกษาก่อนการแข่งขันกีฬามหาวิทยาลัย 1 ปี จะต้องมีหน่วยกิตก้าวหน้า ไม่น้อยกว่า 18 หน่วยกิต และ ต้องได้คะแนนเฉลี่ยสะสม ไม่น้อยกว่า 2.00 ในระบบ คะแนนเต็ม 4.00\nกรณีไม่ใช่นักศึกษาบัณฑิตแรกเข้า ต้องลงทะเบียนเรียนในภาคการศึกษาที่ 1 หรือ ภาคต้น ของปีการศึกษาที่มีการแข่งขันกีฬามหาวิทยาลัย และในปีการศึกษาก่อนการแข่งขันกีฬามหาวิทยาลัย 1 ปี จะต้องมีหน่วยกิตก้าวหน้า ไม่น้อยกว่า 6 หน่วยกิต และ ต้องได้คะแนนเฉลี่ยสะสม ไม่น้อยกว่า 3.00 ใน ระบบคะแนนเต็ม 4.00\n3.ต้องมีอายุไม่เกิน 28 ปี โดยให้นับถึง วันที่ 1 มกราคม ของปีที่สมัครเข้าแข่งขัน เว้นแต่ ระเบียบชนิดกีฬาใดก าหนดอายุไว้ ต่ำากว่า 28 ปี ก็ให้เป็นไปตามระเบียบชนิดกีฬานั้น\n4.ต้องไม่อยู่ในระหว่างการถูกลงโทษตัดสิทธิ เข้าร่วมการแข่งขันกีฬามหาวิทยาลัย หรือการแข่งขันของสมาคมกีฬาสมัครเล่นแห่งประเทศไทย หรือของการกีฬาแห่งประเทศไทย ทั้งนี้ หากการลงโทษตามวรรคแรก เกิดขึ้นภายหลังวันสมัครเข้าร่วมการแข่งขัน ให้ผู้สมัครเข้าร่วมการแข่งขันผู้นั้น เสียสิทธิในการเข้าร่วมการแข่งขันกีฬามหาวิทยาลัยปีนั้นด้วย"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [ 
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
            elif "สนาม" in query_result.get('queryText'):
                node = "ติดตามการ เปิด-ปิด ศูนย์กีฬาพระจอมเกล้าลาดกระบังได้ที่เพจ สำนักงานบริหารทรัพย์สิน สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [ 
                        {
                            "text": {"text": [node]},
                            "platform": "LINE"
                        }
                    ]
                }
        #ถ่ายเอกสาร
        elif "ถ่ายเอกสาร" in query_result.get('queryText'):
            node = "ร้านถ่ายเอกสารอยู่ชั้น 3 อาคารเฉลิมพระเกียรติ (อาคารเดิม)"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [ 
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #ขอรถ
        elif "ขอรถ" in query_result.get('queryText'):
            node = "รับแบบฟอร์มขอใช้รถส่วนกลางจากสำนักงานกิจการนักศึกษาและศิษย์เก่าสัมพันธ์พร้อมทั้งแนบโครงการที่ได้รับการอนุมัติ"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [ 
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #ละหมาด
        elif "ละหมาด" in query_result.get('queryText'):
            node = "ห้องสมุดจัดสถานที่สำหรับละหมาดไว้ อาคารเดิม ชั้น 3 ห้องบริการวิทยานิพนธ์ และสามารถใช้ห้องอาบน้ำได้ที่ชั้น 4"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [ 
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #ไม่ได้ลงทะเบียน
        elif "ไม่ได้" in query_result.get('queryText') and ("ลงทะเบียน" in query_result.get('queryText') or "ลงเรียน" in query_result.get('queryText')):
            node = "ต้องรอไปลงทะเบียนเรียนจริง ในช่วงเวลาที่กำหนดให้ลงทะเบียนเรียนจริง รายละเอียดต่างๆ ดูได้จากปฏิทินการศึกษา"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [ 
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #ถ่ายเอกสาร
        elif "กิจกรรม" in query_result.get('queryText'):
            node = "เข้าไปเขียนขออนุมัติโครงการ (ในระบบ) ที่ลิงก์ osda.kmitl.ac.th/e-filing/login"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [ 
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #เทียบวิชา
        elif "เทียบ" in query_result.get('queryText') and "วิชา" in query_result.get('queryText'):
            node = "นักศึกษาต้องไปติดต่อขอทำเรื่องเทียบโอนรายวิชาที่ส่วนงานวิชาการของคณะ/วิทยาลัย ที่นักศึกษาสังกัดนักศึกษาต้องไปติดต่อขอทำเรื่องเทียบโอนรายวิชาที่ส่วนงานวิชาการของคณะ/วิทยาลัย ที่นักศึกษาสังกัด"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [ 
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #ปฏิทิน
        elif "ค่าเทอม" in query_result.get('queryText') and "ปิดเทอม" in query_result.get('queryText'):
            node = "สามารถตรวจสอบข้อมูลได้ที่เว็บไซต์ดังนี้ https://www.reg.kmitl.ac.th/educalendar/"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [ 
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #ชมรม
        elif "ชมรม" in query_result.get('queryText'):
            node = "เข้าไปเลือกกิจกรรมได้ที่ https://osda.kmitl.ac.th"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [ 
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #ใส่ชุดธรรมดาได้วันไหน
        elif "ใส่ชุด" in query_result.get('queryText'):
            node = "สามารถใส่ชุดธรรมดา หรือชุดไปรเวทมาได้ทุกวันพฤหัสบดี"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [ 
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #ใส่ชุดธรรมดาได้วันไหน
        elif "ใส่ชุด" in query_result.get('queryText'):
            node = "สามารถใส่ชุดธรรมดา หรือชุดไปรเวทมาได้ทุกวันพฤหัสบดี"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [ 
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }
        #ชื่ออธิการ
        elif "อธิการ" in query_result.get('queryText') and elif "ชื่อ" in query_result.get('queryText'):
            node = "อธิการบดีของเรามีชื่อว่าพี่เอ้ ชื่อจริงว่าสุชัชวีร์ สุวรรณสวัสดิ์"
            return {
                "displayText": '25',
                "source": "webhookdata",
                "fulfillmentMessages": [ 
                    {
                        "text": {"text": [node]},
                        "platform": "LINE"
                    }
                ]
            }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
