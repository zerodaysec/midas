

run:
	op run --env-file=.env pipenv run streamlit run app.py

get-data:
	pipenv run python grab_data.py