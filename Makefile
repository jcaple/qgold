test-quote-retrieval:
	aws lambda invoke --function-name qgold-server-ApiDataFunction-SadYYO6PIS9Y --payload '{}' response.json
