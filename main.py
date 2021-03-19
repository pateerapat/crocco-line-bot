import json, random
from flask import Flask, request
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
