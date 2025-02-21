import streamlit as st
import matplotlib.pyplot as plt

st.title("Überschrift!")

fig, ax = plt.subplots()
x = [10, 20, 30]
y = [20, 30, 40]

ax.plot(x, y)

st.pyplot(fig)
