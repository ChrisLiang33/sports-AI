uvicorn app:app --reload
npm run dev

to do:
get_final_score(): done
get_pregame_odds(): done
make_predictions(): done

form training_data: it should work tomorrow cuz there is 11/6 pregame and 11/6 finalscore by then
turn it into csv, add relational db later

for fastapi, turn it into cloud once yesterdays prediction is up in the cloud

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
