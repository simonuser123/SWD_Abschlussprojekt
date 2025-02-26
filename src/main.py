import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from mechanism import Joint, Link, Mechanism, clear_workspace
from simulation_manager import SimulationManager

# --------------- Page Settings ---------------
# st.set_page_config(layout="wide")
st.set_page_config(
    page_title="Ebenenmechanismus Simulator",
    page_icon=":material/simulation:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Benutzerdefiniertes CSS für den Footer
st.markdown(
    """
    <style>
    .footer {
        text-align: center;
        padding: 10px;
        margin-top: 50px;
        border-top: 1px solid #eaeaea;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title(":material/simulation: Ebenenmechanismus Simulator")
st.markdown("---")

if "state" not in st.session_state:
    st.session_state["state"] = "Live_Editor"

# Funktionen zur Zustandsänderung (Navigation zwischen den Seiten)
def go_to_state_live_editor():
    """Setzt den Status auf 'Live_Editor'."""
    st.session_state["state"] = "Live_Editor"

def go_to_state_animation():
    """Setzt den Status auf 'Animation'."""
    st.session_state["state"] = "Animation"

if st.session_state["state"] == "Live_Editor":
    st.header(":material/edit: Live- Editor")
        
    # --------------- Arbeitsumgebung ---------------  
    with st.sidebar:
        st.title(":material/menu: Navigation")
        if st.button(":material/animated_images: Simulation & Animation"):
            go_to_state_animation()
            st.rerun()
        st.title(":material/settings: Settings")
        with st.form("Save Point"):
            # ++++++ Add New Point ++++++
            st.write(":material/nest_heat_link_e: Add New Point")
            newNamePoint = st.text_input("Name", key="new_name_point")
            newXPoint = float(st.text_input("x-Pos.", key="new_x_point", value=0))
            newYPoint = float(st.text_input("y-Pos.", key="new_y_point", value=0))
            newPointFixed = st.checkbox("Is Point fixed?")
            newPointOnCircularPath = st.checkbox("Is Point on Circular path?")
            
            if st.form_submit_button(":material/add_circle: Add point"):
                try:
                    newNamePoint = Joint(newNamePoint, newXPoint, newYPoint, newPointFixed, newPointOnCircularPath)
                    newNamePoint.save()
                    Link.update_link()
                except:
                    st.error("Error!")
                    
        with st.form("add Line"):
            # ++++++ Add New Link ++++++
            all_points = Joint.find_all_joints()
            st.write(":material/link: Add New Link")
            linkName = st.text_input("Link name")
            firstPointName = st.selectbox("Select first Point", all_points)
            secondPointName = st.selectbox("Select second Point", all_points)
            
            if st.form_submit_button(":material/add_circle: Add link"):
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
            newMechanismName = st.text_input(":material/build: Mechanism name")
            newMechanism = Mechanism(newMechanismName, [], [])
            
            if st.form_submit_button(":material/save: Save mechanism"):
                if newMechanismName == "Viergelenkkette" or newMechanismName == "Strandbeest":
                    st.error("Unable to overwrite: Viergelenkkette or Strandbeest.")
                else:
                    for joint in Joint.find_joints_info():
                        joint_obj = Joint.find_by_name(joint["name"])
                        if joint_obj:
                            newMechanism.add_joint(joint_obj)
                    for link in Link.find_link_info():
                        link_obj = Link.find_by_name(link["name"])
                        if link_obj:
                            newMechanism.add_link(link_obj)
                    is_valid, validation_msg = newMechanism.validate()
                    if is_valid:
                        newMechanism.save()
                        st.success(f"{newMechanismName} saved")
                    else:
                        st.error("Invalid mechanism")
                        st.error(validation_msg)


        # st.write(" ")
        # st.write(" ")
        st.divider()
        # st.write(" ")
        # st.write(" ")
        st.title(":material/delete: Remove Mechanism")
        with st.form("DeleteMech"):
            name = st.selectbox("Select mechanism", Mechanism.find_all_mechs())
            if st.form_submit_button(":material/delete: Delete"):
                if name == "Viergelenkkette" or name == "Strandbeest":
                    st.error("Unable to delete: Viergelenkkette or Strandbeest.")
                else:
                    Mechanism.clear_by_name(name)
                    st.success(f"{name} deleted")
                    st.rerun()


    # --------------- Live Editor ---------------
    # ++++++ Erstelle kleineren, mittigen Plot ++++++
    fig, ax = plt.subplots(figsize=(4, 3))  # Kleinere Größe setzen
    
    # Punkte zeichnen
    for points in Joint.find_joints_info():
        ax.plot(points["x"], points["y"], 'o', label=points["name"])
        ax.text(points["x"], points["y"], points["name"], fontsize=10, ha='right', va='bottom')

    
    # Verbindungen zeichnen
    for link in Link.find_link_info():
        x = (link["joint_a"]["x"], link["joint_b"]["x"])
        y = (link["joint_a"]["y"], link["joint_b"]["y"])
        ax.plot(x, y)
    
    if Joint.find_joints_info():
        ax.legend()
    
    # Drei Spalten erstellen und Plot in der mittleren Spalte anzeigen
    col1, col2, col3 = st.columns([1, 4, 1])  # Mittlere Spalte größer machen für bessere Zentrierung
    with col2:
        st.pyplot(fig)
    
    # ++++++ Tabellen für Points und Links ++++++
    tab1, tab2 = st.columns(2)
    with tab1:
        st.header(":material/nest_heat_link_e: Joints")
        all_joints_info = Joint.find_joints_info()
        if not all_joints_info:
            st.warning("Noch keine Joints gespeichert.")
        else:
            columns = ["name", "x", "y", "is_fixed", "on_circular_path"]
            df = pd.DataFrame(all_joints_info, columns=columns)
            st.write(df)
        
        if st.button(":material/delete: Clear workspace"):
            st.info(clear_workspace())
            st.rerun()
    with tab2:
        st.header(":material/link: Links")
        all_links_info = Link.find_link_info()
        if not all_links_info:
            st.warning("Noch keine Links gespeichert.")
        else:
            df1 = []
            for links in all_links_info:
                name = links["name"]
                joint_a = links["joint_a"]["name"]
                joint_b = links["joint_b"]["name"]
                length = links["length"]
                df1.append([name, joint_a, joint_b, length])
            columns = ["Name", "Joint A", "Joint B", "Length"]
            df3 = pd.DataFrame(df1, columns=columns)
            st.write(df3)

if st.session_state["state"] == "Animation":

    with st.sidebar:
        st.header(":material/menu: Navigation")
        if st.button(":material/arrow_back: Zurück zum Live-Editor wechseln"):
            go_to_state_live_editor()
            st.rerun()

    # --------------- Animation Editor ---------------
    st.header(":material/animated_images: Simulation & Animation")
    st.write("Berechne die Kinematik des Mechanismus über einen Winkelbereich von 0 bis 360° und erstelle eine Animation.")
        
    mech = st.selectbox("Select mechanism", Mechanism.find_all_mechs())
    choosedMech = Mechanism.find_mech_by_name(mech)
    
    sim_manager = SimulationManager(mech)
    m1 = sim_manager.mechanism
    
    if st.button(":material/play_circle: Run Animation"):
        with st.spinner("Simuliere und erstelle Animation..."):
            sim_manager.simulate_over_360(num_steps=36)
            print("Anzahl Frames:", len(next(iter(sim_manager.trajectories.values()))))
            gif_buf = sim_manager.create_animation()
            # Speichere die erzeugten GIF-Bytes in st.session_state
            st.session_state["animation_bytes"] = gif_buf.getvalue()
        st.session_state.simulation_done = True

    # Prüfe, ob wir schon Animationsergebnisse haben, und zeige diese an:
    if "animation_bytes" in st.session_state and st.session_state["animation_bytes"]:
        col1, col2, col3 = st.columns([1, 4, 1])  # Mittlere Spalte größer machen für bessere Zentrierung
        with col2:
            st.image(st.session_state["animation_bytes"], caption=f"{choosedMech.name} Animation", use_container_width=True)
        st.download_button(
            label=":material/download: Animation herunterladen",
            data=st.session_state["animation_bytes"],
            file_name="mechanism_animation.gif",
            mime="image/gif"
        )

    if st.session_state.get("simulation_done", False):
        csv_bytes = sim_manager.export_trajectories_to_csv()
        st.write("Debug - CSV Bytes:", csv_bytes)  # Debug-Ausgabe
        if csv_bytes:
            st.download_button(
                label=":material/download: CSV herunterladen",
                data=csv_bytes,
                file_name="bahnkurven.csv",
                mime="text/csv"
            )

    if st.session_state.get("simulation_done", False):
        if st.button(":material/cancel: Animation abbrechen"):
            st.session_state.simulation_done = False
            st.session_state["animation_bytes"] = None
            st.rerun()
