import streamlit as st
from PIL import Image
import pandas as pd
import pymysql
from sqlalchemy import create_engine
import easyocr
import numpy as np
import base64
from streamlit_option_menu import option_menu
import re
# Connect to the MySQL database
mydb = pymysql.connect(
  host="127.0.0.1",
  user="root",
  password="qwerty123",
  database="bizcardx"
)
# Create a cursor object
mycursor = mydb.cursor()

# Create a connection engine to the database
engine = create_engine('mysql+pymysql://root:qwerty123@localhost:3306/bizcardx')

#easyocr image reading and printing
reader = easyocr.Reader(['en'])
#image_path = r'C:\Users\Admin\PycharmProjects\pythonProject\venv\bcimages\bc2.jpg'  # Replace with the path to your image
#image = Image.open(image_path)
#results = reader.readtext(image,paragraph=True)

#streamlit interface

# Open and display the image
biz_image = Image.open(r'C:\Users\Admin\PycharmProjects\pythonProject\venv\Capture.PNG')
st.set_page_config(page_title="BizCardX_Extraction", page_icon=biz_image, layout="wide",initial_sidebar_state="expanded")
st.markdown("<h1 style='text-align: center; color: yellow;'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)

# Streamlit app code goes here...
def setting_bg():
    st.markdown(f""" 
    <style>
        .stApp {{
            background: linear-gradient(to right, #800080, #A52A2A);
            background-size: cover;
            transition: background 0.5s ease;
        }}
        h1,h2,h3,h4,h5,h6 {{
            color: #f3f3f3;
            font-family: 'Roboto', sans-serif;
        }}
        .stButton>button {{
            color: #4e4376;
            background-color: #f3f3f3;
            transition: all 0.3s ease-in-out;
        }}
        .stButton>button:hover {{
            color: #f3f3f3;
            background-color: #2b5876;
        }}
        .stTextInput>div>div>input {{
            color: #4e4376;
            background-color: #f3f3f3;
        }}
    </style>
    """,unsafe_allow_html=True)
setting_bg()

st.sidebar.image(biz_image,caption="BizCardX: Extracting Business Card Data",width=200)

st.write("Upload an Image of a Business Card to Extract the Data.")


# Increase tab width
st.markdown(
    """
    <style>
    .stTab > div {
        max-width: 1000px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Create tabs
tabs = st.columns(3)
tab_selected = st.radio("Select Tab", ["Home", "Upload and Extract", "Modify"])

# Display content based on selected tab
if tab_selected == "Home":
    st.markdown("## :green[**Technologies Used :**] Python, easy OCR, Streamlit, SQL, Pandas")
    st.markdown("## :green[**Overview :**] In this streamlit web app, you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify, or delete the extracted data in this app. This app also allows users to save the extracted information into a database along with the uploaded business card image. The database can store multiple entries, each with its own business card image and extracted information.")

if tab_selected == "Upload and Extract":
    st.markdown("### Upload a Business Card")
    uploader_file = st.file_uploader("choose an image", type=["jpg"])
    if uploader_file is not None:
        img=Image.open(uploader_file)
        st.image(img,caption="Uploaded Image")
        result = reader.readtext(img,detail=0)
        #extract name
        def name(img):
            for i in img:
                return i
        #extract designation
        def designation(img):
            for i in img:
                return img[1]

        #extract phone number
        def phone_number(img):
            num=[]
            for i in img:
                if re.findall(r'^[+]',i):
                    num.append(i)
                elif(re.findall(r'^\d{3}-\d{3}-\d{4}$',i)):
                    num.append(i)
            return num

        #extract website

        def website(img):
            website = ""
            for i in img:
                if re.match(r'^WWW(?=.*\.com)', i):
                    website = i
                elif re.match(r'^\w+\.com$', i):
                    website = ('WWW.' + i)
            if len(website) == 0:
                website = "Not Available"
            else:
                return website


        # extracting email
        def email(img):
            for i in img:
                if (re.findall(r'[\w\.-]+@[\w\.-]+',i)):
                    return i
        #extracting address

        def address(img):
            for i in img:
                if (re.findall(r'^123+\s[\w\.-]+',i)):
                    return i[0:10]
        #extract business type

        def b_type(img):
            for i in img[-1]:
                if len(img[-1])>5:
                    return img[-1]
                else:
                    return img[-2]
        #extract district

        def district(img):
            for i in img:
                if(re.search(r'^123+\s',i)):
                    if len(i[10:20])>6:
                        return i [11:20].replace(",","")
                elif(re.search(r'\bBangalore\b',i)):
                    return i.replace(";","")
            return "not available"

        # extract pincode

        def pincode(img):
            pincode="not"
            for i in img:
                pin_match=re.search(r'\d{6}|\b(\d{3}\s*\d{3})\b',i)
                if pin_match:
                    pincode=pin_match.group(0).replace(' ','')
                return pincode
        #extract state

        def state(img):
            for i in img:
                match=re.search(r'TamilNadu',i)
                if match:
                    return match.group()
            return 'not found'


        def data(img):
            data = {}
            data['Name'] = name(img)
            data['Designation'] = designation(img)
            data['Domain'] = b_type(img)
            data['Contact'] = phone_number(img)
            data['Email'] = email(img)
            data['Website'] = website(img)
            data['Address'] = address(img)
            data['District'] = district(img)
            data['State'] = state(img)
            data['Pincode'] = pincode(img)
            return data

        df1=pd.DataFrame(data(result))
        df1.to_csv('Extracted_data.csv',index=False)
        df=pd.read_csv('Extracted_data.csv')
        st.success("###Data Extracted!")
        st.dataframe(df)



        image_upload_button=st.button("Upload the image in MySql")
        st.write("Click the above button to upload the image in MySql")

        if image_upload_button is not None and image_upload_button:
            if uploader_file is not None:
                image = Image.open(uploader_file)
                img_bytes = uploader_file.read()
                img_base64 = base64.b64encode(img_bytes).decode()
                sql = "INSERT INTO biz_image (image) VALUES (%s)"
                val = (img_base64,)
                mycursor.execute(sql, val)
                mydb.commit()
                st.write("Image uploaded to MySQL successfully!")
        st.empty()

        data_upload_button=st.button("Upload extracted data into Mysql")
        if data_upload_button is not None and data_upload_button:
            if uploader_file is not None:
                img= Image.open(uploader_file)
                st.image(img, caption="Uploaded Image")
                result= reader.readtext(img,detail=0)
                mycursor.execute('''CREATE TABLE IF NOT EXISTS card_datas
                                   (id INT PRIMARY KEY AUTO_INCREMENT,
                                    Name TEXT,
                                    Designation TEXT,
                                    Domain TEXT,
                                    Contact VARCHAR(255),
                                    Email TEXT,
                                    Website TEXT,
                                    Address TEXT,
                                    District TEXT,
                                    State TEXT,
                                    Pincode VARCHAR(10)
                                    )''')
                # Extract relevant data from the results
                for i, row in df.iterrows():
                    # here %S means string values
                    sql = """INSERT INTO card_datas(Name, Designation, Domain, Contact, Email, Website, Address, District, State, Pincode)
                                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                    mycursor.execute(sql, tuple(row))
                    # the connection is not auto committed by default, so we must commit to save our changes
                    mydb.commit()
                st.success("#### Uploaded to database successfully!")
        st.empty()

if tab_selected == "Modify":
    col1, col2, col3 = st.columns([3, 3, 2])
    col2.markdown("Alter or Delete the data here")
    column1, column2 = st.columns(2, gap="small")
    try:
        with column1:
            mycursor.execute("SELECT Name FROM card_datas")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a name to update", list(business_cards.keys()))
            st.markdown("#### Update or modify any data below")
            mycursor.execute(
                "SELECT Name, Designation, Domain, Contact, Email, Website, Address, District, State, Pincode FROM card_datas WHERE Name=%s",
                (selected_card,))
            result = mycursor.fetchone()
            # DISPLAYING ALL THE INFORMATIONS
            Name = st.text_input("Name", result[0])
            designation = st.text_input("Designation", result[1])
            domain = st.text_input("Domain", result[2])
            mobile_number = st.text_input("Contact", result[3])
            email = st.text_input("Email", result[4])
            website = st.text_input("Website", result[5])
            address = st.text_input("Address", result[6])
            district=st.text_input("District",result[7])
            state = st.text_input("State", result[8])
            pin_code = st.text_input("Pincode", result[9])

            if st.button("Commit changes to DB"):
                # Update the information for the selected business card in the database
                mycursor.execute("""UPDATE card_datas SET Name=%s, Designation=%s, Domain=%s, Contact=%s, Email=%s, Website=%s, Address=%s, District=%s, State=%s, Pincode=%s
                                               WHERE Name=%s""", (
                    Name, designation, domain, mobile_number, email, website, address, district,state,pin_code,
                    selected_card))
                mydb.commit()
                st.success("Information updated in the database successfully.")

        with column2:
            mycursor.execute("SELECT Name FROM card_datas")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a  name to delete", list(business_cards.keys()))
            st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
            st.write("#### Proceed to delete this card?")

            if st.button("Yes, delete Business Card"):
                mycursor.execute(f"DELETE FROM card_datas WHERE Name='{selected_card}'")
                mydb.commit()
                st.success("Business card information deleted from the database.")
    except:
        st.warning("There is no data available in the database")

    if st.button("View updated data"):
        mycursor.execute("SELECT Name, Designation, Domain, Contact, Email, Website, Address, District, State, Pincode FROM card_datas")
        updated_df = pd.DataFrame(mycursor.fetchall(), columns=["Name","Designation","Domain","Contact","Email","Website","Address","District","State","Pincode"])
        st.write(updated_df)
