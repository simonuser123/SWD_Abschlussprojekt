import streamlit as st
import matplotlib.pyplot as plt
from mechanism import Joint, Link, Mechanism
import pandas as pd
import numpy as np

m1 = Mechanism([0],[0])
st.title("Überschrift!")
tab1, tab2 = st.tabs(["Add", "Edit"])
with tab1:

# ++++++ add new point ++++++
    st.write("add new Point")
    newNamePoint = st.text_input("name", key = "new_name_point")
    newXPoint = st.text_input("x-Pos.",key = "new_x_point", value= 0) 
    newYPoint = st.text_input("y-Pos.",key = "new_y_point", value= 0)
    newPointFixed = st.checkbox("is Point fixed?")
    newPointOnCircularPath = st.checkbox("is Point on Circular path?")

    if st.button("add point", key= "addPoint"):
        try: 
            newNamePoint = Joint(newNamePoint, newXPoint,newYPoint)
            newNamePoint.save()
            m1.add_joint(newNamePoint)
        except:
            st.error("Error!")

# ++++++ add new line ++++++
    st.write("add new Point")
    if st.button("add link"):
        pass

# ++++++ Tabelle für Streamlit +++++
df = pd.DataFrame({
    "Link": [],
    "Start-Point": [],
    "End-Point": [],  
    "is_fixed": [],
    "on_radius": []
})

#edited_df = st.data_editor(df, num_rows="dynamic") 
#st.write("current settings")
st.write(df)


#g1= Joint(1,0,0)
#g2= Joint(2,10,10)
#g3= Joint(3,20,10)

#s1= Link(g1,g2)
#s2= Link(g2,g3)

#m1= Mechanism([g1,g2,g3],[s1,s2])

# ++++++ erstelle Plot ++++++
fig, ax = plt.subplots()
x= m1.get_all_x()
y= m1.get_all_y() 
ax.plot(x, y)
st.pyplot(fig)

m1.print_info()

if __name__ == "__main__":
    print(s1.get_current_length())
    print(m1.get_all_x())
    print(m1.get_all_y())