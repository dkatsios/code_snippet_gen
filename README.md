# CODE SNIPPET GENERATOR

## Docker
- Run `docker pull dkatsios/code_gen` to pull the docker image.
- Run `docker run --rm dkatsios/code_gen sh -c 'echo "OPENAI_API_KEY=<your-OpenAI-API-key>" > .env && pytest test.py'` to execute all the tests.
- Run `docker run -p 8000:8000 dkatsios/code_gen` to start the server. Change the host port if needed.

