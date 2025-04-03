# import pandas as pd
# import os
# from settings import BASE_DIR


# def display_surgical_device_result(result):
#     csv_path = os.path.join(BASE_DIR, "data", "surgical_file.csv")
#     try:
#         df = pd.read_csv(csv_path, encoding='utf-8', encoding_errors='ignore')
#         st.dataframe(df)
#         highlight_last_row(df)
#     except Exception as e:
#         st.error(f"Error reading the CSV file: {str(e)}")
#         st.write("Raw result data:")
#         st.write(result)


# def display_diagnostic_result(result, diagnostic_type):
#     csv_filename = get_csv_filename(diagnostic_type)
#     csv_path = os.path.join(BASE_DIR, "data", csv_filename)

#     try:
#         df = pd.read_csv(csv_path, encoding='utf-8', encoding_errors='ignore',
#                          on_bad_lines='skip', quotechar='"', engine='python')
#         st.dataframe(df)
#         highlight_last_row(df)
#     except Exception as e:
#         error(f"Error reading the CSV file: {str(e)}")
#         st.write("Raw result data:")
#         st.write(result)


# def highlight_last_row(df):
#     last_row_index = df.index[-1]
#     st.markdown(f'<style> .row-highlight-{last_row_index} {{ background-color: yellow; }} </style>',
#                 unsafe_allow_html=True)
#     st.markdown(f'<style> .row-highlight-{last_row_index} td {{ color: black; }} </style>', unsafe_allow_html=True)
#     st.markdown(f'<style> .row-highlight-{last_row_index} th {{ color: black; }} </style>', unsafe_allow_html=True)


# def get_csv_filename(diagnostic_type):
#     if diagnostic_type == 'Influenza':
#         return "flu.csv"
#     elif diagnostic_type == 'SARS-CoV-2':
#         return "sars.csv"
#     else:
#         return "diagnostic.csv"