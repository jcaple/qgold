test-quote-retrieval:
	sam remote invoke qgold-api-data-function

test-quote-analysis:
	sam remote invoke qgold-quote-analysis-function --event-file functions/quote_analysis/tests/event.json

deploy:
	sam build
	sam deploy --capabilities CAPABILITY_NAMED_IAM

deploy-quote-retrieval:
	sam build ApiDataFunction
	sam deploy --capabilities CAPABILITY_NAMED_IAM

deploy-quote-analysis:
	sam build QuoteAnalysisFunction
	sam deploy --capabilities CAPABILITY_NAMED_IAM

seed-db:
	aws dynamodb batch-write-item --request-items file://seed/dynamodb_bkup.json