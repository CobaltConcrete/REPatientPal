import os
import requests
import google.generativeai as genai
import translators as ts
from gtts import gTTS

translated_text = """
## John Doe嘅簡化醫療報告

**患者信息：**

* **姓名：** John Doe
* **出生日期：** 1980年1月15日
* **性別：**男
* ** 地址：** 123 Main Street， Anytown， USA
* **電話：**（555）123-4567
* **緊急聯繫人：** Jane Doe （配偶），（555）987-6543

**主訴：** John Doe 在過去兩周內出現持續的**腹痛**和偶爾的**噁心**。

**現病史：** Mr. Doe報告說**腹痛**局限於**右下腹**。 他否認有任何**發燒**、**嘔吐**或**排便習慣**的改變。 他沒有注意到他的大便中有任何**血液**。

**既往病史：**

***高血壓**（用**賴諾普利**控制）
***闌尾切除術 **（10年前）

**藥物：**

1. **赖诺普利**每日10毫克
2. **辛伐他汀**每日20毫克

**藥物過敏 ： ** 沒有已知的藥物過敏。

**社會歷史：** Mr. Doe 不吸煙，偶爾也會飲酒。 佢係一名會計師，過住久坐唔郁嘅生活方式。

**家族史：** 他的父親有**冠狀動脈疾病**的病史**，他的母親患有**2型糖尿病**。

**重要的醫學術語：**

* **腹痛：**胃部疼痛。
* **惡心：**感覺胃不舒服。
* **右下腹：**胃的右下部分。
* **高血壓：**高血壓。
* **賴諾普利：**一種治療高血壓的藥物。
***闌尾切除術：**手術切除闌尾。
* **辛伐他汀：**一種降低膽固醇的藥物。
* **冠狀動脈疾病：**向心臟供血的動脈變窄或阻塞的疾病。
* **2型 糖尿病：** 身體不能正確使用胰島素的情況。

**註：**這是醫療報告的簡化摘要。 它唔包括所有詳細信息。 最好諮詢醫療保健專業人員以進行完整和準確嘅醫療評估。
"""

# Language in which you want to convert
language = "yue"

# Creating an object for gTTS
speech = gTTS(text=translated_text, lang=language)

# Saving the converted audio in a mp3 file
speech.save("cantonese.mp3")

