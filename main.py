from fastapi import FastAPI, Response

app = FastAPI()


@app.get("/livez")
def livez():
    return Response(content="OK", media_type="text/plain")
