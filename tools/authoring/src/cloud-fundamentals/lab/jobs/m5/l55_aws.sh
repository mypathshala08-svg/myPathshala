#!/bin/bash
# Lesson 5.5 — budget alert + Spot price history (moto emulator; real account: drop --endpoint-url)
E="--endpoint-url ${ENDPOINT:-http://localhost:5000} --region ap-south-1"
ACCT=$(aws $E sts get-caller-identity --query Account --output text)
echo "== 1) monthly cost budget US\$50 (≈ ₹4,400), e-mail at 80% of actual spend"
aws $E budgets create-budget --account-id $ACCT \
  --budget '{"BudgetName":"tiffingo-monthly","BudgetLimit":{"Amount":"50","Unit":"USD"},"TimeUnit":"MONTHLY","BudgetType":"COST"}' \
  --notifications-with-subscribers '[{"Notification":{"NotificationType":"ACTUAL","ComparisonOperator":"GREATER_THAN","Threshold":80,"ThresholdType":"PERCENTAGE"},"Subscribers":[{"SubscriptionType":"EMAIL","Address":"owner@tiffingo.in"}]}]'
aws $E budgets describe-budgets --account-id $ACCT --query 'Budgets[].[BudgetName,BudgetLimit.Amount,BudgetLimit.Unit,TimeUnit,BudgetType]' --output text
aws $E budgets describe-notifications-for-budget --account-id $ACCT --budget-name tiffingo-monthly --query 'Notifications[].[NotificationType,ComparisonOperator,Threshold,ThresholdType]' --output text
echo "== 2) clean up"
aws $E budgets delete-budget --account-id $ACCT --budget-name tiffingo-monthly && echo "deleted: budget"
