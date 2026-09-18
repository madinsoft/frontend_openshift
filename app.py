import os
import requests
import streamlit as st
import pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service:8000")

st.set_page_config(page_title="Suivi de Temps", layout="wide")
st.title("⏱️ Gestion et Suivi de Temps")

tab_users, tab_projects, tab_tasks, tab_logs = st.tabs(["Utilisateurs", "Projets", "Tâches", "Saisie & Suivi"])

with tab_users:
    st.header("Gestion des utilisateurs")
    with st.form("form_user"):
        username = st.text_input("Nom d'utilisateur")
        email = st.text_input("Email")
        submit_user = st.form_submit_button("Ajouter utilisateur")
        if submit_user and username and email:
            res = requests.post(f"{BACKEND_URL}/users", json={"username": username, "email": email})
            if res.status_code == 201:
                st.success(f"Utilisateur {username} créé !")
            else:
                st.error(res.text)

    users_res = requests.get(f"{BACKEND_URL}/users")
    if users_res.status_code == 200 and users_res.json():
        st.dataframe(pd.DataFrame(users_res.json()))

with tab_projects:
    st.header("Gestion des projets")
    with st.form("form_project"):
        proj_name = st.text_input("Nom du projet")
        proj_desc = st.text_area("Description")
        submit_proj = st.form_submit_button("Ajouter projet")
        if submit_proj and proj_name:
            res = requests.post(f"{BACKEND_URL}/projects", json={"name": proj_name, "description": proj_desc})
            if res.status_code == 201:
                st.success(f"Projet {proj_name} créé !")
            else:
                st.error(res.text)

    projects_res = requests.get(f"{BACKEND_URL}/projects")
    if projects_res.status_code == 200 and projects_res.json():
        st.dataframe(pd.DataFrame(projects_res.json()))

with tab_tasks:
    st.header("Gestion des tâches")
    projects_list = requests.get(f"{BACKEND_URL}/projects").json() if requests.get(f"{BACKEND_URL}/projects").status_code == 200 else []
    proj_map = {p["name"]: p["id"] for p in projects_list}

    if proj_map:
        with st.form("form_task"):
            task_title = st.text_input("Titre de la tâche")
            selected_proj = st.selectbox("Projet associé", options=list(proj_map.keys()))
            submit_task = st.form_submit_button("Ajouter tâche")
            if submit_task and task_title:
                res = requests.post(f"{BACKEND_URL}/tasks", json={"title": task_title, "project_id": proj_map[selected_proj]})
                if res.status_code == 201:
                    st.success(f"Tâche {task_title} créée !")
                else:
                    st.error(res.text)

    tasks_res = requests.get(f"{BACKEND_URL}/tasks")
    if tasks_res.status_code == 200 and tasks_res.json():
        st.dataframe(pd.DataFrame(tasks_res.json()))

with tab_logs:
    st.header("Saisie des temps")
    users_list = requests.get(f"{BACKEND_URL}/users").json() if requests.get(f"{BACKEND_URL}/users").status_code == 200 else []
    tasks_list = requests.get(f"{BACKEND_URL}/tasks").json() if requests.get(f"{BACKEND_URL}/tasks").status_code == 200 else []

    user_map = {u["username"]: u["id"] for u in users_list}
    task_map = {t["title"]: t["id"] for t in tasks_list}

    if user_map and task_map:
        with st.form("form_timelog"):
            selected_user = st.selectbox("Utilisateur", options=list(user_map.keys()))
            selected_task = st.selectbox("Tâche", options=list(task_map.keys()))
            duration = st.number_input("Durée (minutes)", min_value=1, value=60)
            submit_log = st.form_submit_button("Enregistrer le temps")
            if submit_log:
                res = requests.post(f"{BACKEND_URL}/timelogs", json={
                    "user_id": user_map[selected_user],
                    "task_id": task_map[selected_task],
                    "duration_minutes": duration
                })
                if res.status_code == 201:
                    st.success("Temps enregistré !")
                else:
                    st.error(res.text)

    st.subheader("Historique des temps passés")
    logs_res = requests.get(f"{BACKEND_URL}/timelogs")
    if logs_res.status_code == 200 and logs_res.json():
        st.dataframe(pd.DataFrame(logs_res.json()))
