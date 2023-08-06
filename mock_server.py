from fastapi import APIRouter, FastAPI, Depends, HTTPException, Header, Query, Body, status, Response, Form, Request
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import csv


app = FastAPI()

@app.get("/data/craft_table")
async def get_craft_table():
    with open("data/resource_table.csv", "r") as file:
        table_reader = csv.reader(file, delimiter=',', quotechar='"')
        headers = next(table_reader)
        data = []
        for row in table_reader:
            datum = {
                "craft_machine": row[5],
                "craft_time": float(row[4]),
                "craft_from": row[5],
                "products": [
                    {
                        "id": row[0],
                        "num_per_tick": float(row[1])
                    }
                ],
                "requires": []
            }
            if(row[2] != ''):
                datum["products"].append({
                    "id": row[2],
                    "num_per_tick": float(row[3])
                })
            component_index = 6
            while(component_index < len(row)):
                if row[component_index] != '':
                    datum["requires"].append({
                        "id": row[component_index],
                        "num_per_tick": float(row[component_index + 1])
                    })
                component_index += 2
            data.append(datum)
    return data
    

@ app.on_event("startup")
async def startup_event():
    print("Test is starting up.")


@ app.on_event("shutdown")
def shutdown_event():
    print("Test is exiting.", "Wait a moment until completely exits.")

app.mount("/", StaticFiles(directory="web"))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("mock_server:app", host="127.0.0.1",
                port=8000, log_level="info")
