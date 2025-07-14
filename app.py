# app.py
import streamlit as st
import requests

# Page config
st.set_page_config(page_title="Recipe Recommender", page_icon="🥘", layout="wide")

st.markdown("""
    <style>
    .title {font-size:38px !important; font-weight:600; color:#FF4B4B;}
    .subsection {font-size:24px !important; font-weight:500; margin-top:30px;}
    .divider {margin-top: 40px; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🥘 Smart Recipe Recommendation ChatBot</div>', unsafe_allow_html=True)

# Side-by-side titles
title_col1, title_col2 = st.columns([1, 1])
with title_col1:
    st.markdown('<div class="subsection">🥕 Enter Your Ingredients</div>', unsafe_allow_html=True)
with title_col2:
    st.markdown('<div class="subsection">🧮 Calorie & Nutrition Analysis</div>', unsafe_allow_html=True)

# Content layout
col1, col2 = st.columns([1, 1])
with col1:
    ingredients = st.text_input("Separate ingredients with commas", placeholder="e.g., tomato, onion, cheese")

    def format_steps(instruction_text):
        steps = instruction_text.split('. ')
        return [step.strip() for step in steps if step.strip()]

    if st.button("🔍 Recommend Recipes"):
        with st.spinner("Looking for delicious ideas... 🍳"):
            try:
                res = requests.post("https://recipe-bot-1.onrender.com/recommend", json={"ingredients": ingredients})
                data = res.json()

                if data:
                    st.success("✅ Recipes Found!")
                    for recipe in data:
                        with st.expander(f"🍽 {recipe['recipe']}", expanded=True):
                            st.markdown(f"**🧂 Ingredients:** `{recipe['ingredients']}`")
                            st.markdown("**📖 Instructions:**")
                            steps = format_steps(recipe["instructions"])
                            for i, step in enumerate(steps, 1):
                                st.markdown(f"`Step {i}`: {step}")
                else:
                    st.warning("🤖 Hmm... I couldn't find anything that fits those ingredients. Try fewer or more common ones.")
            except Exception as e:
                st.error(f"⚠️ Error fetching recipes: {e}")

with col2:
    # st.markdown('<div class="subsection">🧮 Calorie & Nutrition Analysis</div>', unsafe_allow_html=True)
    calorie_ingredients = st.text_area("Enter ingredients (one per line):", height=160, placeholder="e.g.,\npotato\nonion\ncarrot")

    if st.button("🧪 Analyze Calories"):
        lines = [line.strip() for line in calorie_ingredients.split('\n') if line.strip()]
        if lines:
            with st.spinner("Crunching the nutrition data... 🍎"):
                try:
                    res = requests.post("https://recipe-bot-1.onrender.com/calorie", json={"ingredients": lines})
                    result = res.json()

                    if res.status_code == 200 and "error" not in result:
                        st.success("✅ Calorie Analysis Result")
                        col_a, col_b, col_c, col_d = st.columns(4)
                        col_a.metric("🔥 Calories", f"{result['calories']:.2f} kcal")
                        col_b.metric("💪 Protein", f"{result['protein']:.2f} g")
                        col_c.metric("🥑 Fat", f"{result['fat']:.2f} g")
                        col_d.metric("🍞 Carbs", f"{result['carbs']:.2f} g")
                    else:
                        if "message" in result:
                            st.warning(f"❗ Error: {result['message']}")
                        else:
                            st.warning("❗ Could not analyze the given ingredients.")

                except Exception as e:
                    st.error(f"⚠️ Error: {e}")
        else:
            st.warning("Please enter at least one ingredient.")

# Footer
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown("🌱 *Powered by LangChain, Streamlit, and Edamam API*", unsafe_allow_html=True)
