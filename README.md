#This is Techdome loan app created by Mayank Nagariya.

Tech stack used-
1. Backend- Flask (choosen flask because it's very lightweight and gives us flexibility to choose other things)
2. Frontend- Jinja Templating (As it has to be simple html pages, chooses jinja templating)
3. DB- sqlite (we needed lightweighted database, so choosen inbuilt sqlite, there is no need to use external DBs)


# run below command to install dependecies-

pip install -r requirements.txt 

# for jwt secret key-
create .env file in LOAN APP folder. 
JWT_SECRET_KEY = <keep any secret string key>
e.g- JWT_SECRET_KEY = "ldfldlfllfs;s$3l4#"

# for db setup use below commands -

flask db init 
flask db migrate -m "initail database setup"
flask db upgrade 

# run flask app using either of the below commands -
python app.py
flask run 
or use vs code debug mode to run app. 

# Now open browser and run 127.0.0.1:5000/login 
-This will land to login page where you can create your account as a customer or admin.
-Admin will login and land in the approval page. 
-Customer will login and land into the loan view page.
-Customer will get option to create loan. Once admin approve the loan, he will be able to do repayments. 

# test cases-
it's inside test folder run below commands to run test cases-
pytest 

