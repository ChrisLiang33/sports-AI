uvicorn app:app --reload
npm run dev

to do:
update the csv to db

turn it into csv, add relational db later
deploy it

step1:
get today pregame odds and yesterday final score write into db

step2:
form training data with rating on them from yesterdays pregame odds and yesterdays final score, then put rating into csv

step3:
make predictions, write to db

step4:
write prediction to cvs

step5:
calculate result, update the prediction field with win or lost
