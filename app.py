from dotenv import load_dotenv
import os
import re

# Load the .env file
load_dotenv()

# Access the API key
api_key = os.getenv('GROQ_API_KEY')

from flask import Flask,request,render_template
app=Flask(__name__)
from langchain_groq import ChatGroq

llm = ChatGroq(
    model_name="llama-3.1-70b-versatile",
    temperature=0,
    groq_api_key=api_key

)
from langchain_core.prompts import PromptTemplate
prompt_extract = PromptTemplate(
    input_variables=['State', 'District', 'Town'],
    template="""
    Urban Heat Island (UHI) Effect Assessment:

    Location:
    State: {State}
    District: {District}
    Town: {Town}

    Determine if the specified location falls under the Urban Heat Island (UHI) effect.
    If you are unsure, please respond with 'no' and provide reasoning based on factors like population density, urban development, and geographical characteristics.
    
    1. Answer only "yes" or "no". If "yes", explain briefly in 4-5 bullet points numberwise why (in simple language).
    2. Provide 4-5 concise, actionable recommendations that can help reduce the UHI effect in this location (If the answer in yes). If no then recoomend like that how to maintain that temperature so that it will not come under the areas of UHI effect.
    output shuld be in the format 
    Answer:
    
    Reasoning:
    
    
    Recommendations:
    """
)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST','GET'])

def recommend():
    if request.method=="POST":
        State=request.form['State']
        District=request.form['District']
        Town=request.form['Town']
        
        input_data = {
            'State': State,
            'District': District,
            'Town':Town
        }
        chain_extract = prompt_extract | llm
        res = chain_extract.invoke(input=input_data)
        print(res.content)
        pattern = r"Answer:(.*?)\n\nReasoning:\n"
        PREDICTION=re.findall(pattern, res.content, re.DOTALL)
        print(f"PREDICTION regex match: {PREDICTION}")
        Reasons = re.findall(r"\n\nReasoning:\n(.*?)\n\nRecommendations:\n",res.content ,re.DOTALL)
        Recommendations=re.findall(r"\n\nRecommendations:\n(.*?)$",res.content,re.DOTALL)
        
        
        PREDICTION = [reason.strip() for reason in PREDICTION[0].strip().split('\n') if reason.strip()] if PREDICTION else []
        Reasons = [reason.strip() for reason in Reasons[0].strip().split('\n') if reason.strip()] if Reasons else []
        Recommendations=[reason.strip() for reason in Recommendations[0].strip().split('\n') if reason.strip()] if Recommendations else []
        
        return render_template ('result.html',PREDICTION=PREDICTION ,Reasons=Reasons, Recommendations=Recommendations)
    



        
        
    return render_template('index.html')  





if __name__=="__main__":
    app.run(debug=True)