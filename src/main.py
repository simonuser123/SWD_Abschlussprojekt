import streamlit as st
import matplotlib.pyplot as plt
from mechanism import Joint, Link, Mechanism
import pandas as pd
import numpy as np

# ++++++ Page Settings ++++++
st.set_page_config(layout="wide")

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

        #if newNamePoint
        if st.button("add point", key= "addPoint"):
            try: 
                newNamePoint = Joint(newNamePoint, newXPoint, newYPoint, newPointFixed, newPointOnCircularPath)
                newNamePoint.save()
                #newMechanism.add_joint(newNamePoint)
            except:
                st.error("Error!")
        #else: st.error("Bitte Namen eingeben")

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
            except:
                st.error("Error!")

    # ++++++ Alle Joints abrufen ++++++
        all_joints_info = Joint.find_joints_info() 

        if not all_joints_info:
            st.warning("Noch keine Joints gespeichert.")
        else:
            df = pd.DataFrame(all_joints_info)
            required_columns = ["name", "x", "y", "is_fixed", "on_circular_path"]
            st.write(df)

    # ++++++ Alle Links abrufen ++++++
        all_links_info = Link.find_link_info()  # Alle gespeicherten Joints abrufen

        if not  all_links_info:
            st.warning("Noch keine Links gespeichert.")
        else:
            df1 = pd.DataFrame( all_links_info)
            required_columns = ["name", "Joint A", "Joint B"]
            st.write(df1)

        newMechanismName = st.text_input("Mechanism name")
        newMechanism = Mechanism(newMechanismName, [], [])
        if st.button("Save mech"):

            for joint in Joint.find_joints_info():
                joint = Joint.find_by_name(joint["name"]) 
                if joint:
                    newMechanism.add_joint(joint)

            for link in Link.find_link_info():
                link = Link.find_by_name(link["name"])
                if link:
                    newMechanism.add_link(link)

            newMechanism.save()
  

with col2:
# ++++++ erstelle Plot ++++++
    fig, ax = plt.subplots()
    for points in Joint.find_joints_info():
        ax.plot(points["x"],points["y"],'o',  label= points["name"])
    for link in Link.find_link_info():
        x = (link["joint_a"]["x"],link["joint_b"]["x"])
        y = (link["joint_a"]["y"],link["joint_b"]["y"])
        ax.plot(x,y)
    #ax.legend()
    st.pyplot(fig)


if __name__ == "__main__":
#    mech1 = Mechanism("Viergelenkkette",[c,p0,p1,p2],(l0,l1,l2))
#     # print(s1.get_current_length())
#     # print(m1.get_all_x())
#     # print(m1.get_all_y())

# # #++++++++++++++++++++++++++++++++++
    # p0= Joint("p0",0,0)
    # p0.save()
    # p1= Joint("p1",1,1)
    # p1.save()
    # s1= Link("s1",p0,p1)
    # s1.save()
    # for links in Link.find_link_info():
    #    # print(links)
    #     print(links["joint_a"]["x"])
#     #print(Joint.find_all_joints())
#     #print(Joint.find_joints_info())
#     #print(p0.get_position())
#     for points in Joint.find_joints_info():
#         print(points['name'])
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

#     #Joint(data["name"], data["x"], data["y"], data["is_fixed"], data["on_circular_path"]
    pass