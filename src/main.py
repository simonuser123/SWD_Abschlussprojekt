import streamlit as st
import matplotlib.pyplot as plt
from mechanism import Joint, Link, Mechanism
import pandas as pd
import numpy as np

# ++++++ Page Settings ++++++
st.set_page_config(layout="wide")

m1 = Mechanism([0],[0])

st.title("Überschrift!")

col1, col2 = st.columns(2)
with col1:
    tab1, tab2 = st.tabs(["Add", "Edit"])
    with tab1:

    # ++++++ add new point ++++++
        st.write("add new Point")
        newNamePoint = st.text_input("name", key = "new_name_point")
        newXPoint = float( st.text_input("x-Pos.",key = "new_x_point", value= 0) )
        newYPoint = float( st.text_input("y-Pos.",key = "new_y_point", value= 0) )
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
        all_points = Joint.find_all_joints()
        st.write("add new Link")
        linkName = st.text_input("link name")
        firstPointName = st.selectbox("select first Point",all_points)
        secondPointName = st.selectbox("select second Point",all_points)

        if st.button("add link", key="addLink"):
            firstPoint = Joint.find_by_name(firstPointName)                                               
            secondPoint = Joint.find_by_name(secondPointName)
            try: 
                linkName = Link(linkName, firstPoint, secondPoint)
                linkName.initialize_self_lenght()
                linkName.save()
                #m1.add_link(newNameLink)
            except:
                st.error("Error!")

    # ++++++ Alle Joints abrufen ++++++
        all_joints_info = Joint.find_joints_info()  # Alle gespeicherten Joints abrufen

        if not all_joints_info:
            st.warning("Noch keine Joints gespeichert.")
        else:
            df = pd.DataFrame(all_joints_info)
            required_columns = ["name", "x", "y", "is_fixed", "on_circular_path"]
            st.write(df)



with col2:
# ++++++ erstelle Plot ++++++
    fig, ax = plt.subplots()
    x= m1.get_all_x()
    y= m1.get_all_y() 
    ax.plot(x, y)
    ax.plot(2,3,'o',  label= 'Label')
    st.pyplot(fig)


if __name__ == "__main__":
#     # print(s1.get_current_length())
#     # print(m1.get_all_x())
#     # print(m1.get_all_y())

# #++++++++++++++++++++++++++++++++++
#     p0= Joint(1,0,0)
#     p1= Joint(2,10,10)
#     p0.save()
#     p1.save()
#     #g3= Joint(3,20,10)

#     #s1= Link(p0,p1)
#     #s2= Link(g2,g3)

#     #m1= Mechanism([g1,g2,g3],[s1,s2])
#     #print(Joint.find_joints_info())
#     firstP = Joint.find_by_name("p0")                                               
#     secondP = Joint.find_by_name("p1")

#     s1=Link("test", firstP,secondP)
#     s1.save()
#     print(s1.get_current_length())

#     #Joint(data["name"], data["x"], data["y"], data["is_fixed"], data["on_circular_path"])
    pass