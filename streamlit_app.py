import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account

# db = firestore.Client.from_service_account_json("names-firebase.json")
import json
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="names-project-demo")

db_names = db.collection('names')

def load_by_name(name):
  names_ref = db_names.where('name', '==', name)
  current_name = None
  for my_name in names_ref.stream():
    current_name = my_name
  return current_name

st.header("Streamlit - Nuevo registro de nombre")

st.sidebar.subheader('Buscar nombre')
name_search = st.sidebar.text_input('Inserte nombre')
filtrar_nombre_btn = st.sidebar.button('Buscar')

if filtrar_nombre_btn:
  doc = load_by_name(name_search)
  if doc is None:
    st.sidebar.write('El nombre no se encontro')
  else:
    st.sidebar.write(doc.to_dict())

st.sidebar.markdown("""---""")
btn_eliminar = st.sidebar.button('Eliminar')

if btn_eliminar:
  delete_name = load_by_name(name_search)
  if delete_name is None:
    st.sidebar.write('El nombre no existe')
  else:
    db_names.document(delete_name.id).delete()
    st.sidebar.write('Nombre eliminado')

st.sidebar.markdown("""---""")
new_name = st.sidebar.text_input('Ingrese nombre actualizado')
update_button = st.sidebar.button('Actualizar')

if update_button:
  update_name = load_by_name(name_search)
  if update_name is None:
    st.sidebar.write('Nombre no existe')
  else:
    update_new_name = db_names.document(update_name.id)
    update_new_name.update(
        {
            "name": new_name
        }
    )

index = st.text_input("Index")
name = st.text_input("Name")
sex = st.selectbox(
    "Select sex", ('F','M','Other')
)

submit = st.button('Crear nuevo registro')

# Once the name is submitted, upload it to the database
if index and name and sex and submit:
  doc_ref = db_names.document(name)
  doc_ref.set({
      "index":index,
      "name":name,
      "sex":sex
  })
  st.write("Registro insertado correctamente")

  names_ref = list(db_names.stream())
  names_dict = list(map(lambda x: x.to_dict(), names_ref))
  names_df = pd.DataFrame(names_dict)
  st.dataframe(names_df)
