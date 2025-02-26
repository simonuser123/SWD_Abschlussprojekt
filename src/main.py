import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from mechanism import Joint, Link, Mechanism
from simulation_manager import SimulationManager
from mechanism import FourBarLinkage

# ++++++ Page Settings ++++++
#st.set_page_config(layout="wide")

st.title("Live- Editor")

#col1, col2 = st.columns(2)
#st.sidebar["side"]
#tab1, tab2 = st.tabs(["Add", "Edit"])

with st.sidebar:
    st.title("Settings")
    with st.form("Save Point"):
    # ++++++ add new point ++++++
        st.write("add new Point")
        newNamePoint = st.text_input("name", key = "new_name_point")
        newXPoint = float( st.text_input("x-Pos.",key = "new_x_point", value= 0) )
        newYPoint = float( st.text_input("y-Pos.",key = "new_y_point", value= 0) )
        newPointFixed = st.checkbox("is Point fixed?")
        newPointOnCircularPath = st.checkbox("is Point on Circular path?")

        #if newNamePoint
        if st.form_submit_button("Save point"):
            try: 
                newNamePoint = Joint(newNamePoint, newXPoint, newYPoint, newPointFixed, newPointOnCircularPath)
                newNamePoint.save()
            except:
                st.error("Error!")
        #else: st.error("Bitte Namen eingeben")

    with st.form("add Line"):
    # ++++++ add new line ++++++
        all_points = Joint.find_all_joints()
        st.write("add new Link")
        linkName = st.text_input("link name")
        firstPointName = st.selectbox("select first Point",all_points)
        secondPointName = st.selectbox("select second Point",all_points)

        if st.form_submit_button("add link"):
            firstPoint = Joint.find_by_name(firstPointName)                                               
            secondPoint = Joint.find_by_name(secondPointName)
            try: 
                linkName = Link(linkName, firstPoint, secondPoint)
                linkName.initialize_self_lenght()
                linkName.save()
            except:
                st.error("Error!")

    # ++++++ New Mechanism ++++++
    with st.form("New Mechanism"):

        newMechanismName = st.text_input("Mechanism name")
        newMechanism = Mechanism(newMechanismName, [], [])

        if st.form_submit_button("Save mech"):
            for joint in Joint.find_joints_info():
                joint = Joint.find_by_name(joint["name"]) 
                if joint:
                    newMechanism.add_joint(joint)

            for link in Link.find_link_info():
                link = Link.find_by_name(link["name"])
                if link:
                    newMechanism.add_link(link)

            newMechanism.save()
  


# ++++++++++ Live Editor +++++++++++++++++

# ++++++ erstelle Plot ++++++
fig, ax = plt.subplots()
for points in Joint.find_joints_info():
    ax.plot(points["x"],points["y"],'o',  label= points["name"])
for link in Link.find_link_info():
    x = (link["joint_a"]["x"],link["joint_b"]["x"])
    y = (link["joint_a"]["y"],link["joint_b"]["y"])
    ax.plot(x,y)
    ax.legend()            # Fehlermeldung wenn keine Points oder links in Db. Eventuell schon behoben
st.pyplot(fig)

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
#else:
    #for links in all_links_info:
     #   df1 = pd.DataFrame(link["name"],link["joint_a"]["name"],link["joint_b"]["name"])
    #df1 = pd.DataFrame(all_links_info)
    #required_columns = ["name","Joint a", "Joint B"]
    #st.write(df1)

# ++++++++++++++++++ Animation Editor +++++++++++++++++++
st.header("360° Simulation & Animation")
st.write("Berechne die Kinematik des Mechanismus über einen Winkelbereich von 0 bis 360° und erstelle eine Animation.")

#Erzeuge den SimulationManager (Singleton)
mech = st.selectbox("select mechanism",Mechanism.find_all_mechs())
choosedMech = Mechanism.find_mech_by_name(mech)
st.write(choosedMech)

fourbar = FourBarLinkage.create_default()
sim_manager = SimulationManager(mech)
# Der Mechanismus wird vom SimulationManager verwaltet:
m1 = sim_manager.mechanism

if st.button("Run 360° Animation"):
    with st.spinner("Simuliere und erstelle Animation..."):
        # Führe die Simulation durch (Speicherung der Trajektorien)
        sim_manager.simulate_over_360(num_steps=36)
        # Erstelle die GIF-Animation
        gif_buf = sim_manager.create_animation()
        st.image(gif_buf.read(), caption="Mechanism Animation", use_container_width =True)

    st.session_state.simulation_done = True

# Zeige den Export-Button nur, wenn die Simulation bereits durchgeführt wurde
if st.session_state.get("simulation_done", False):
    if st.button("Bahnkurven als CSV speichern"):
        sim_manager.export_trajectories_to_csv("bahnkurven.csv")
        st.success("Bahnkurven wurden erfolgreich als CSV gespeichert!")
if __name__ == "__main__":

#    mech1 = Mechanism("Viergelenkkette",[c,p0,p1,p2],(l0,l1,l2))
#     # print(s1.get_current_length())
#     # print(m1.get_all_x())
#     # print(m1.get_all_y())

# # #++++++++++++++++++++++++++++++++++
#
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

    # s1= Link(p0,p1)
    # s2= Link(g2,g3)

    # m1= Mechanism([g1,g2,g3],[s1,s2])
#     #print(Joint.find_joints_info())
#     firstP = Joint.find_by_name("p0")                                               
#     secondP = Joint.find_by_name("p1")

#     s1=Link("test", firstP,secondP)
#     s1.save()
#     print(s1.get_current_length())

#     #Joint(data["name"], data["x"], data["y"], data["is_fixed"], data["on_circular_path"]

    #sim_manager = SimulationManager("Viergelenkkette")
    #print(Mechanism.find_joints_by_mechanism("Viergelenkkette"))
    #print(Mechanism.find_links_by_mechanism("Viergelenkkette"))

# Der Mechanismus wird vom SimulationManager verwaltet:
    #m1 = sim_manager.mechanism
    #print(m1)
    pass