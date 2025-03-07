import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from mechanism import Joint, Link, Mechanism, clear_workspace
from simulation_manager import SimulationManager

# --------------- Page Settings ---------------
# st.set_page_config(layout="wide")
st.set_page_config(
    page_title="Simulator for planar mechanisms",
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

st.header(":material/simulation: Simulator for planar mechanisms", 
          divider=True,
          help="This app allows you to create, simulate and analyze planar mechanisms.")

if "state" not in st.session_state:
    st.session_state["state"] = "Live_Editor"

# Funktionen zur Zustandsänderung (Navigation zwischen den Seiten)
def go_to_state_live_editor():
    """Setzt den Status auf 'Live_Editor'."""
    st.session_state["state"] = "Live_Editor"

def go_to_state_animation():
    """Setzt den Status auf 'Animation'."""
    st.session_state["state"] = "Animation"

def go_to_state_parts_list():
    """Setzt den Status auf 'Parts_List'."""
    st.session_state["state"] = "Parts_List"

if st.session_state["state"] == "Live_Editor":
        
    # --------------- Arbeitsumgebung ---------------  
    with st.sidebar:
        st.title(":material/menu: Navigation")
        if st.button(":material/animated_images: Simulation & Animation"):
            go_to_state_animation()
            st.rerun()
        if st.button(":material/list: Create Bill of Materials"):
            go_to_state_parts_list()
            st.rerun()

        st.header(":material/settings: Configurate Mechanism", 
                  help="Here you can create and save points and links for your mechanism.",
                  divider="gray")
        
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
    
    con1 = st.container(border=True)
    with con1:
        st.header(":material/visibility: Live preview")
        col1, col2, col3 = st.columns([1, 4, 1])  # Mittlere Spalte größer machen für bessere Zentrierung
        with col2:
            st.pyplot(fig)
    
    # ++++++ Tabellen für Points und Links ++++++
    tab1, tab2 = st.columns(2, border=True)
    with tab1:
        st.header(":material/nest_heat_link_e: Joints")
        all_joints_info = Joint.find_joints_info()
        if not all_joints_info:
            st.warning("No joints saved yet.")
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
            st.warning("No links saved yet.")
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
        if st.button(":material/list: Create Bill of Materials"):
            go_to_state_parts_list()
            st.rerun()

        if st.button(":material/edit: Live-Editor"):
            go_to_state_live_editor()
            st.rerun()
    con1 = st.container(border=True)
    with con1:
        # --------------- Animation Editor ---------------
        st.header(":material/animated_images: Simulation & Animation")        
        mech = st.selectbox("Select mechanism", Mechanism.find_all_mechs())
        choosedMech = Mechanism.find_mech_by_name(mech)

        if ("sim_manager" not in st.session_state or 
            st.session_state.sim_manager.mechanism.name != choosedMech.name):
            st.session_state.sim_manager = SimulationManager(mech)
        sim_manager = st.session_state.sim_manager
        m1 = sim_manager.mechanism

        st.info("Calculate the kinematics of the mechanism over a full rotation of the driven shaft and create an animation.")
        st.info("Note: A higher number of calculated steps provides a more precise result, but it also increases the computation time.")
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            num_steps = st.slider("Number of steps", 36, 360, 72, step=9)

        if st.button(":material/play_circle: Run Animation"):
            st.session_state.simulation_done = False
            with st.spinner("Simulate and create an animation..."):
                st.session_state.simulation_done = False
                sim_manager.simulate_over_360(num_steps=num_steps)
                gif_buf = sim_manager.create_animation()
                # Speichere die erzeugten GIF-Bytes in st.session_state
                st.session_state["animation_bytes"] = gif_buf.getvalue()
                st.session_state["csv_bytes"] = sim_manager.export_trajectories_to_csv()
            st.session_state.simulation_done = True

        # Prüfe, ob wir schon Animationsergebnisse haben, und zeige diese an:
        if "animation_bytes" in st.session_state and st.session_state["animation_bytes"]:
            col1, col2, col3 = st.columns([1, 4, 1])  # Mittlere Spalte größer machen für bessere Zentrierung
            with col2:
                st.image(st.session_state["animation_bytes"], caption=f"{choosedMech.name} Animation", use_container_width=True)
            st.download_button(
                label=":material/download: Download animation",
                data=st.session_state["animation_bytes"],
                file_name=f"{choosedMech.name}_animation.gif",
                mime="image/gif"
            )

        if "csv_bytes" in st.session_state and st.session_state.csv_bytes:
            #st.write("Debug - CSV Bytes:", csv_bytes)  # Debug-Ausgabe
                st.download_button(
                    label=":material/download: Download CSV",
                    data=st.session_state["csv_bytes"],
                    file_name=f"{choosedMech.name}_trajectories.csv",
                    mime="text/csv"
                )

        if st.session_state.get("simulation_done", False):
            if st.button(":material/download: Export to OpenSCAD"):
                sim_manager.export_configuration_to_scad(filename=f"{choosedMech.name}.scad")
                st.success(f"OpenSCAD-Datei {choosedMech.name}.scad generiert!")

        if st.session_state.get("simulation_done", False):
            if st.button(":material/cancel: Reset animation"):
                st.session_state.simulation_done = False
                st.session_state["animation_bytes"] = None
                st.session_state["csv_bytes"] = None
                st.rerun()


        if st.session_state.get("simulation_done", False):
            st.divider()

            # Neue Geschwindigkeitsberechnungssektion
            st.header(":material/speed: Speed analysis")

            col1, col2 = st.columns(2)
            with col1:
                crank_rpm = st.slider("Crank speed (RPM)", 1, 120, 60)
                selected_point = st.selectbox("Point of analysis", [j.name for j in choosedMech.joints])

            if st.button(":material/calculate: Calculate velocity"):
                velocity, step_length, steps = sim_manager.calculate_forward_velocity(crank_rpm, selected_point)

                col1, col2 = st.columns([1, 2])  # Mittlere Spalte größer machen für bessere Zentrierung
                with col1:
                    st.markdown("<div style='margin-top:100px;'></div>", unsafe_allow_html=True)
                    st.metric(label="Maximum Forward Speed", 
                             value=f"{velocity:.2f} m/s",
                             help="Calculated forward velocity in x-direction")

                    st.metric(label="Step Length", 
                             value=f"{step_length:.2f} m",
                             help="Horizontal distance between steps")

                    st.metric(label="Crank Speed", 
                             value=f"{crank_rpm} RPM",
                             help="Input rotation speed")

                    st.metric(label="Step Length", 
                             value=f"{step_length:.2f} m",
                             help="Horizontal distance between steps")
                    st.markdown("</div>", unsafe_allow_html=True)

                with col2:
                    # Visualisierung
                    fig, ax = plt.subplots()
                    ax.plot(
                        [pos[0] for pos in sim_manager.trajectories[selected_point]],
                        [pos[1] for pos in sim_manager.trajectories[selected_point]],
                        marker='o', linestyle='-', color='blue'
                    )
                    ax.set_title(f"trajectory of {selected_point}")
                    ax.set_xlabel("X-position [m]")
                    ax.set_ylabel("Y-position [m]")
                    ax.grid(True)
                    st.pyplot(fig)


if st.session_state["state"] == "Parts_List":

    with st.sidebar:
        st.header(":material/menu: Navigation")
        if st.button(":material/animated_images: Simulation & Animation"):
            go_to_state_animation()
            st.rerun()

        if st.button(":material/edit: Live Editor"):
            go_to_state_live_editor()
            st.rerun()
    con1 = st.container(border=True)
    with con1:
        st.header(":material/list: Create Bill of Materials", 
                  help="Generate a bill of materials (BOM) for the selected mechanism.")
        st.info("Create a bill of materials (BOM) for the mechanism.")
        with st.form("BOM"):
            selected_mech = st.selectbox("Select Mechanism", Mechanism.find_all_mechs())

            if st.form_submit_button(":material/description: Generate BOM"):
                mechanism = Mechanism.find_mech_by_name(selected_mech)

                # Identify drive components first
                drive_joints = [j for j in mechanism.joints if j.on_circular_path]
                drive_links = []
                for link in mechanism.links:
                    if link.joint_a in drive_joints or link.joint_b in drive_joints:
                        drive_links.append(link)

                bom = []

                fixed_joints = [j for j in mechanism.joints if j.is_fixed and j not in drive_joints]
                free_joints = [j for j in mechanism.joints if not j.is_fixed and j not in drive_joints]
                bom.append({
                    "Category": "Joints",
                    "Name": "Fixed Joints",
                    "Quantity": len(fixed_joints),
                    "comment": ", ".join([j.name for j in fixed_joints]) or "-"
                })
                bom.append({
                    "Category": "Joints",
                    "Name": "Free Joints",
                    "Quantity": len(free_joints),
                    "comment": ", ".join([j.name for j in free_joints]) or "-"
                })

                standard_links = [l for l in mechanism.links if l not in drive_links]
                # Group links by length (rounded to 2 decimals)
                length_groups = {}
                for link in standard_links:
                    rounded_length = round(link.length, 2)
                    if rounded_length not in length_groups:
                        length_groups[rounded_length] = []
                    length_groups[rounded_length].append(link.name)
                for length, names in length_groups.items():
                    bom.append({
                        "Category": "Links",
                        "Name": f"Link {length:.2f}m",
                        "Quantity": len(names),
                        "comment": ", ".join(names)
                    })
                for drive in drive_joints:
                    # Find connected fixed joint and link
                    drive_link = next((l for l in mechanism.links 
                                      if (l.joint_a == drive or l.joint_b == drive) 
                                      and (l.joint_a.is_fixed or l.joint_b.is_fixed)), None)
                    bom.append({
                        "Category": "Drive System",
                        "Name": "Drive Unit",
                        "Quantity": 1,
                        "comment": f"Drive joint: {drive.name}, Lever arm: {drive_link.length:.2f}m" if drive_link else drive.name
                    })

                st.session_state.bom = bom
                st.session_state.show_bom = True

        if st.session_state.get("show_bom", False):
            st.header(":material/list: Bill of Materials (DIN 6771)")

            df_bom = pd.DataFrame(st.session_state.bom)

            df_bom = df_bom.set_index(['Name', 'Quantity'])
            # Style dataframe
            styled_df = df_bom.style.set_properties(**{
                'background-color': '#f8f9fa',
                'border': '1px solid #dee2e6',
                'padding': '8px'
            })
            st.dataframe(styled_df, use_container_width=True)

            # CSV Download
            csv = df_bom.to_csv(sep=';').encode("utf-8")
            st.download_button(
                label=":material/download: Download BOM (CSV)",
                data=csv,
                file_name=f"bom_{selected_mech}.csv",
                mime="text/csv",
                help="Download in DIN 6771 compatible format using semicolon delimiter"
            )
